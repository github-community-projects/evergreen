"""Tests for Dockerfile package-install guardrails."""

import re
from pathlib import Path


def _dockerfile_text() -> str:
    return Path(__file__).with_name("Dockerfile").read_text(encoding="utf-8")


def _normalized_dockerfile() -> str:
    return _dockerfile_text().replace("\\\n", " ")


def _canonical_package_name(token: str) -> str:
    return token.strip("'\"").split("=", maxsplit=1)[0].split(":", maxsplit=1)[0]


def _extract_run_commands() -> list[str]:
    return [
        line.strip()[4:].strip()
        for line in _normalized_dockerfile().splitlines()
        if line.lstrip().upper().startswith("RUN ")
    ]


def _strip_run_prefix_tokens(command: str) -> list[str]:
    tokens = command.split()
    while tokens and tokens[0].startswith("--"):
        tokens = tokens[1:]
    while tokens and re.match(r"^[A-Za-z_][A-Za-z0-9_]*=", tokens[0]):
        tokens = tokens[1:]
    return tokens


def _extract_apt_package_tokens(operation: str) -> list[str]:
    package_tokens: list[str] = []
    for run_command in _extract_run_commands():
        for segment in re.split(r"\s*(?:&&|;)\s*", run_command):
            tokens = _strip_run_prefix_tokens(segment)
            if not tokens or tokens[0] not in {"apt", "apt-get"}:
                continue
            if operation not in tokens[1:]:
                continue
            operation_index = tokens.index(operation)
            package_tokens.extend(
                token
                for token in tokens[operation_index + 1 :]
                if not token.startswith("-")
            )
    return package_tokens


def _iter_run_segments() -> list[str]:
    segments: list[str] = []
    for run_command in _extract_run_commands():
        segments.extend(
            segment.strip()
            for segment in re.split(r"\s*(?:&&|;)\s*", run_command)
            if segment.strip()
        )
    return segments


def _segment_has_apt_command(segment: str) -> bool:
    return bool(
        re.search(
            r"\bapt(?:-get)?\b\s+(?:-[\w-]+\s+)*(?:update|install|purge|remove|autoremove)\b",
            segment,
            re.IGNORECASE,
        )
    )


def _canonical_shell_text(text: str) -> str:
    """Normalize common shell obfuscation forms for static guardrail matching."""
    text = re.sub(
        r"\\x([0-9A-Fa-f]{2})", lambda match: chr(int(match.group(1), 16)), text
    )
    text = text.replace("\\", "")
    text = re.sub(r"[\"']", "", text)
    return re.sub(r"\s+", "", text).lower()


def test_dockerfile_installs_git_for_runtime_support():
    """Docker image must include Git for evergreen repository interactions."""
    assert "git" in {
        _canonical_package_name(package)
        for package in _extract_apt_package_tokens("install")
    }


def test_dockerfile_keeps_required_build_packages_for_cffi_on_python_3_15():
    """Build dependencies are required while lockfile needs source builds on Python 3.15."""
    installed_packages = {
        _canonical_package_name(package)
        for package in _extract_apt_package_tokens("install")
    }
    assert {"gcc", "libc6-dev", "libffi-dev"}.issubset(installed_packages)


def test_dockerfile_does_not_pin_apt_package_versions():
    """Exact apt version pins break on moving Debian repositories."""
    install_tokens = _extract_apt_package_tokens("install")
    assert install_tokens, "Dockerfile must include apt install package tokens"
    assert all("=" not in package for package in install_tokens)


def test_dockerfile_purges_temporary_build_dependencies_after_sync():
    """Temporary compiler packages should be removed after dependency install."""
    dockerfile = _normalized_dockerfile()
    assert dockerfile.index("apt-get -y purge --auto-remove") > dockerfile.index(
        "uv sync --frozen --no-dev --no-editable"
    )
    assert {"gcc", "libc6-dev", "libffi-dev"}.issubset(
        {
            _canonical_package_name(package)
            for package in _extract_apt_package_tokens("purge")
        }
    )


def test_dockerfile_does_not_purge_git():
    """Git must remain available at runtime after temporary-package cleanup."""
    removed_package_tokens = (
        _extract_apt_package_tokens("purge")
        + _extract_apt_package_tokens("remove")
        + _extract_apt_package_tokens("autoremove")
    )
    removed_packages = {
        _canonical_package_name(package) for package in removed_package_tokens
    }
    assert "git" not in removed_packages
    assert all(
        not re.search(r"\bgit[.*?+\[\]{}|()\\-]*\b", token)
        for token in removed_package_tokens
    )


def test_dockerfile_does_not_use_variable_expansion_for_apt_packages():
    """Apt package names must be explicit so pin checks cannot be bypassed."""
    package_tokens = (
        _extract_apt_package_tokens("install")
        + _extract_apt_package_tokens("purge")
        + _extract_apt_package_tokens("remove")
        + _extract_apt_package_tokens("autoremove")
    )
    assert all("$" not in token and "`" not in token for token in package_tokens)


def test_dockerfile_does_not_use_apt_preferences_version_pinning():
    """APT preferences version pinning reintroduces the same fragility as inline pins."""
    canonical = _canonical_shell_text(_normalized_dockerfile())
    assert "/etc/apt/preferen" not in canonical
    assert "pin:version" not in canonical
    assert "dir::etc::preferences" not in canonical
    assert "dir::etc::preferencesparts" not in canonical


def test_dockerfile_does_not_use_run_heredoc_blocks():
    """RUN heredocs can hide apt commands from line-oriented guardrails."""
    assert not re.search(
        r"^\s*RUN(?:\s+--\S+)*\s+<<",
        _normalized_dockerfile(),
        re.IGNORECASE | re.MULTILINE,
    )


def test_dockerfile_does_not_wrap_commands_with_nested_shells():
    """Nested shells can hide apt operations from static package-token checks."""
    dockerfile = _normalized_dockerfile()
    assert not re.search(r"\b(?:bash|sh)\s+-\S*c\S*\b", dockerfile, re.IGNORECASE)


def test_dockerfile_keeps_apt_as_top_level_shell_command():
    """Apt invocations must be explicit top-level shell segments for static checks."""
    for segment in _iter_run_segments():
        tokens = _strip_run_prefix_tokens(segment)
        if not _segment_has_apt_command(segment):
            continue
        assert tokens and tokens[0] in {"apt", "apt-get"}


def test_dockerfile_does_not_indirect_apt_commands():
    """Apt must be called directly so pinning checks cannot be sidestepped via variables."""
    for segment in _iter_run_segments():
        assert not re.search(
            r"[\"']?\$(?:\{?[A-Za-z_][A-Za-z0-9_]*\}?)[\"']?\s+(?:-[\w-]+\s+)*(?:update|install|purge|remove|autoremove)\b",
            segment,
            re.IGNORECASE,
        )


def test_dockerfile_does_not_delete_runtime_git_binary_paths():
    """Dockerfile must not remove git binaries after installing runtime git support."""
    for segment in _iter_run_segments():
        assert not re.search(
            r"\brm\b[^;&\n]*(?:/usr/bin/git|/usr/lib/git-core/git)\b",
            segment,
            re.IGNORECASE,
        )
        assert not re.search(
            r"\b(?:find|unlink)\b[^;&\n]*(?:/usr/bin/git|/usr/lib/git-core/git|\sgit(?:\s|$))",
            segment,
            re.IGNORECASE,
        )


def test_dockerfile_does_not_remove_git_with_dpkg():
    """Dockerfile must not use dpkg remove/purge operations for package cleanup."""
    for segment in _iter_run_segments():
        canonical_segment = re.sub(r"[\"']", "", segment).replace("\\", "")
        assert not re.search(
            r"\bdpkg\b[^;&\n]*(?:--purge|--remove|-P|-r)[^;&\n]*\bgit\b",
            canonical_segment,
            re.IGNORECASE,
        )
