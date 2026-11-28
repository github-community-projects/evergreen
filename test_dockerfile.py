"""Validate the container's restricted, auditable package-install contract."""

import re
import shlex
from pathlib import Path

import pytest


def _build_commands(text: str) -> list[list[str]]:
    assert all(
        char in "\t\r\n" or 32 <= ord(char) <= 126 for char in text
    ), "Unsupported Dockerfile characters"
    physical_lines = []
    for line in text.split("\n"):
        line = line.removesuffix("\r")
        assert "\r" not in line, "Unsupported embedded carriage return"
        assert not re.match(
            r"^\s*#\s*(escape|syntax|check)\s*=", line, re.IGNORECASE
        ), "Unmodeled parser directive"
        if line.strip() and not line.lstrip().startswith("#"):
            physical_lines.append(line)
    logical_lines = "\n".join(physical_lines).replace("\\\n", " ").split("\n")
    runs = []
    supported = {
        "FROM",
        "LABEL",
        "WORKDIR",
        "COPY",
        "RUN",
        "HEALTHCHECK",
        "ENV",
        "CMD",
        "ENTRYPOINT",
    }
    for line in logical_lines:
        instruction = re.fullmatch(r"\s*([A-Za-z]+)(?:\s+(.*))?", line)
        assert (
            instruction and instruction[1].upper() in supported
        ), "Unsupported Dockerfile instruction"
        if instruction[1].upper() == "RUN":
            runs.append(instruction[2] or "")
    assert len(runs) == 1, "Keep package installation and cleanup in one RUN layer"
    assert not runs[0].lstrip().startswith(("[", "<<")), "Use explicit shell-form RUN"
    lexer = shlex.shlex(runs[0], posix=True, punctuation_chars=";&|()")
    lexer.whitespace_split = True
    lexer.commenters = ""
    commands: list[list[str]] = [[]]
    for token in lexer:
        if token == "&&":
            assert commands[-1], "Empty shell command"
            commands.append([])
        else:
            assert not any(
                char in token for char in "$`;&|()#"
            ), "Unsupported shell expansion or operator"
            commands[-1].append(token)
    assert commands[-1], "Empty shell command"
    assert all(
        command[0] in {"apt-get", "uv", "rm"} for command in commands
    ), "Unsupported build command"
    return commands


def _apt_operation(command: list[str]) -> tuple[str, list[str]]:
    assert command[0] == "apt-get"
    flags = {"-y", "--yes", "--no-install-recommends", "--auto-remove"}
    arguments = []
    for token in command[1:]:
        if token.startswith("-"):
            assert token in flags, f"Unsupported apt option: {token}"
        else:
            arguments.append(token)
    assert arguments and arguments[0] in {
        "update",
        "install",
        "purge",
    }, "Unsupported apt operation"
    return arguments[0], arguments[1:]


def _install_pins(text: str) -> dict[str, str]:
    pins = {}
    for command in _build_commands(text):
        if command[0] != "apt-get":
            continue
        operation, packages = _apt_operation(command)
        if operation != "install":
            continue
        assert packages, "An install command must list packages"
        for package in packages:
            match = re.fullmatch(
                r"(?P<name>[a-z0-9][a-z0-9+.-]+(?::[a-z0-9][a-z0-9-]*)?)="
                r"(?P<version>(?:[0-9]+:)?[0-9][A-Za-z0-9.+~-]*)",
                package,
            )
            assert match, f"APT install requires an exact literal version: {package}"
            assert match["name"] not in pins, "Duplicate package version selection"
            pins[match["name"]] = match["version"]
    assert pins, "Dockerfile must explicitly install pinned packages"
    return pins


def test_dockerfile_pins_every_direct_install_package():
    """All required direct packages must use literal versions, not moving selectors."""
    text = Path(__file__).with_name("Dockerfile").read_text(encoding="utf-8")
    assert set(_install_pins(text)) == {"gcc", "git", "libc6-dev", "libffi-dev"}


def test_dockerfile_preserves_frozen_dependencies_and_runtime_git():
    """Build tools must survive sync, then leave the same layer without removing Git."""
    text = Path(__file__).with_name("Dockerfile").read_text(encoding="utf-8")
    commands = _build_commands(text)
    assert [command[0] for command in commands] == [
        "apt-get",
        "apt-get",
        "uv",
        "apt-get",
        "rm",
    ]
    assert _apt_operation(commands[0]) == ("update", [])
    assert _apt_operation(commands[1])[0] == "install"
    assert commands[2] == ["uv", "sync", "--frozen", "--no-dev", "--no-editable"]
    operation, removed = _apt_operation(commands[3])
    assert operation == "purge"
    assert set(removed) == {"gcc", "libc6-dev", "libffi-dev"}
    assert "--auto-remove" in commands[3]
    assert commands[4] == ["rm", "-rf", "/var/lib/apt/lists/*"]


def test_exact_pin_policy_accepts_debian_versions_and_shell_quoting():
    """Epochs and architecture qualifiers must survive argument normalization."""
    assert _install_pins(
        "RUN\tapt-get -y install 'gcc=4:14.2.0-1' git:amd64=1:2.0~rc1-2+deb13u5"
    ) == {
        "gcc": "4:14.2.0-1",
        "git:amd64": "1:2.0~rc1-2+deb13u5",
    }


def test_comment_lines_inside_continuations_preserve_both_install_commands():
    """Docker removes full comment lines before passing continued RUN text to the shell."""
    text = "RUN apt-get install gcc=1 \\\n# note\n&& apt-get install git=1"
    assert _install_pins(text) == {"gcc": "1", "git": "1"}


@pytest.mark.parametrize(
    ("packages", "reason"),
    [
        ("gcc", "exact literal version"),
        ("gcc=", "exact literal version"),
        ("gcc=4*", "exact literal version"),
        ("gcc=[14]", "exact literal version"),
        ("gcc>=4", "exact literal version"),
        ("git/trixie-backports", "exact literal version"),
        ("~ngcc", "exact literal version"),
        ("gcc=1 git=1 libc6-dev libffi-dev=1", "exact literal version"),
        ("gcc=1 gcc=2", "Duplicate package"),
        ("-o Dpkg::Options::=--force-confold", "Unsupported apt option"),
        ("", "install command must list"),
    ],
)
def test_exact_pin_policy_rejects_nonliteral_package_selection(packages, reason):
    """A single moving selector must fail for its own policy violation."""
    with pytest.raises(AssertionError, match=reason):
        _install_pins(f"RUN apt-get -y install {packages}")


@pytest.mark.parametrize(
    ("text", "reason"),
    [
        ('RUN ["apt-get", "install", "gcc=1"]', "explicit shell-form"),
        ("RUN ${APT_CMD:-apt-get} install gcc=1", "Unsupported shell"),
        ("RUN apt-get install gcc=1#x && apt-get install git=1", "Unsupported shell"),
        ("# escape=`\nRUN apt-get install gcc=1", "Unmodeled parser directive"),
        (
            "RUN apt-get install gcc=1\u2028&& apt-get install git=1",
            "Unsupported Dockerfile characters",
        ),
        ("RUN apt-get install gcc=1\ngarbage", "Unsupported Dockerfile instruction"),
        ("RUN apt-get install gcc=1 && apt-get upgrade", "Unsupported apt operation"),
        (
            "RUN apt-get install gcc=1 && apt-get satisfy git=1",
            "Unsupported apt operation",
        ),
        ("RUN apt-get install gcc=$VERSION", "Unsupported shell"),
        ("RUN apt-get install gcc=1; apt-get install git=1", "Unsupported shell"),
        ("RUN apt-get install gcc=1 || true", "Unsupported shell"),
        ("RUN <<EOF\napt-get install gcc=1\nEOF", "Unsupported Dockerfile instruction"),
        ("RUN true\nRUN apt-get install gcc=1", "one RUN layer"),
    ],
)
def test_build_contract_rejects_unmodeled_install_routes(text, reason):
    """Unknown shell or apt forms require an explicit policy update, not silent acceptance."""
    with pytest.raises(AssertionError, match=reason):
        _install_pins(text)
