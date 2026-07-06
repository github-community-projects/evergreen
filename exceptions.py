"""Custom exceptions for the evergreen application."""

from github import GithubException, UnknownObjectException


class OptionalFileNotFoundError(UnknownObjectException):
    """Exception raised when an optional file is not found.

    This exception inherits from github.UnknownObjectException but provides
    a more explicit name for cases where missing files are expected and should
    not be treated as errors. This is typically used for optional configuration
    files or dependency files that may not exist in all repositories.

    Args:
        status: The HTTP status code
        data: The response data
        headers: The response headers
    """


def check_optional_file(repo, filename):
    """
    Example utility function demonstrating OptionalFileNotFoundError usage.

    This function shows how the new exception type can be used to provide
    more explicit error handling for optional files that may not exist.

    Args:
        repo: GitHub repository object
        filename: Name of the optional file to check

    Returns:
        File contents object if file exists, None if optional file is missing

    Raises:
        OptionalFileNotFoundError: When the file is not found (expected for optional files)
        Other exceptions: For unexpected errors (permissions, network issues, etc.)
    """
    try:
        file_contents = repo.get_contents(filename)
        if hasattr(file_contents, "size"):
            if file_contents.size > 0:
                return file_contents
            return None
        return file_contents if file_contents else None
    except UnknownObjectException as e:
        raise OptionalFileNotFoundError(
            status=e.status, data=e.data, headers=e.headers
        ) from e
    except GithubException as e:
        # An empty repository (one with no commits) returns a 404 that PyGithub
        # raises as the base GithubException ("This repository is empty.")
        # rather than UnknownObjectException. Treat it the same as a missing
        # optional file so the repository is skipped instead of crashing the run.
        if e.status == 404:
            raise OptionalFileNotFoundError(
                status=e.status, data=e.data, headers=e.headers
            ) from e
        raise
