"""This is the module that contains functions related to authenticating to GitHub with a personal access token."""

import env
from github import Auth, Github, GithubIntegration


def auth_to_github(
    token: str,
    gh_app_id: int | None,
    gh_app_installation_id: int | None,
    gh_app_private_key_bytes: bytes,
    ghe: str,
    gh_app_enterprise_only: bool,
    ghe_api_url: str = "",
) -> Github:
    """
    Connect to GitHub.com or GitHub Enterprise, depending on env variables.

    Args:
        token (str): the GitHub personal access token
        gh_app_id (int | None): the GitHub App ID
        gh_app_installation_id (int | None): the GitHub App Installation ID
        gh_app_private_key_bytes (bytes): the GitHub App Private Key
        ghe (str): the GitHub Enterprise URL
        gh_app_enterprise_only (bool): Set this to true if the GH APP is created on GHE and needs to communicate with GHE api only
        ghe_api_url (str): the full GitHub Enterprise API endpoint URL override

    Returns:
        Github: the GitHub connection object
    """
    if gh_app_id and gh_app_private_key_bytes and gh_app_installation_id:
        app_auth = Auth.AppAuth(int(gh_app_id), gh_app_private_key_bytes.decode())
        installation_auth = app_auth.get_installation_auth(int(gh_app_installation_id))
        if ghe and gh_app_enterprise_only:
            base_url = env.get_api_endpoint(ghe, ghe_api_url)
            github_connection = Github(base_url=base_url, auth=installation_auth)
        else:
            github_connection = Github(auth=installation_auth)
    elif ghe and token:
        base_url = env.get_api_endpoint(ghe, ghe_api_url)
        github_connection = Github(base_url=base_url, auth=Auth.Token(token))
    elif token:
        github_connection = Github(auth=Auth.Token(token))
    else:
        raise ValueError(
            "GH_TOKEN or the set of [GH_APP_ID, GH_APP_INSTALLATION_ID, GH_APP_PRIVATE_KEY] environment variables are not set"
        )

    return github_connection


def get_github_app_installation_token(
    ghe: str,
    gh_app_id: int | None,
    gh_app_private_key_bytes: bytes,
    gh_app_installation_id: int | None,
    ghe_api_url: str = "",
) -> str | None:
    """
    Get a GitHub App Installation token.
    API: https://docs.github.com/en/apps/creating-github-apps/authenticating-with-a-github-app/authenticating-as-a-github-app-installation

    Args:
        ghe (str): the GitHub Enterprise endpoint
        gh_app_id (int | None): the GitHub App ID
        gh_app_private_key_bytes (bytes): the GitHub App Private Key
        gh_app_installation_id (int | None): the GitHub App Installation ID
        ghe_api_url (str): the full GitHub Enterprise API endpoint URL override

    Returns:
        str | None: the GitHub App token, or None if IDs are missing or the request fails
    """
    if not gh_app_id or not gh_app_installation_id:
        return None
    try:
        app_auth = Auth.AppAuth(int(gh_app_id), gh_app_private_key_bytes.decode())
        if ghe:
            base_url = env.get_api_endpoint(ghe, ghe_api_url)
            gi = GithubIntegration(auth=app_auth, base_url=base_url)
        else:
            gi = GithubIntegration(auth=app_auth)
        installation_token = gi.get_access_token(int(gh_app_installation_id))
        return installation_token.token
    except Exception as e:  # pylint: disable=broad-exception-caught
        print(f"Request failed: {e}")
        return None
