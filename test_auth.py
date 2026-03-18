"""Test cases for the auth module."""

import unittest
from unittest.mock import MagicMock, patch

import auth
import requests


class TestAuth(unittest.TestCase):
    """
    Test case for the auth module.
    """

    @patch("github3.login")
    def test_auth_to_github_with_token(self, mock_login):
        """
        Test the auth_to_github function when the token is provided.
        """
        mock_login.return_value = "Authenticated to GitHub.com"

        result = auth.auth_to_github("token", "", "", b"", "", False)

        self.assertEqual(result, "Authenticated to GitHub.com")

    def test_auth_to_github_without_token(self):
        """
        Test the auth_to_github function when the token is not provided.
        Expect a ValueError to be raised.
        """
        with self.assertRaises(ValueError) as context_manager:
            auth.auth_to_github("", "", "", b"", "", False)
        the_exception = context_manager.exception
        self.assertEqual(
            str(the_exception),
            "GH_TOKEN or the set of [GH_APP_ID, GH_APP_INSTALLATION_ID, GH_APP_PRIVATE_KEY] environment variables are not set",
        )

    @patch("github3.github.GitHubEnterprise")
    def test_auth_to_github_with_ghe(self, mock_ghe):
        """
        Test the auth_to_github function when the GitHub Enterprise URL is provided.
        """
        mock_ghe.return_value = "Authenticated to GitHub Enterprise"
        result = auth.auth_to_github(
            "token", "", "", b"", "https://github.example.com", False
        )

        self.assertEqual(result, "Authenticated to GitHub Enterprise")

    @patch("github3.github.GitHubEnterprise")
    def test_auth_to_github_with_ghe_and_ghe_app(self, mock_ghe):
        """
        Test the auth_to_github function when the GitHub Enterprise URL is provided and the app was created in GitHub Enterprise URL.
        """
        mock = mock_ghe.return_value
        mock.login_as_app_installation = MagicMock(return_value=True)
        result = auth.auth_to_github(
            "", 123, 456, b"123", "https://github.example.com", True
        )
        mock.login_as_app_installation.assert_called_once_with(b"123", "123", 456)
        self.assertEqual(result, mock)

    @patch("github3.github.GitHub")
    def test_auth_to_github_with_app(self, mock_gh):
        """
        Test the auth_to_github function when app credentials are provided
        """
        mock = mock_gh.return_value
        mock.login_as_app_installation = MagicMock(return_value=True)
        result = auth.auth_to_github(
            "", 123, 456, b"123", "https://github.example.com", False
        )
        mock.login_as_app_installation.assert_called_once_with(b"123", "123", 456)
        self.assertEqual(result, mock)

    @patch("github3.apps.create_jwt_headers", MagicMock(return_value="gh_token"))
    @patch("requests.post")
    def test_get_github_app_installation_token(self, mock_post):
        """
        Test the get_github_app_installation_token function.
        """
        dummy_token = "dummytoken"
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {"token": dummy_token}
        mock_post.return_value = mock_response

        result = auth.get_github_app_installation_token(
            b"ghe", "gh_private_token", "gh_app_id", "gh_installation_id"
        )

        self.assertEqual(result, dummy_token)

    @patch("github3.apps.create_jwt_headers", MagicMock(return_value="gh_token"))
    @patch("auth.requests.post")
    def test_get_github_app_installation_token_request_failure(self, mock_post):
        """
        Test the get_github_app_installation_token function returns None when the request fails.
        """
        # Mock the post request to raise a RequestException
        mock_post.side_effect = requests.exceptions.RequestException("Request failed")

        # Call the function with test data
        result = auth.get_github_app_installation_token(
            ghe="https://api.github.com",
            gh_app_id=12345,
            gh_app_private_key_bytes=b"private_key",
            gh_app_installation_id=678910,
        )

        # Assert that the result is None
        self.assertIsNone(result)

    @patch("github3.login")
    def test_auth_to_github_invalid_credentials(self, mock_login):
        """
        Test the auth_to_github function raises correct ValueError
        when credentials are present but incorrect.
        """
        mock_login.return_value = None
        with self.assertRaises(ValueError) as context_manager:
            auth.auth_to_github("not_a_valid_token", "", "", b"", "", False)

        the_exception = context_manager.exception
        self.assertEqual(
            str(the_exception),
            "Unable to authenticate to GitHub",
        )


if __name__ == "__main__":
    unittest.main()
