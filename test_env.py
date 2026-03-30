# pylint: disable=too-many-public-methods,too-many-lines

"""Test the get_env_vars function"""

import os
import random
import string
import unittest
from unittest.mock import patch

from env import (
    MAX_BODY_LENGTH,
    MAX_COMMIT_MESSAGE_LENGTH,
    MAX_TITLE_LENGTH,
    EvergreenConfig,
    get_api_endpoint,
    get_env_vars,
)


class TestEnv(unittest.TestCase):
    """Test the get_env_vars function"""

    def setUp(self):
        env_keys = [
            "BATCH_SIZE",
            "BODY",
            "COMMIT_MESSAGE",
            "CREATED_AFTER_DATE",
            "EXEMPT_REPOS",
            "GH_APP_ID",
            "GH_APP_INSTALLATION_ID",
            "GH_APP_PRIVATE_KEY",
            "GITHUB_APP_ENTERPRISE_ONLY",
            "GH_ENTERPRISE_API_URL",
            "GH_ENTERPRISE_URL",
            "GH_TOKEN",
            "GROUP_DEPENDENCIES",
            "ORGANIZATION",
            "PROJECT_ID",
            "TITLE",
            "TYPE",
            "UPDATE_EXISTING",
            "REPO_SPECIFIC_EXEMPTIONS",
            "REPOSITORY_SEARCH_QUERY",
            "SCHEDULE",
            "SCHEDULE_DAY",
            "LABELS",
        ]
        for key in env_keys:
            if key in os.environ:
                del os.environ[key]

    @patch.dict(
        os.environ,
        {
            "ORGANIZATION": "my_organization",
            "EXEMPT_REPOS": "repo4,repo5",
            "GH_TOKEN": "my_token",
            "TYPE": "issue",
            "TITLE": "Dependabot Alert custom title",
            "BODY": "Dependabot custom body",
            "CREATED_AFTER_DATE": "2020-01-01",
            "COMMIT_MESSAGE": "Create dependabot configuration",
            "PROJECT_ID": "123",
            "GROUP_DEPENDENCIES": "false",
        },
        clear=True,
    )
    def test_get_env_vars_with_org(self):
        """Test that all environment variables are set correctly using an organization"""
        expected_result = EvergreenConfig(
            organization="my_organization",
            repository_list=[],
            search_query="",
            gh_app_id=None,
            gh_app_installation_id=None,
            gh_app_private_key_bytes=b"",
            gh_app_enterprise_only=False,
            token="my_token",
            ghe="",
            exempt_repositories_list=["repo4", "repo5"],
            follow_up_type="issue",
            title="Dependabot Alert custom title",
            body="Dependabot custom body",
            created_after_date="2020-01-01",
            dry_run=False,
            commit_message="Create dependabot configuration",
            project_id="123",
            group_dependencies=False,
            filter_visibility=["internal", "private", "public"],
            batch_size=None,
            enable_security_updates=True,
            exempt_ecosystems=[],
            update_existing=False,
            repo_specific_exemptions={},
            schedule="weekly",
            schedule_day="",
            team_name=None,
            labels=[],
            dependabot_config_file=None,
            ghe_api_url="",
        )
        result = get_env_vars(True)
        self.assertEqual(result, expected_result)

    @patch.dict(
        os.environ,
        {
            "ORGANIZATION": "my_organization",
            "EXEMPT_REPOS": "repo4,repo5",
            "GH_TOKEN": "my_token",
            "TYPE": "issue",
            "TITLE": "Dependabot Alert custom title",
            "BODY": "Dependabot custom body",
            "CREATED_AFTER_DATE": "2020-01-01",
            "COMMIT_MESSAGE": "Create dependabot configuration",
            "PROJECT_ID": "123",
            "GROUP_DEPENDENCIES": "false",
            "REPO_SPECIFIC_EXEMPTIONS": "repo1:gomod;repo2:docker,gomod;",
        },
        clear=True,
    )
    def test_get_env_vars_with_org_and_repo_specific_exemptions(self):
        """Test that all environment variables are set correctly using an organization"""
        expected_result = EvergreenConfig(
            organization="my_organization",
            repository_list=[],
            search_query="",
            gh_app_id=None,
            gh_app_installation_id=None,
            gh_app_private_key_bytes=b"",
            gh_app_enterprise_only=False,
            token="my_token",
            ghe="",
            exempt_repositories_list=["repo4", "repo5"],
            follow_up_type="issue",
            title="Dependabot Alert custom title",
            body="Dependabot custom body",
            created_after_date="2020-01-01",
            dry_run=False,
            commit_message="Create dependabot configuration",
            project_id="123",
            group_dependencies=False,
            filter_visibility=["internal", "private", "public"],
            batch_size=None,
            enable_security_updates=True,
            exempt_ecosystems=[],
            update_existing=False,
            repo_specific_exemptions={
                "repo1": ["gomod"],
                "repo2": ["docker", "gomod"],
            },
            schedule="weekly",
            schedule_day="",
            team_name=None,
            labels=[],
            dependabot_config_file=None,
            ghe_api_url="",
        )
        result = get_env_vars(True)
        self.assertEqual(result, expected_result)

    @patch.dict(
        os.environ,
        {
            "ORGANIZATION": "my_organization",
            "EXEMPT_REPOS": "repo4,repo5",
            "GH_TOKEN": "my_token",
            "TYPE": "issue",
            "TITLE": "Dependabot Alert custom title",
            "BODY": "Dependabot custom body",
            "CREATED_AFTER_DATE": "2020-01-01",
            "COMMIT_MESSAGE": "Create dependabot configuration",
            "PROJECT_ID": "123",
            "GROUP_DEPENDENCIES": "false",
            "REPO_SPECIFIC_EXEMPTIONS": "repo1:gomod, docker;",
        },
        clear=True,
    )
    def test_get_env_vars_repo_specific_exemptions_trims_whitespace(self):
        """Test that REPO_SPECIFIC_EXEMPTIONS trims whitespace in ecosystems."""
        expected_result = EvergreenConfig(
            organization="my_organization",
            repository_list=[],
            search_query="",
            gh_app_id=None,
            gh_app_installation_id=None,
            gh_app_private_key_bytes=b"",
            gh_app_enterprise_only=False,
            token="my_token",
            ghe="",
            exempt_repositories_list=["repo4", "repo5"],
            follow_up_type="issue",
            title="Dependabot Alert custom title",
            body="Dependabot custom body",
            created_after_date="2020-01-01",
            dry_run=False,
            commit_message="Create dependabot configuration",
            project_id="123",
            group_dependencies=False,
            filter_visibility=["internal", "private", "public"],
            batch_size=None,
            enable_security_updates=True,
            exempt_ecosystems=[],
            update_existing=False,
            repo_specific_exemptions={
                "repo1": ["gomod", "docker"],
            },
            schedule="weekly",
            schedule_day="",
            team_name=None,
            labels=[],
            dependabot_config_file=None,
            ghe_api_url="",
        )
        result = get_env_vars(True)
        self.assertEqual(result, expected_result)

    @patch.dict(
        os.environ,
        {
            "REPOSITORY": "org/repo1,org2/repo2",
            "GH_TOKEN": "my_token",
            "EXEMPT_REPOS": "repo4,repo5",
            "TYPE": "pull",
            "TITLE": "Dependabot Alert custom title",
            "BODY": "Dependabot custom body",
            "CREATED_AFTER_DATE": "2023-01-01",
            "DRY_RUN": "true",
            "COMMIT_MESSAGE": "Create dependabot configuration",
            "PROJECT_ID": "123",
            "GROUP_DEPENDENCIES": "false",
            "REPO_SPECIFIC_EXEMPTIONS": "org1/repo1-docker;org2/repo2",
        },
        clear=True,
    )
    def test_get_env_vars_repo_specific_exemptions_improper_format(self):
        """Test that REPO_SPECIFIC_EXEMPTIONS is handled correctly when improperly formatted"""
        with self.assertRaises(ValueError) as cm:
            get_env_vars(True)
        the_exception = cm.exception
        self.assertEqual(
            str(the_exception),
            "REPO_SPECIFIC_EXEMPTIONS environment variable not formatted correctly",
        )

    @patch.dict(
        os.environ,
        {
            "REPOSITORY": "org/repo1,org2/repo2",
            "GH_TOKEN": "my_token",
            "EXEMPT_REPOS": "repo4,repo5",
            "TYPE": "pull",
            "TITLE": "Dependabot Alert custom title",
            "BODY": "Dependabot custom body",
            "CREATED_AFTER_DATE": "2023-01-01",
            "DRY_RUN": "true",
            "COMMIT_MESSAGE": "Create dependabot configuration",
            "PROJECT_ID": "123",
            "GROUP_DEPENDENCIES": "false",
            "REPO_SPECIFIC_EXEMPTIONS": "org1/repo1:snap;org2/repo2:docker",
        },
        clear=True,
    )
    def test_get_env_vars_repo_specific_exemptions_unsupported_ecosystem(self):
        """Test that REPO_SPECIFIC_EXEMPTIONS is handled correctly when unsupported ecosystem is provided"""
        with self.assertRaises(ValueError) as cm:
            get_env_vars(True)
        the_exception = cm.exception
        self.assertEqual(
            str(the_exception),
            "REPO_SPECIFIC_EXEMPTIONS environment variable not formatted correctly. Unrecognized package-ecosystem.",
        )

    @patch.dict(
        os.environ,
        {
            "REPOSITORY": "org/repo1,org2/repo2",
            "GH_TOKEN": "my_token",
            "EXEMPT_REPOS": "repo4,repo5",
            "TYPE": "pull",
            "TITLE": "Dependabot Alert custom title",
            "BODY": "Dependabot custom body",
            "CREATED_AFTER_DATE": "2023-01-01",
            "DRY_RUN": "true",
            "COMMIT_MESSAGE": "Create dependabot configuration",
            "PROJECT_ID": "123",
            "GROUP_DEPENDENCIES": "false",
            "REPO_SPECIFIC_EXEMPTIONS": "org1/repo1:docker;org2/repo2:gomod",
        },
        clear=True,
    )
    def test_get_env_vars_with_repos(self):
        """Test that all environment variables are set correctly using a list of repositories"""
        expected_result = EvergreenConfig(
            organization=None,
            repository_list=["org/repo1", "org2/repo2"],
            search_query="",
            gh_app_id=None,
            gh_app_installation_id=None,
            gh_app_private_key_bytes=b"",
            gh_app_enterprise_only=False,
            token="my_token",
            ghe="",
            exempt_repositories_list=["repo4", "repo5"],
            follow_up_type="pull",
            title="Dependabot Alert custom title",
            body="Dependabot custom body",
            created_after_date="2023-01-01",
            dry_run=True,
            commit_message="Create dependabot configuration",
            project_id="123",
            group_dependencies=False,
            filter_visibility=["internal", "private", "public"],
            batch_size=None,
            enable_security_updates=True,
            exempt_ecosystems=[],
            update_existing=False,
            repo_specific_exemptions={
                "org1/repo1": ["docker"],
                "org2/repo2": ["gomod"],
            },
            schedule="weekly",
            schedule_day="",
            team_name=None,
            labels=[],
            dependabot_config_file=None,
            ghe_api_url="",
        )
        result = get_env_vars(True)
        self.assertEqual(result, expected_result)

    @patch.dict(
        os.environ,
        {
            "TEAM_NAME": "engineering",
            "ORGANIZATION": "my_organization",
            "GH_TOKEN": "my_token",
            "EXEMPT_REPOS": "repo4,repo5",
            "TYPE": "pull",
            "TITLE": "Dependabot Alert custom title",
            "BODY": "Dependabot custom body",
            "CREATED_AFTER_DATE": "2023-01-01",
            "DRY_RUN": "true",
            "COMMIT_MESSAGE": "Create dependabot configuration",
            "PROJECT_ID": "123",
            "GROUP_DEPENDENCIES": "false",
            "REPO_SPECIFIC_EXEMPTIONS": "org1/repo1:docker;org2/repo2:gomod",
        },
        clear=True,
    )
    def test_get_env_vars_with_team(self):
        """Test that all environment variables are set correctly using a team"""
        expected_result = EvergreenConfig(
            organization="my_organization",
            repository_list=[],
            search_query="",
            gh_app_id=None,
            gh_app_installation_id=None,
            gh_app_private_key_bytes=b"",
            gh_app_enterprise_only=False,
            token="my_token",
            ghe="",
            exempt_repositories_list=["repo4", "repo5"],
            follow_up_type="pull",
            title="Dependabot Alert custom title",
            body="Dependabot custom body",
            created_after_date="2023-01-01",
            dry_run=True,
            commit_message="Create dependabot configuration",
            project_id="123",
            group_dependencies=False,
            filter_visibility=["internal", "private", "public"],
            batch_size=None,
            enable_security_updates=True,
            exempt_ecosystems=[],
            update_existing=False,
            repo_specific_exemptions={
                "org1/repo1": ["docker"],
                "org2/repo2": ["gomod"],
            },
            schedule="weekly",
            schedule_day="",
            team_name="engineering",
            labels=[],
            dependabot_config_file=None,
            ghe_api_url="",
        )
        result = get_env_vars(True)
        self.assertEqual(result, expected_result)

    @patch.dict(
        os.environ,
        {
            "TEAM_NAME": "engineering",
            "REPOSITORY": "org/repo1,org2/repo2",
            "GH_TOKEN": "my_token",
            "EXEMPT_REPOS": "repo4,repo5",
            "TYPE": "pull",
            "TITLE": "Dependabot Alert custom title",
            "BODY": "Dependabot custom body",
            "CREATED_AFTER_DATE": "2023-01-01",
            "DRY_RUN": "true",
            "COMMIT_MESSAGE": "Create dependabot configuration",
            "PROJECT_ID": "123",
            "GROUP_DEPENDENCIES": "false",
            "REPO_SPECIFIC_EXEMPTIONS": "org1/repo1:docker;org2/repo2:gomod",
        },
        clear=True,
    )
    def test_get_env_vars_with_team_and_repo(self):
        """Test the prgoram errors when TEAM_NAME is set with REPOSITORY"""
        with self.assertRaises(ValueError) as cm:
            get_env_vars(True)
        the_exception = cm.exception
        self.assertEqual(
            str(the_exception),
            "TEAM_NAME environment variable cannot be used with REPOSITORY",
        )

    @patch.dict(
        os.environ,
        {
            "ORGANIZATION": "my_organization",
            "GH_TOKEN": "my_token",
        },
        clear=True,
    )
    def test_get_env_vars_optional_values(self):
        """Test that optional values are set to their default values if not provided"""
        expected_result = EvergreenConfig(
            organization="my_organization",
            repository_list=[],
            search_query="",
            gh_app_id=None,
            gh_app_installation_id=None,
            gh_app_private_key_bytes=b"",
            gh_app_enterprise_only=False,
            token="my_token",
            ghe="",
            exempt_repositories_list=[],
            follow_up_type="pull",
            title="Enable Dependabot",
            body=(
                "Dependabot could be enabled for this repository. "
                "Please enable it by merging this pull request "
                "so that we can keep our dependencies up to date and secure."
            ),
            created_after_date="",
            dry_run=False,
            commit_message="Create/Update dependabot.yaml",
            project_id=None,
            group_dependencies=False,
            filter_visibility=["internal", "private", "public"],
            batch_size=None,
            enable_security_updates=True,
            exempt_ecosystems=[],
            update_existing=False,
            repo_specific_exemptions={},
            schedule="weekly",
            schedule_day="",
            team_name=None,
            labels=[],
            dependabot_config_file=None,
            ghe_api_url="",
        )
        result = get_env_vars(True)
        self.assertEqual(result, expected_result)

    @patch.dict(
        os.environ,
        {
            "ORGANIZATION": "my_organization",
            "GH_TOKEN": "my_token",
            "UPDATE_EXISTING": "true",
        },
        clear=True,
    )
    def test_get_env_vars_with_update_existing(self):
        """Test that optional values are set to their default values if not provided"""
        expected_result = EvergreenConfig(
            organization="my_organization",
            repository_list=[],
            search_query="",
            gh_app_id=None,
            gh_app_installation_id=None,
            gh_app_private_key_bytes=b"",
            gh_app_enterprise_only=False,
            token="my_token",
            ghe="",
            exempt_repositories_list=[],
            follow_up_type="pull",
            title="Enable Dependabot",
            body=(
                "Dependabot could be enabled for this repository. "
                "Please enable it by merging this pull request "
                "so that we can keep our dependencies up to date and secure."
            ),
            created_after_date="",
            dry_run=False,
            commit_message="Create/Update dependabot.yaml",
            project_id=None,
            group_dependencies=False,
            filter_visibility=["internal", "private", "public"],
            batch_size=None,
            enable_security_updates=True,
            exempt_ecosystems=[],
            update_existing=True,
            repo_specific_exemptions={},
            schedule="weekly",
            schedule_day="",
            team_name=None,
            labels=[],
            dependabot_config_file=None,
            ghe_api_url="",
        )
        result = get_env_vars(True)
        self.assertEqual(result, expected_result)

    @patch.dict(os.environ, {})
    def test_get_env_vars_missing_org_or_repo(self):
        """Test that an error is raised if required environment variables are not set"""
        with self.assertRaises(ValueError) as cm:
            get_env_vars(True)
        the_exception = cm.exception
        self.assertEqual(
            str(the_exception),
            "ORGANIZATION, REPOSITORY, and REPOSITORY_SEARCH_QUERY environment variables were not set. Please set one",
        )

    @patch.dict(
        os.environ,
        {
            "ORGANIZATION": "my_organization",
            "GH_APP_ID": "12345",
            "GH_APP_INSTALLATION_ID": "678910",
            "GH_APP_PRIVATE_KEY": "hello",
            "GH_TOKEN": "",
        },
        clear=True,
    )
    def test_get_env_vars_auth_with_github_app_installation(self):
        """Test that an error is raised if at least one type of authentication
        required environment variables are not set"""
        expected_result = EvergreenConfig(
            organization="my_organization",
            repository_list=[],
            search_query="",
            gh_app_id=12345,
            gh_app_installation_id=678910,
            gh_app_private_key_bytes=b"hello",
            gh_app_enterprise_only=False,
            token="",
            ghe="",
            exempt_repositories_list=[],
            follow_up_type="pull",
            title="Enable Dependabot",
            body=(
                "Dependabot could be enabled for this repository. "
                "Please enable it by merging this pull request "
                "so that we can keep our dependencies up to date and secure."
            ),
            created_after_date="",
            dry_run=False,
            commit_message="Create/Update dependabot.yaml",
            project_id=None,
            group_dependencies=False,
            filter_visibility=["internal", "private", "public"],
            batch_size=None,
            enable_security_updates=True,
            exempt_ecosystems=[],
            update_existing=False,
            repo_specific_exemptions={},
            schedule="weekly",
            schedule_day="",
            team_name=None,
            labels=[],
            dependabot_config_file=None,
            ghe_api_url="",
        )
        result = get_env_vars(True)
        self.assertEqual(result, expected_result)

    @patch.dict(
        os.environ,
        {
            "ORGANIZATION": "my_organization",
            "GH_APP_ID": "12345",
            "GH_APP_INSTALLATION_ID": "",
            "GH_APP_PRIVATE_KEY": "",
            "GH_TOKEN": "",
        },
        clear=True,
    )
    def test_get_env_vars_auth_with_github_app_installation_missing_inputs(self):
        """Test that an error is raised there are missing inputs for the gh app"""
        with self.assertRaises(ValueError) as context_manager:
            get_env_vars(True)
        the_exception = context_manager.exception
        self.assertEqual(
            str(the_exception),
            "GH_APP_ID set and GH_APP_INSTALLATION_ID or GH_APP_PRIVATE_KEY variable not set",
        )

    @patch.dict(
        os.environ,
        {
            "ORGANIZATION": "my_organization",
            "GH_APP_ID": "",
            "GH_APP_INSTALLATION_ID": "",
            "GH_APP_PRIVATE_KEY": "",
            "GH_TOKEN": "",
        },
        clear=True,
    )
    def test_get_env_vars_missing_at_least_one_auth(self):
        """Test that an error is raised if at least one type of authentication
        required environment variables are not set"""
        with self.assertRaises(ValueError) as cm:
            get_env_vars(True)
        the_exception = cm.exception
        self.assertEqual(
            str(the_exception),
            "GH_TOKEN environment variable not set",
        )

    @patch.dict(
        os.environ,
        {
            "ORGANIZATION": "my_organization",
            "GH_TOKEN": "my_token",
            "DRY_RUN": "false",
        },
        clear=True,
    )
    def test_get_env_vars_with_repos_no_dry_run(self):
        """Test that all environment variables are set correctly when DRY_RUN is false"""
        expected_result = EvergreenConfig(
            organization="my_organization",
            repository_list=[],
            search_query="",
            gh_app_id=None,
            gh_app_installation_id=None,
            gh_app_private_key_bytes=b"",
            gh_app_enterprise_only=False,
            token="my_token",
            ghe="",
            exempt_repositories_list=[],
            follow_up_type="pull",
            title="Enable Dependabot",
            body=(
                "Dependabot could be enabled for this repository. "
                "Please enable it by merging this pull request "
                "so that we can keep our dependencies up to date and secure."
            ),
            created_after_date="",
            dry_run=False,
            commit_message="Create/Update dependabot.yaml",
            project_id=None,
            group_dependencies=False,
            filter_visibility=["internal", "private", "public"],
            batch_size=None,
            enable_security_updates=True,
            exempt_ecosystems=[],
            update_existing=False,
            repo_specific_exemptions={},
            schedule="weekly",
            schedule_day="",
            team_name=None,
            labels=[],
            dependabot_config_file=None,
            ghe_api_url="",
        )
        result = get_env_vars(True)
        self.assertEqual(result, expected_result)

    @patch.dict(
        os.environ,
        {
            "ORGANIZATION": "my_organization",
            "GH_TOKEN": "my_token",
            "ENABLE_SECURITY_UPDATES": "false",
        },
        clear=True,
    )
    def test_get_env_vars_with_repos_disabled_security_updates(self):
        """Test that all environment variables are set correctly when DRY_RUN is false"""
        expected_result = EvergreenConfig(
            organization="my_organization",
            repository_list=[],
            search_query="",
            gh_app_id=None,
            gh_app_installation_id=None,
            gh_app_private_key_bytes=b"",
            gh_app_enterprise_only=False,
            token="my_token",
            ghe="",
            exempt_repositories_list=[],
            follow_up_type="pull",
            title="Enable Dependabot",
            body=(
                "Dependabot could be enabled for this repository. "
                "Please enable it by merging this pull request "
                "so that we can keep our dependencies up to date and secure."
            ),
            created_after_date="",
            dry_run=False,
            commit_message="Create/Update dependabot.yaml",
            project_id=None,
            group_dependencies=False,
            filter_visibility=["internal", "private", "public"],
            batch_size=None,
            enable_security_updates=False,
            exempt_ecosystems=[],
            update_existing=False,
            repo_specific_exemptions={},
            schedule="weekly",
            schedule_day="",
            team_name=None,
            labels=[],
            dependabot_config_file=None,
            ghe_api_url="",
        )
        result = get_env_vars(True)
        self.assertEqual(result, expected_result)

    @patch.dict(
        os.environ,
        {
            "ORGANIZATION": "my_organization",
            "GH_TOKEN": "my_token",
            "ENABLE_SECURITY_UPDATES": "false",
            "FILTER_VISIBILITY": "private,internal",
        },
        clear=True,
    )
    def test_get_env_vars_with_repos_filter_visibility_multiple_values(self):
        """Test that filter_visibility is set correctly when multiple values are provided"""
        expected_result = EvergreenConfig(
            organization="my_organization",
            repository_list=[],
            search_query="",
            gh_app_id=None,
            gh_app_installation_id=None,
            gh_app_private_key_bytes=b"",
            gh_app_enterprise_only=False,
            token="my_token",
            ghe="",
            exempt_repositories_list=[],
            follow_up_type="pull",
            title="Enable Dependabot",
            body=(
                "Dependabot could be enabled for this repository. "
                "Please enable it by merging this pull request "
                "so that we can keep our dependencies up to date and secure."
            ),
            created_after_date="",
            dry_run=False,
            commit_message="Create/Update dependabot.yaml",
            project_id=None,
            group_dependencies=False,
            filter_visibility=["internal", "private"],
            batch_size=None,
            enable_security_updates=False,
            exempt_ecosystems=[],
            update_existing=False,
            repo_specific_exemptions={},
            schedule="weekly",
            schedule_day="",
            team_name=None,
            labels=[],
            dependabot_config_file=None,
            ghe_api_url="",
        )
        result = get_env_vars(True)
        self.assertEqual(result, expected_result)

    @patch.dict(
        os.environ,
        {
            "ORGANIZATION": "my_organization",
            "GH_TOKEN": "my_token",
            "ENABLE_SECURITY_UPDATES": "false",
            "FILTER_VISIBILITY": "public",
        },
        clear=True,
    )
    def test_get_env_vars_with_repos_filter_visibility_single_value(self):
        """Test that filter_visibility is set correctly when a single value is provided"""
        expected_result = EvergreenConfig(
            organization="my_organization",
            repository_list=[],
            search_query="",
            gh_app_id=None,
            gh_app_installation_id=None,
            gh_app_private_key_bytes=b"",
            gh_app_enterprise_only=False,
            token="my_token",
            ghe="",
            exempt_repositories_list=[],
            follow_up_type="pull",
            title="Enable Dependabot",
            body=(
                "Dependabot could be enabled for this repository. "
                "Please enable it by merging this pull request "
                "so that we can keep our dependencies up to date and secure."
            ),
            created_after_date="",
            dry_run=False,
            commit_message="Create/Update dependabot.yaml",
            project_id=None,
            group_dependencies=False,
            filter_visibility=["public"],
            batch_size=None,
            enable_security_updates=False,
            exempt_ecosystems=[],
            update_existing=False,
            repo_specific_exemptions={},
            schedule="weekly",
            schedule_day="",
            team_name=None,
            labels=[],
            dependabot_config_file=None,
            ghe_api_url="",
        )
        result = get_env_vars(True)
        self.assertEqual(result, expected_result)

    @patch.dict(
        os.environ,
        {
            "ORGANIZATION": "my_organization",
            "GH_TOKEN": "my_token",
            "ENABLE_SECURITY_UPDATES": "false",
            "FILTER_VISIBILITY": "foobar",
        },
        clear=True,
    )
    def test_get_env_vars_with_repos_filter_visibility_invalid_single_value(self):
        """Test that filter_visibility throws an error when an invalid value is provided"""
        with self.assertRaises(ValueError):
            get_env_vars(True)

    @patch.dict(
        os.environ,
        {
            "ORGANIZATION": "my_organization",
            "GH_TOKEN": "my_token",
            "ENABLE_SECURITY_UPDATES": "false",
            "FILTER_VISIBILITY": "public, foobar, private",
        },
        clear=True,
    )
    def test_get_env_vars_with_repos_filter_visibility_invalid_multiple_value(self):
        """Test that filter_visibility throws an error when an invalid value is provided"""
        with self.assertRaises(ValueError):
            get_env_vars(True)

    @patch.dict(
        os.environ,
        {
            "ORGANIZATION": "my_organization",
            "GH_TOKEN": "my_token",
            "ENABLE_SECURITY_UPDATES": "false",
            "FILTER_VISIBILITY": "private,private,public",
        },
        clear=True,
    )
    def test_get_env_vars_with_repos_filter_visibility_no_duplicates(self):
        """Test that filter_visibility is set correctly when there are duplicate values"""
        expected_result = EvergreenConfig(
            organization="my_organization",
            repository_list=[],
            search_query="",
            gh_app_id=None,
            gh_app_installation_id=None,
            gh_app_private_key_bytes=b"",
            gh_app_enterprise_only=False,
            token="my_token",
            ghe="",
            exempt_repositories_list=[],
            follow_up_type="pull",
            title="Enable Dependabot",
            body=(
                "Dependabot could be enabled for this repository. "
                "Please enable it by merging this pull request "
                "so that we can keep our dependencies up to date and secure."
            ),
            created_after_date="",
            dry_run=False,
            commit_message="Create/Update dependabot.yaml",
            project_id=None,
            group_dependencies=False,
            filter_visibility=["private", "public"],
            batch_size=None,
            enable_security_updates=False,
            exempt_ecosystems=[],
            update_existing=False,
            repo_specific_exemptions={},
            schedule="weekly",
            schedule_day="",
            team_name=None,
            labels=[],
            dependabot_config_file=None,
            ghe_api_url="",
        )
        result = get_env_vars(True)
        self.assertEqual(result, expected_result)

    @patch.dict(
        os.environ,
        {
            "ORGANIZATION": "my_organization",
            "GH_TOKEN": "my_token",
            "ENABLE_SECURITY_UPDATES": "false",
            "FILTER_VISIBILITY": "private,private,public",
            "EXEMPT_ECOSYSTEMS": "gomod,docker",
        },
        clear=True,
    )
    def test_get_env_vars_with_repos_exempt_ecosystems(self):
        """Test that filter_visibility is set correctly when there are exempt ecosystems"""
        expected_result = EvergreenConfig(
            organization="my_organization",
            repository_list=[],
            search_query="",
            gh_app_id=None,
            gh_app_installation_id=None,
            gh_app_private_key_bytes=b"",
            gh_app_enterprise_only=False,
            token="my_token",
            ghe="",
            exempt_repositories_list=[],
            follow_up_type="pull",
            title="Enable Dependabot",
            body=(
                "Dependabot could be enabled for this repository. "
                "Please enable it by merging this pull request "
                "so that we can keep our dependencies up to date and secure."
            ),
            created_after_date="",
            dry_run=False,
            commit_message="Create/Update dependabot.yaml",
            project_id=None,
            group_dependencies=False,
            filter_visibility=["private", "public"],
            batch_size=None,
            enable_security_updates=False,
            exempt_ecosystems=["gomod", "docker"],
            update_existing=False,
            repo_specific_exemptions={},
            schedule="weekly",
            schedule_day="",
            team_name=None,
            labels=[],
            dependabot_config_file=None,
            ghe_api_url="",
        )
        result = get_env_vars(True)
        self.assertEqual(result, expected_result)

    @patch.dict(
        os.environ,
        {
            "ORGANIZATION": "my_organization",
            "GH_TOKEN": "my_token",
            "EXEMPT_ECOSYSTEMS": "gomod,docekr",
        },
        clear=True,
    )
    def test_get_env_vars_exempt_ecosystems_unsupported_ecosystem(self):
        """Test that EXEMPT_ECOSYSTEMS raises ValueError for unrecognized ecosystems"""
        with self.assertRaises(ValueError) as cm:
            get_env_vars(True)
        the_exception = cm.exception
        self.assertEqual(
            str(the_exception),
            "EXEMPT_ECOSYSTEMS environment variable contains an unrecognized package-ecosystem: 'docekr'.",
        )

    @patch.dict(
        os.environ,
        {
            "ORGANIZATION": "my_organization",
            "GH_TOKEN": "my_token",
            "ENABLE_SECURITY_UPDATES": "false",
            "FILTER_VISIBILITY": "private,public",
            "EXEMPT_ECOSYSTEMS": "gomod,docker,",
        },
        clear=True,
    )
    def test_get_env_vars_exempt_ecosystems_trailing_comma(self):
        """Test that EXEMPT_ECOSYSTEMS tolerates trailing commas"""
        expected_result = EvergreenConfig(
            organization="my_organization",
            repository_list=[],
            search_query="",
            gh_app_id=None,
            gh_app_installation_id=None,
            gh_app_private_key_bytes=b"",
            gh_app_enterprise_only=False,
            token="my_token",
            ghe="",
            exempt_repositories_list=[],
            follow_up_type="pull",
            title="Enable Dependabot",
            body=(
                "Dependabot could be enabled for this repository. "
                "Please enable it by merging this pull request "
                "so that we can keep our dependencies up to date and secure."
            ),
            created_after_date="",
            dry_run=False,
            commit_message="Create/Update dependabot.yaml",
            project_id=None,
            group_dependencies=False,
            filter_visibility=["private", "public"],
            batch_size=None,
            enable_security_updates=False,
            exempt_ecosystems=["gomod", "docker"],
            update_existing=False,
            repo_specific_exemptions={},
            schedule="weekly",
            schedule_day="",
            team_name=None,
            labels=[],
            dependabot_config_file=None,
            ghe_api_url="",
        )
        result = get_env_vars(True)
        self.assertEqual(result, expected_result)

    @patch.dict(
        os.environ,
        {
            "ORGANIZATION": "my_organization",
            "GH_TOKEN": "my_token",
            "ENABLE_SECURITY_UPDATES": "false",
            "FILTER_VISIBILITY": "private,private,public",
        },
        clear=True,
    )
    def test_get_env_vars_with_no_batch_size(self):
        """Test that filter_visibility is set correctly when there is no batch size provided"""
        expected_result = EvergreenConfig(
            organization="my_organization",
            repository_list=[],
            search_query="",
            gh_app_id=None,
            gh_app_installation_id=None,
            gh_app_private_key_bytes=b"",
            gh_app_enterprise_only=False,
            token="my_token",
            ghe="",
            exempt_repositories_list=[],
            follow_up_type="pull",
            title="Enable Dependabot",
            body=(
                "Dependabot could be enabled for this repository. "
                "Please enable it by merging this pull request "
                "so that we can keep our dependencies up to date and secure."
            ),
            created_after_date="",
            dry_run=False,
            commit_message="Create/Update dependabot.yaml",
            project_id=None,
            group_dependencies=False,
            filter_visibility=["private", "public"],
            batch_size=None,
            enable_security_updates=False,
            exempt_ecosystems=[],
            update_existing=False,
            repo_specific_exemptions={},
            schedule="weekly",
            schedule_day="",
            team_name=None,
            labels=[],
            dependabot_config_file=None,
            ghe_api_url="",
        )
        result = get_env_vars(True)
        self.assertEqual(result, expected_result)

    @patch.dict(
        os.environ,
        {
            "ORGANIZATION": "my_organization",
            "GH_TOKEN": "my_token",
            "ENABLE_SECURITY_UPDATES": "false",
            "FILTER_VISIBILITY": "private,private,public",
            "BATCH_SIZE": str(5),  # os.environ expect str as values
        },
        clear=True,
    )
    def test_get_env_vars_with_batch_size(self):
        """Test that filter_visibility is set correctly when there is a batch size"""
        expected_result = EvergreenConfig(
            organization="my_organization",
            repository_list=[],
            search_query="",
            gh_app_id=None,
            gh_app_installation_id=None,
            gh_app_private_key_bytes=b"",
            gh_app_enterprise_only=False,
            token="my_token",
            ghe="",
            exempt_repositories_list=[],
            follow_up_type="pull",
            title="Enable Dependabot",
            body=(
                "Dependabot could be enabled for this repository. "
                "Please enable it by merging this pull request "
                "so that we can keep our dependencies up to date and secure."
            ),
            created_after_date="",
            dry_run=False,
            commit_message="Create/Update dependabot.yaml",
            project_id=None,
            group_dependencies=False,
            filter_visibility=["private", "public"],
            batch_size=5,
            enable_security_updates=False,
            exempt_ecosystems=[],
            update_existing=False,
            repo_specific_exemptions={},
            schedule="weekly",
            schedule_day="",
            team_name=None,
            labels=[],
            dependabot_config_file=None,
            ghe_api_url="",
        )
        result = get_env_vars(True)
        self.assertEqual(result, expected_result)

    @patch.dict(
        os.environ,
        {
            "ORGANIZATION": "my_organization",
            "GH_TOKEN": "my_token",
            "ENABLE_SECURITY_UPDATES": "false",
            "FILTER_VISIBILITY": "private,private,public",
            "BATCH_SIZE": str(-1),  # os.environ expect str as values
        },
        clear=True,
    )
    def test_get_env_vars_with_invalid_batch_size_int(self):
        """Test that invalid batch size with negative 1 throws exception"""
        with self.assertRaises(ValueError):
            get_env_vars(True)

    @patch.dict(
        os.environ,
        {
            "ORGANIZATION": "my_organization",
            "GH_TOKEN": "my_token",
            "ENABLE_SECURITY_UPDATES": "false",
            "FILTER_VISIBILITY": "private,private,public",
            "BATCH_SIZE": "whatever",
        },
        clear=True,
    )
    def test_get_env_vars_with_invalid_batch_size_str(self):
        """Test that invalid batch size of string throws exception"""
        with self.assertRaises(ValueError):
            get_env_vars(True)

    @patch.dict(
        os.environ,
        {
            "ORGANIZATION": "my_organization",
            "GH_TOKEN": "my_token",
            "CREATED_AFTER_DATE": "20200101",
        },
        clear=True,
    )
    def test_get_env_vars_with_badly_formatted_created_after_date(self):
        """Test that badly formatted CREATED_AFTER_DATE throws exception"""
        with self.assertRaises(ValueError) as context_manager:
            get_env_vars(True)
        the_exception = context_manager.exception
        self.assertEqual(
            str(the_exception),
            "CREATED_AFTER_DATE '20200101' environment variable not in YYYY-MM-DD",
        )

    @patch.dict(
        os.environ,
        {
            "ORGANIZATION": "my_organization",
            "GH_TOKEN": "my_token",
            "SCHEDULE": "annually",
        },
        clear=True,
    )
    def test_get_env_vars_with_bad_schedule_choice(self):
        """Test that bad schedule choice throws exception"""
        with self.assertRaises(ValueError) as context_manager:
            get_env_vars(True)
        the_exception = context_manager.exception
        self.assertEqual(
            str(the_exception),
            "SCHEDULE environment variable not 'daily', 'weekly', or 'monthly'",
        )

    @patch.dict(
        os.environ,
        {
            "ORGANIZATION": "my_organization",
            "GH_TOKEN": "my_token",
            "SCHEDULE": "weekly",
            "SCHEDULE_DAY": "thorsday",
        },
        clear=True,
    )
    def test_get_env_vars_with_bad_schedule_day_choice(self):
        """Test that bad schedule day choice throws exception"""
        with self.assertRaises(ValueError) as context_manager:
            get_env_vars(True)
        the_exception = context_manager.exception
        self.assertEqual(
            str(the_exception),
            "SCHEDULE_DAY environment variable not 'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', or 'sunday'",
        )

    @patch.dict(
        os.environ,
        {
            "ORGANIZATION": "my_organization",
            "GH_TOKEN": "my_token",
            "SCHEDULE": "weekly",
            "SCHEDULE_DAY": "tuesday",
        },
        clear=True,
    )
    def test_get_env_vars_with_valid_schedule_and_schedule_day(self):
        """Test valid schedule and schedule day choices"""
        expected_result = EvergreenConfig(
            organization="my_organization",
            repository_list=[],
            search_query="",
            gh_app_id=None,
            gh_app_installation_id=None,
            gh_app_private_key_bytes=b"",
            gh_app_enterprise_only=False,
            token="my_token",
            ghe="",
            exempt_repositories_list=[],
            follow_up_type="pull",
            title="Enable Dependabot",
            body=(
                "Dependabot could be enabled for this repository. "
                "Please enable it by merging this pull request "
                "so that we can keep our dependencies up to date and secure."
            ),
            created_after_date="",
            dry_run=False,
            commit_message="Create/Update dependabot.yaml",
            project_id=None,
            group_dependencies=False,
            filter_visibility=["internal", "private", "public"],
            batch_size=None,
            enable_security_updates=True,
            exempt_ecosystems=[],
            update_existing=False,
            repo_specific_exemptions={},
            schedule="weekly",
            schedule_day="tuesday",
            team_name=None,
            labels=[],
            dependabot_config_file=None,
            ghe_api_url="",
        )
        result = get_env_vars(True)
        self.assertEqual(result, expected_result)

    @patch.dict(
        os.environ,
        {
            "ORGANIZATION": "my_organization",
            "GH_TOKEN": "my_token",
            "SCHEDULE": "daily",
            "SCHEDULE_DAY": "tuesday",
        },
        clear=True,
    )
    def test_get_env_vars_with_schedule_day_error_when_schedule_not_set(self):
        """Test schedule error setting schedule day when schedule is not set"""
        with self.assertRaises(ValueError) as context_manager:
            get_env_vars(True)
        the_exception = context_manager.exception
        self.assertEqual(
            str(the_exception),
            "SCHEDULE_DAY environment variable not needed when SCHEDULE is not 'weekly'",
        )

    @patch.dict(
        os.environ,
        {
            "ORGANIZATION": "my_organization",
            "GH_TOKEN": "my_token",
            "TYPE": "discussion",
        },
        clear=True,
    )
    def test_get_env_vars_with_incorrect_type(self):
        """Test incorrect type error, should be issue or pull"""
        with self.assertRaises(ValueError) as context_manager:
            get_env_vars(True)
        the_exception = context_manager.exception
        self.assertEqual(
            str(the_exception),
            "TYPE environment variable not 'issue' or 'pull'",
        )

    @patch.dict(
        os.environ,
        {
            "ORGANIZATION": "my_organization",
            "GH_TOKEN": "my_token",
            "LABELS": "dependencies",
        },
        clear=True,
    )
    def test_get_env_vars_with_a_valid_label(self):
        """Test valid single label"""
        expected_result = EvergreenConfig(
            organization="my_organization",
            repository_list=[],
            search_query="",
            gh_app_id=None,
            gh_app_installation_id=None,
            gh_app_private_key_bytes=b"",
            gh_app_enterprise_only=False,
            token="my_token",
            ghe="",
            exempt_repositories_list=[],
            follow_up_type="pull",
            title="Enable Dependabot",
            body=(
                "Dependabot could be enabled for this repository. "
                "Please enable it by merging this pull request "
                "so that we can keep our dependencies up to date and secure."
            ),
            created_after_date="",
            dry_run=False,
            commit_message="Create/Update dependabot.yaml",
            project_id=None,
            group_dependencies=False,
            filter_visibility=["internal", "private", "public"],
            batch_size=None,
            enable_security_updates=True,
            exempt_ecosystems=[],
            update_existing=False,
            repo_specific_exemptions={},
            schedule="weekly",
            schedule_day="",
            team_name=None,
            labels=["dependencies"],
            dependabot_config_file=None,
            ghe_api_url="",
        )
        result = get_env_vars(True)
        self.assertEqual(result, expected_result)

    @patch.dict(
        os.environ,
        {
            "ORGANIZATION": "my_organization",
            "GH_TOKEN": "my_token",
            "LABELS": "dependencies,  test ,test2 ",
        },
        clear=True,
    )
    def test_get_env_vars_with_valid_labels_containing_spaces(self):
        """Test valid list of labels with spaces"""
        expected_result = EvergreenConfig(
            organization="my_organization",
            repository_list=[],
            search_query="",
            gh_app_id=None,
            gh_app_installation_id=None,
            gh_app_private_key_bytes=b"",
            gh_app_enterprise_only=False,
            token="my_token",
            ghe="",
            exempt_repositories_list=[],
            follow_up_type="pull",
            title="Enable Dependabot",
            body=(
                "Dependabot could be enabled for this repository. "
                "Please enable it by merging this pull request "
                "so that we can keep our dependencies up to date and secure."
            ),
            created_after_date="",
            dry_run=False,
            commit_message="Create/Update dependabot.yaml",
            project_id=None,
            group_dependencies=False,
            filter_visibility=["internal", "private", "public"],
            batch_size=None,
            enable_security_updates=True,
            exempt_ecosystems=[],
            update_existing=False,
            repo_specific_exemptions={},
            schedule="weekly",
            schedule_day="",
            team_name=None,
            labels=["dependencies", "test", "test2"],
            dependabot_config_file=None,
            ghe_api_url="",
        )
        result = get_env_vars(True)
        self.assertEqual(result, expected_result)

    @patch.dict(
        os.environ,
        {
            "ORGANIZATION": "my_organization",
            "GH_TOKEN": "test",
            "COMMIT_MESSAGE": "".join(
                random.choices(string.ascii_letters, k=MAX_COMMIT_MESSAGE_LENGTH + 1)
            ),
        },
        clear=True,
    )
    def test_get_env_vars_commit_message_too_long(self):
        """Test that an error is raised when the COMMIT_MESSAGE env variable has more than MAX_COMMIT_MESSAGE_LENGTH characters"""
        with self.assertRaises(ValueError) as context_manager:
            get_env_vars(True)
        the_exception = context_manager.exception
        self.assertEqual(
            str(the_exception),
            "COMMIT_MESSAGE environment variable is too long",
        )

    @patch.dict(
        os.environ,
        {
            "ORGANIZATION": "my_organization",
            "GH_TOKEN": "test",
            "BODY": "".join(
                random.choices(string.ascii_letters, k=MAX_BODY_LENGTH + 1)
            ),
        },
        clear=True,
    )
    def test_get_env_vars_pr_body_too_long(self):
        """Test that an error is raised when the BODY env variable has more than MAX_BODY_LENGTH characters"""
        with self.assertRaises(ValueError) as context_manager:
            get_env_vars(True)
        the_exception = context_manager.exception
        self.assertEqual(
            str(the_exception),
            "BODY environment variable is too long",
        )

    @patch.dict(
        os.environ,
        {
            "ORGANIZATION": "my_organization",
            "GH_TOKEN": "my_token",
            "TITLE": "".join(
                random.choices(string.ascii_letters, k=MAX_TITLE_LENGTH + 1)
            ),
        },
        clear=True,
    )
    def test_get_env_vars_with_long_title(self):
        """Test incorrect type error, should be issue or pull"""
        with self.assertRaises(ValueError) as context_manager:
            get_env_vars(True)
        the_exception = context_manager.exception
        self.assertEqual(
            str(the_exception),
            "TITLE environment variable is too long",
        )

    @patch.dict(
        os.environ,
        {
            "ORGANIZATION": "my_organization",
            "GH_TOKEN": "my_token",
            "PROJECT_ID": "project_name",
        },
        clear=True,
    )
    def test_get_env_vars_project_id_not_a_number(self):
        """Test incorrect type error, should be issue or pull"""
        with self.assertRaises(ValueError) as context_manager:
            get_env_vars(True)
        the_exception = context_manager.exception
        self.assertEqual(
            str(the_exception),
            "PROJECT_ID environment variable is not numeric",
        )

    @patch.dict(
        os.environ,
        {
            "ORGANIZATION": "my_organization",
            "GH_TOKEN": "my_token",
            "SCHEDULE": "weekly",
            "DEPENDABOT_CONFIG_FILE": "config.yaml",
        },
        clear=True,
    )
    def test_get_env_vars_with_dependabot_config_file_set_but_not_found(self):
        """Test that no dependabot file configuration is present and the DEPENDABOT_CONFIG_FILE is set"""
        with self.assertRaises(ValueError) as context_manager:
            get_env_vars(True)
        the_exception = context_manager.exception
        self.assertEqual(
            str(the_exception),
            "No dependabot extra configuration found. Please create one in config.yaml",
        )

    @patch.dict(
        os.environ,
        {
            "ORGANIZATION": "my_organization",
            "GH_TOKEN": "my_token",
            "GH_ENTERPRISE_URL": "https://github.example.com",
            "GH_ENTERPRISE_API_URL": "https://api.example.ghe.com",
        },
        clear=True,
    )
    def test_get_env_vars_with_ghe_api_url(self):
        """Test that GH_ENTERPRISE_API_URL is correctly read when GH_ENTERPRISE_URL is also set"""
        expected_result = EvergreenConfig(
            organization="my_organization",
            repository_list=[],
            search_query="",
            gh_app_id=None,
            gh_app_installation_id=None,
            gh_app_private_key_bytes=b"",
            gh_app_enterprise_only=False,
            token="my_token",
            ghe="https://github.example.com",
            exempt_repositories_list=[],
            follow_up_type="pull",
            title="Enable Dependabot",
            body=(
                "Dependabot could be enabled for this repository. "
                "Please enable it by merging this pull request "
                "so that we can keep our dependencies up to date and secure."
            ),
            created_after_date="",
            dry_run=False,
            commit_message="Create/Update dependabot.yaml",
            project_id=None,
            group_dependencies=False,
            filter_visibility=["internal", "private", "public"],
            batch_size=None,
            enable_security_updates=True,
            exempt_ecosystems=[],
            update_existing=False,
            repo_specific_exemptions={},
            schedule="weekly",
            schedule_day="",
            team_name=None,
            labels=[],
            dependabot_config_file=None,
            ghe_api_url="https://api.example.ghe.com",
        )
        result = get_env_vars(True)
        self.assertEqual(result, expected_result)

    @patch.dict(
        os.environ,
        {
            "ORGANIZATION": "my_organization",
            "GH_TOKEN": "my_token",
            "GH_ENTERPRISE_URL": "https://github.example.com",
            "GH_ENTERPRISE_API_URL": "  https://api.example.ghe.com/  ",
        },
        clear=True,
    )
    def test_get_env_vars_with_ghe_api_url_strips_whitespace_and_trailing_slash(self):
        """Test that GH_ENTERPRISE_API_URL is stripped of whitespace and trailing slashes"""
        result = get_env_vars(True)
        self.assertEqual(result.ghe_api_url, "https://api.example.ghe.com")

    @patch.dict(
        os.environ,
        {
            "ORGANIZATION": "my_organization",
            "GH_TOKEN": "my_token",
            "GH_ENTERPRISE_API_URL": "https://api.example.ghe.com",
        },
        clear=True,
    )
    def test_get_env_vars_with_ghe_api_url_without_ghe_url(self):
        """Test that GH_ENTERPRISE_API_URL without GH_ENTERPRISE_URL raises ValueError"""
        with self.assertRaises(ValueError) as context_manager:
            get_env_vars(True)
        the_exception = context_manager.exception
        self.assertEqual(
            str(the_exception),
            "GH_ENTERPRISE_API_URL requires GH_ENTERPRISE_URL to also be set",
        )


class TestGetApiEndpoint(unittest.TestCase):
    """Test the get_api_endpoint helper function"""

    def test_returns_ghe_api_url_when_set(self):
        """Test that ghe_api_url takes precedence"""
        result = get_api_endpoint(
            "https://github.example.com", "https://api.example.ghe.com"
        )
        self.assertEqual(result, "https://api.example.ghe.com")

    def test_strips_trailing_slash_from_ghe_api_url(self):
        """Test that trailing slashes are stripped from ghe_api_url"""
        result = get_api_endpoint(
            "https://github.example.com", "https://api.example.ghe.com/"
        )
        self.assertEqual(result, "https://api.example.ghe.com")

    def test_returns_ghe_with_api_v3_when_no_api_url(self):
        """Test the traditional GHE endpoint construction"""
        result = get_api_endpoint("https://github.example.com", "")
        self.assertEqual(result, "https://github.example.com/api/v3")

    def test_returns_github_com_when_no_ghe(self):
        """Test the default github.com endpoint"""
        result = get_api_endpoint("", "")
        self.assertEqual(result, "https://api.github.com")

    def test_strips_trailing_slash_from_ghe(self):
        """Test that trailing slashes on ghe don't produce double slashes"""
        result = get_api_endpoint("https://github.example.com/", "")
        self.assertEqual(result, "https://github.example.com/api/v3")


if __name__ == "__main__":
    unittest.main()
