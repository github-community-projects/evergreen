"""Check literal package declarations; Docker CI tests the resulting image."""

import re
import shlex
from itertools import groupby
from pathlib import Path

import pytest


def _literal_commands(text: str) -> list[list[str]]:
    text = re.sub(r"(?m)^[ \t]*#.*\n?", "", text).replace("\\\n", " ")
    commands = []
    for run in re.findall(r"(?im)^[ \t]*RUN[ \t]+(.+)$", text):
        assert not run.lstrip().startswith(
            ("[", "<<")
        ), "Expected literal shell-form RUN"
        lexer = shlex.shlex(run, posix=True, punctuation_chars=";&|")
        lexer.whitespace_split = True
        for separator, words in groupby(
            lexer, lambda token: token in {"&&", ";", "||", "|", "&"}
        ):
            if not separator:
                command = list(words)
                while command and re.fullmatch(
                    r"[A-Za-z_][A-Za-z0-9_]*=.*", command[0]
                ):
                    command.pop(0)
                if command:
                    commands.append(command)
    return commands


def _install_pins(text: str) -> dict[str, str]:
    pins = {}
    for command in _literal_commands(text):
        if command[0] != "apt-get" or "install" not in command[1:]:
            continue
        packages = command[command.index("install") + 1 :]
        assert packages, "An install command must list packages"
        for package in packages:
            if package in {"-y", "--yes", "--no-install-recommends"}:
                continue
            match = re.fullmatch(
                r"(?P<name>[a-z0-9][a-z0-9+.-]*(?::[a-z0-9][a-z0-9-]*)?)="
                r"(?P<version>(?:[0-9]+:)?[0-9][A-Za-z0-9.+~-]*)",
                package,
            )
            assert match, f"APT install requires an exact literal version: {package}"
            pins[match["name"]] = match["version"]
    assert pins, "Dockerfile must explicitly install pinned packages"
    return pins


def _check_sync_flags(text: str) -> None:
    syncs = [
        command for command in _literal_commands(text) if command[:2] == ["uv", "sync"]
    ]
    assert syncs, "Dockerfile must sync locked Python dependencies"
    for command in syncs:
        assert {"--frozen", "--no-dev", "--no-editable"} <= set(
            command[2:]
        ), "Preserve production sync flags"


def test_dockerfile_pins_every_direct_install_package():
    """Version refreshes must not turn a direct dependency into a moving target."""
    text = Path(__file__).with_name("Dockerfile").read_text(encoding="utf-8")
    assert set(_install_pins(text)) == {"gcc", "git", "libc6-dev", "libffi-dev"}


def test_dockerfile_preserves_frozen_production_dependencies():
    """Image tests cannot prove which flags produced the installed environment."""
    _check_sync_flags(
        Path(__file__).with_name("Dockerfile").read_text(encoding="utf-8")
    )


def test_pin_policy_accepts_version_updates_and_separate_layers():
    """Valid version or layout updates must not require changing the policy."""
    text = """RUN DEBIAN_FRONTEND=noninteractive apt-get install 'gcc=9:99.1-2+deb20u1' --yes
RUN true
RUN apt-get -y install git:amd64=1:99.0~rc1-2 \\
# Docker permits comments inside continuations.
&& apt-get install libc6-dev=99.0-1 libffi-dev=99.0-2
"""
    assert _install_pins(text) == {
        "gcc": "9:99.1-2+deb20u1",
        "git:amd64": "1:99.0~rc1-2",
        "libc6-dev": "99.0-1",
        "libffi-dev": "99.0-2",
    }


@pytest.mark.parametrize(
    "package",
    [
        "gcc",
        "gcc=",
        "gcc=4*",
        "gcc=4?",
        "gcc=[14]",
        'gcc="$VERSION"',
        "git/trixie",
        "git=latest",
    ],
)
def test_pin_policy_rejects_moving_versions(package):
    """A selector must identify one literal Debian version."""
    with pytest.raises(AssertionError, match="exact literal version"):
        _install_pins(f"RUN apt-get install {package}")


def test_sync_policy_allows_reordered_flags_and_extra_commands():
    """Equivalent command layouts must not cause maintenance work."""
    _check_sync_flags(
        "RUN true && uv sync --no-editable --no-dev --frozen && echo done"
    )


@pytest.mark.parametrize("missing", ["--frozen", "--no-dev", "--no-editable"])
def test_sync_policy_rejects_missing_production_flags(missing):
    """Each flag protects a distinct part of the production dependency policy."""
    flags = [
        flag for flag in ["--frozen", "--no-dev", "--no-editable"] if flag != missing
    ]
    with pytest.raises(AssertionError, match="production sync flags"):
        _check_sync_flags("RUN uv sync " + " ".join(flags))
