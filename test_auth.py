"""Test cases for the auth module."""

import unittest
from unittest.mock import MagicMock, patch

import auth


class TestAuth(unittest.TestCase):
    """
    Test case for the auth module.
    """

    @patch("auth.Github")
    def test_auth_to_github_with_token(self, mock_github_cls):
        """
        Test the auth_to_github function when the token is provided.
        """
        mock_github_cls.return_value = MagicMock()

        result = auth.auth_to_github("token", "", "", b"", "", False)

        mock_github_cls.assert_called_once()
        self.assertEqual(result, mock_github_cls.return_value)

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

    @patch("auth.Github")
    def test_auth_to_github_with_ghe(self, mock_github_cls):
        """
        Test the auth_to_github function when the GitHub Enterprise URL is provided.
        """
        mock_github_cls.return_value = MagicMock()
        result = auth.auth_to_github(
            "token", "", "", b"", "https://github.example.com", False
        )

        mock_github_cls.assert_called_once()
        call_kwargs = mock_github_cls.call_args
        self.assertEqual(
            call_kwargs.kwargs["base_url"],
            "https://github.example.com/api/v3",
        )
        self.assertEqual(result, mock_github_cls.return_value)

    @patch("auth.Github")
    def test_auth_to_github_with_ghe_and_ghe_api_url(self, mock_github_cls):
        """
        Test that base_url uses the custom API URL when ghe_api_url is provided with token auth.
        """
        mock_github_cls.return_value = MagicMock()
        result = auth.auth_to_github(
            "token",
            "",
            "",
            b"",
            "https://github.example.com",
            False,
            ghe_api_url="https://api.example.ghe.com",
        )

        mock_github_cls.assert_called_once()
        call_kwargs = mock_github_cls.call_args
        self.assertEqual(
            call_kwargs.kwargs["base_url"],
            "https://api.example.ghe.com",
        )
        self.assertEqual(result, mock_github_cls.return_value)

    @patch("auth.Github")
    @patch("auth.Auth.AppAuth")
    def test_auth_to_github_with_ghe_and_ghe_app(
        self, mock_app_auth_cls, mock_github_cls
    ):
        """
        Test the auth_to_github function when the GitHub Enterprise URL is provided and the app was created in GitHub Enterprise URL.
        """
        mock_app_auth = MagicMock()
        mock_app_auth_cls.return_value = mock_app_auth
        mock_installation_auth = MagicMock()
        mock_app_auth.get_installation_auth.return_value = mock_installation_auth
        mock_github_cls.return_value = MagicMock()

        result = auth.auth_to_github(
            "", 123, 456, b"123", "https://github.example.com", True
        )

        mock_app_auth_cls.assert_called_once_with(123, "123")
        mock_app_auth.get_installation_auth.assert_called_once_with(456)
        mock_github_cls.assert_called_once()
        call_kwargs = mock_github_cls.call_args
        self.assertEqual(
            call_kwargs.kwargs["base_url"],
            "https://github.example.com/api/v3",
        )
        self.assertEqual(call_kwargs.kwargs["auth"], mock_installation_auth)
        self.assertEqual(result, mock_github_cls.return_value)

    @patch("auth.Github")
    @patch("auth.Auth.AppAuth")
    def test_auth_to_github_with_ghe_app_and_ghe_api_url(
        self, mock_app_auth_cls, mock_github_cls
    ):
        """
        Test that base_url uses the custom API URL when ghe_api_url is provided with app auth.
        """
        mock_app_auth = MagicMock()
        mock_app_auth_cls.return_value = mock_app_auth
        mock_installation_auth = MagicMock()
        mock_app_auth.get_installation_auth.return_value = mock_installation_auth
        mock_github_cls.return_value = MagicMock()

        result = auth.auth_to_github(
            "",
            123,
            456,
            b"123",
            "https://github.example.com",
            True,
            ghe_api_url="https://api.example.ghe.com",
        )

        mock_app_auth_cls.assert_called_once_with(123, "123")
        mock_app_auth.get_installation_auth.assert_called_once_with(456)
        mock_github_cls.assert_called_once()
        call_kwargs = mock_github_cls.call_args
        self.assertEqual(
            call_kwargs.kwargs["base_url"],
            "https://api.example.ghe.com",
        )
        self.assertEqual(result, mock_github_cls.return_value)

    @patch("auth.Github")
    @patch("auth.Auth.AppAuth")
    def test_auth_to_github_with_app(self, mock_app_auth_cls, mock_github_cls):
        """
        Test the auth_to_github function when app credentials are provided
        """
        mock_app_auth = MagicMock()
        mock_app_auth_cls.return_value = mock_app_auth
        mock_installation_auth = MagicMock()
        mock_app_auth.get_installation_auth.return_value = mock_installation_auth
        mock_github_cls.return_value = MagicMock()

        result = auth.auth_to_github(
            "", 123, 456, b"123", "https://github.example.com", False
        )

        mock_app_auth_cls.assert_called_once_with(123, "123")
        mock_app_auth.get_installation_auth.assert_called_once_with(456)
        mock_github_cls.assert_called_once()
        call_kwargs = mock_github_cls.call_args
        self.assertNotIn("base_url", call_kwargs.kwargs)
        self.assertEqual(call_kwargs.kwargs["auth"], mock_installation_auth)
        self.assertEqual(result, mock_github_cls.return_value)

    @patch("auth.Github")
    @patch("auth.Auth.AppAuth")
    def test_auth_to_github_with_app_enterprise_only_false_ignores_ghe_api_url(
        self, mock_app_auth_cls, mock_github_cls
    ):
        """
        Test that ghe_api_url does not override base_url when
        gh_app_enterprise_only is False, since the app authenticates against github.com.
        The ghe_api_url still applies to direct REST/GraphQL calls via get_api_endpoint().
        """
        mock_app_auth = MagicMock()
        mock_app_auth_cls.return_value = mock_app_auth
        mock_installation_auth = MagicMock()
        mock_app_auth.get_installation_auth.return_value = mock_installation_auth
        mock_github_cls.return_value = MagicMock()

        result = auth.auth_to_github(
            "",
            123,
            456,
            b"123",
            "https://github.example.com",
            False,
            ghe_api_url="https://api.example.ghe.com",
        )

        mock_app_auth_cls.assert_called_once_with(123, "123")
        mock_app_auth.get_installation_auth.assert_called_once_with(456)
        mock_github_cls.assert_called_once()
        call_kwargs = mock_github_cls.call_args
        # base_url should NOT be set -- app authenticates against github.com
        self.assertNotIn("base_url", call_kwargs.kwargs)
        self.assertEqual(result, mock_github_cls.return_value)

    @patch("auth.GithubIntegration")
    @patch("auth.Auth.AppAuth")
    def test_get_github_app_installation_token(self, mock_app_auth_cls, mock_gi_cls):
        """
        Test the get_github_app_installation_token function.
        """
        dummy_token = "dummytoken"
        mock_app_auth = MagicMock()
        mock_app_auth_cls.return_value = mock_app_auth
        mock_gi = MagicMock()
        mock_gi_cls.return_value = mock_gi
        mock_access_token = MagicMock()
        mock_access_token.token = dummy_token
        mock_gi.get_access_token.return_value = mock_access_token

        result = auth.get_github_app_installation_token(
            ghe="https://github.example.com",
            gh_app_id=12345,
            gh_app_private_key_bytes=b"gh_private_key",
            gh_app_installation_id=678910,
        )

        self.assertEqual(result, dummy_token)

    @patch("auth.GithubIntegration")
    @patch("auth.Auth.AppAuth")
    def test_get_github_app_installation_token_casts_int_app_id(
        self, mock_app_auth_cls, mock_gi_cls
    ):
        """
        Test that get_github_app_installation_token casts an int gh_app_id to int
        and decodes private key bytes to str for Auth.AppAuth.
        """
        mock_app_auth = MagicMock()
        mock_app_auth_cls.return_value = mock_app_auth
        mock_gi = MagicMock()
        mock_gi_cls.return_value = mock_gi
        mock_access_token = MagicMock()
        mock_access_token.token = "dummytoken"
        mock_gi.get_access_token.return_value = mock_access_token

        auth.get_github_app_installation_token(
            ghe="",
            gh_app_id=12345,
            gh_app_private_key_bytes=b"private_key",
            gh_app_installation_id=678910,
        )

        mock_app_auth_cls.assert_called_once_with(12345, "private_key")
        mock_gi.get_access_token.assert_called_once_with(678910)

    @patch("auth.GithubIntegration")
    @patch("auth.Auth.AppAuth")
    def test_get_github_app_installation_token_request_failure(
        self, mock_app_auth_cls, mock_gi_cls
    ):
        """
        Test the get_github_app_installation_token function returns None when the request fails.
        """
        mock_app_auth = MagicMock()
        mock_app_auth_cls.return_value = mock_app_auth
        mock_gi = MagicMock()
        mock_gi_cls.return_value = mock_gi
        mock_gi.get_access_token.side_effect = Exception("Request failed")

        result = auth.get_github_app_installation_token(
            ghe="https://api.github.com",
            gh_app_id=12345,
            gh_app_private_key_bytes=b"private_key",
            gh_app_installation_id=678910,
        )

        self.assertIsNone(result)

    @patch("auth.GithubIntegration")
    @patch("auth.Auth.AppAuth")
    def test_get_github_app_installation_token_with_ghe_api_url(
        self, mock_app_auth_cls, mock_gi_cls
    ):
        """
        Test that get_github_app_installation_token uses the custom API URL when provided.
        """
        dummy_token = "dummytoken"
        mock_app_auth = MagicMock()
        mock_app_auth_cls.return_value = mock_app_auth
        mock_gi = MagicMock()
        mock_gi_cls.return_value = mock_gi
        mock_access_token = MagicMock()
        mock_access_token.token = dummy_token
        mock_gi.get_access_token.return_value = mock_access_token

        result = auth.get_github_app_installation_token(
            ghe="https://github.example.com",
            gh_app_id=12345,
            gh_app_private_key_bytes=b"private_key",
            gh_app_installation_id=678910,
            ghe_api_url="https://api.example.ghe.com",
        )

        self.assertEqual(result, dummy_token)
        mock_gi_cls.assert_called_once_with(
            auth=mock_app_auth,
            base_url="https://api.example.ghe.com",
        )

    def test_get_github_app_installation_token_missing_app_id(self):
        """
        Test that get_github_app_installation_token returns None when gh_app_id is None.
        """
        result = auth.get_github_app_installation_token(
            ghe="",
            gh_app_id=None,
            gh_app_private_key_bytes=b"private_key",
            gh_app_installation_id=678910,
        )
        self.assertIsNone(result)

    def test_get_github_app_installation_token_missing_installation_id(self):
        """
        Test that get_github_app_installation_token returns None when gh_app_installation_id is None.
        """
        result = auth.get_github_app_installation_token(
            ghe="",
            gh_app_id=12345,
            gh_app_private_key_bytes=b"private_key",
            gh_app_installation_id=None,
        )
        self.assertIsNone(result)


if __name__ == "__main__":
    unittest.main()
