"""Tests for the exceptions module."""

import unittest
from unittest.mock import Mock

from exceptions import OptionalFileNotFoundError, check_optional_file
from github import GithubException, UnknownObjectException


class TestOptionalFileNotFoundError(unittest.TestCase):
    """Test the OptionalFileNotFoundError exception."""

    def test_optional_file_not_found_error_inherits_from_unknown_object_exception(self):
        """Test that OptionalFileNotFoundError inherits from github.UnknownObjectException."""
        error = OptionalFileNotFoundError(status=404, data="Not Found")
        self.assertIsInstance(error, UnknownObjectException)

    def test_optional_file_not_found_error_creation(self):
        """Test OptionalFileNotFoundError can be created."""
        error = OptionalFileNotFoundError(status=404, data="Not Found")
        self.assertIsInstance(error, OptionalFileNotFoundError)

    def test_optional_file_not_found_error_with_response(self):
        """Test OptionalFileNotFoundError with HTTP response data."""
        error = OptionalFileNotFoundError(status=404, data="Not Found", headers={})
        self.assertIsInstance(error, OptionalFileNotFoundError)

    def test_can_catch_as_unknown_object_exception(self):
        """Test that OptionalFileNotFoundError can be caught as github.UnknownObjectException."""
        try:
            raise OptionalFileNotFoundError(status=404, data="Not Found")
        except UnknownObjectException as e:
            self.assertIsInstance(e, OptionalFileNotFoundError)
        except Exception:  # pylint: disable=broad-exception-caught
            self.fail(
                "OptionalFileNotFoundError should be catchable as UnknownObjectException"
            )

    def test_can_catch_specifically(self):
        """Test that OptionalFileNotFoundError can be caught specifically."""
        try:
            raise OptionalFileNotFoundError(status=404, data="Not Found")
        except OptionalFileNotFoundError as e:
            self.assertIsInstance(e, OptionalFileNotFoundError)
        except Exception:  # pylint: disable=broad-exception-caught
            self.fail("OptionalFileNotFoundError should be catchable specifically")

    def test_optional_file_not_found_error_properties(self):
        """Test OptionalFileNotFoundError has expected properties."""
        error = OptionalFileNotFoundError(
            status=404, data="Not Found", headers={"X-Test": "value"}
        )
        self.assertEqual(error.status, 404)
        self.assertEqual(error.data, "Not Found")


class TestCheckOptionalFile(unittest.TestCase):
    """Test the check_optional_file utility function."""

    def test_check_optional_file_with_existing_file(self):
        """Test check_optional_file when file exists."""
        mock_repo = Mock()
        mock_file_contents = Mock()
        mock_file_contents.size = 100
        mock_repo.get_contents.return_value = mock_file_contents

        result = check_optional_file(mock_repo, "config.yml")

        self.assertEqual(result, mock_file_contents)
        mock_repo.get_contents.assert_called_once_with("config.yml")

    def test_check_optional_file_with_empty_file(self):
        """Test check_optional_file when file exists but is empty."""
        mock_repo = Mock()
        mock_file_contents = Mock()
        mock_file_contents.size = 0
        mock_repo.get_contents.return_value = mock_file_contents

        result = check_optional_file(mock_repo, "config.yml")

        self.assertIsNone(result)
        mock_repo.get_contents.assert_called_once_with("config.yml")

    def test_check_optional_file_with_missing_file(self):
        """Test check_optional_file when file doesn't exist."""
        mock_repo = Mock()

        original_error = UnknownObjectException(status=404, data="Not Found")
        mock_repo.get_contents.side_effect = original_error

        with self.assertRaises(OptionalFileNotFoundError) as context:
            check_optional_file(mock_repo, "missing.yml")

        self.assertEqual(context.exception.__cause__, original_error)
        mock_repo.get_contents.assert_called_once_with("missing.yml")

    def test_check_optional_file_with_empty_repository(self):
        """Test check_optional_file when the repository is empty.

        An empty repository returns a 404 that PyGithub raises as the base
        GithubException rather than UnknownObjectException. It should be
        translated to OptionalFileNotFoundError so the repository is skipped.
        """
        mock_repo = Mock()

        original_error = GithubException(
            status=404, data={"message": "This repository is empty."}
        )
        mock_repo.get_contents.side_effect = original_error

        with self.assertRaises(OptionalFileNotFoundError) as context:
            check_optional_file(mock_repo, "config.yml")

        self.assertEqual(context.exception.__cause__, original_error)
        mock_repo.get_contents.assert_called_once_with("config.yml")

    def test_check_optional_file_reraises_non_404_github_exception(self):
        """Test check_optional_file re-raises non-404 GithubExceptions unchanged."""
        mock_repo = Mock()

        original_error = GithubException(status=403, data={"message": "Forbidden"})
        mock_repo.get_contents.side_effect = original_error

        with self.assertRaises(GithubException) as context:
            check_optional_file(mock_repo, "config.yml")

        self.assertNotIsInstance(context.exception, OptionalFileNotFoundError)
        self.assertEqual(context.exception.status, 403)
        mock_repo.get_contents.assert_called_once_with("config.yml")

    def test_check_optional_file_can_catch_as_unknown_object_exception(self):
        """Test that OptionalFileNotFoundError from check_optional_file can be caught as UnknownObjectException."""
        mock_repo = Mock()

        mock_repo.get_contents.side_effect = UnknownObjectException(
            status=404, data="Not Found"
        )

        try:
            check_optional_file(mock_repo, "missing.yml")
        except UnknownObjectException as e:
            self.assertIsInstance(e, OptionalFileNotFoundError)
        except Exception:  # pylint: disable=broad-exception-caught
            self.fail(
                "Should be able to catch OptionalFileNotFoundError as UnknownObjectException"
            )


if __name__ == "__main__":
    unittest.main()
