"""Test the evergreen.py module."""

import unittest
import uuid
from unittest.mock import MagicMock, patch

import github3
import requests
from evergreen import (
    append_to_github_summary,
    check_existing_config,
    check_pending_issues_for_duplicates,
    check_pending_pulls_for_duplicates,
    commit_changes,
    enable_dependabot_security_updates,
    get_global_issue_id,
    get_global_pr_id,
    get_global_project_id,
    get_repos_iterator,
    is_dependabot_security_updates_enabled,
    is_repo_created_date_before,
    link_item_to_project,
)


class TestDependabotSecurityUpdates(unittest.TestCase):
    """Test the Dependabot security updates functions in evergreen.py"""

    def test_is_dependabot_security_updates_enabled(self):
        """
        Test the is_dependabot_security_updates_enabled function.

        This test checks if the is_dependabot_security_updates_enabled function correctly
        detects if Dependabot security updates are enabled.

        It mocks the requests.get method to simulate different scenarios.
        """
        owner = "my_owner"
        repo = "my_repo"
        access_token = "my_access_token"
        ghe = ""

        expected_url = (
            f"https://api.github.com/repos/{owner}/{repo}/automated-security-fixes"
        )
        expected_headers = {
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/vnd.github.london-preview+json",
        }
        expected_response = {"enabled": True}

        with patch("requests.get") as mock_get:
            mock_get.return_value.status_code = 200
            mock_get.return_value.json.return_value = expected_response

            result = is_dependabot_security_updates_enabled(
                ghe, "", owner, repo, access_token
            )

            mock_get.assert_called_once_with(
                expected_url, headers=expected_headers, timeout=20
            )
            self.assertTrue(result)

    def test_is_dependabot_security_updates_disabled(self):
        """
        Test the is_dependabot_security_updates_enabled function when security updates are disabled.

        This test checks if the is_dependabot_security_updates_enabled function correctly
        detects if Dependabot security updates are disabled.

        It mocks the requests.get method to simulate different scenarios.
        """
        owner = "my_owner"
        repo = "my_repo"
        access_token = "my_access_token"
        ghe = ""

        expected_url = (
            f"https://api.github.com/repos/{owner}/{repo}/automated-security-fixes"
        )
        expected_headers = {
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/vnd.github.london-preview+json",
        }

        with patch("requests.get") as mock_get:
            mock_get.return_value.status_code = 200
            mock_get.return_value.json.return_value = {"enabled": False}

            result = is_dependabot_security_updates_enabled(
                ghe, "", owner, repo, access_token
            )

            mock_get.assert_called_once_with(
                expected_url, headers=expected_headers, timeout=20
            )
            self.assertFalse(result)

    def test_is_dependabot_security_updates_not_found(self):
        """
        Test the is_dependabot_security_updates_enabled function when the endpoint is not found.

        This test checks if the is_dependabot_security_updates_enabled function correctly
        handles the case when the endpoint is not found.

        It mocks the requests.get method to simulate different scenarios.
        """
        owner = "my_owner"
        repo = "my_repo"
        access_token = "my_access_token"
        ghe = ""

        expected_url = (
            f"https://api.github.com/repos/{owner}/{repo}/automated-security-fixes"
        )
        expected_headers = {
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/vnd.github.london-preview+json",
        }

        with patch("requests.get") as mock_get:
            mock_get.return_value.status_code = 404

            result = is_dependabot_security_updates_enabled(
                ghe, "", owner, repo, access_token
            )

            mock_get.assert_called_once_with(
                expected_url, headers=expected_headers, timeout=20
            )
            self.assertFalse(result)

    def test_enable_dependabot_security_updates(self):
        """
        Test the enable_dependabot_security_updates function.

        This test checks if the enable_dependabot_security_updates function successfully enables
        Dependabot security updates.

        It mocks the requests.put method to simulate different scenarios.
        """
        owner = "my_owner"
        repo = "my_repo"
        access_token = "my_access_token"
        ghe = ""

        expected_url = (
            f"https://api.github.com/repos/{owner}/{repo}/automated-security-fixes"
        )
        expected_headers = {
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/vnd.github.london-preview+json",
        }

        with patch("requests.put") as mock_put:
            mock_put.return_value.status_code = 204

            with patch("builtins.print") as mock_print:
                enable_dependabot_security_updates(ghe, "", owner, repo, access_token)

                mock_put.assert_called_once_with(
                    expected_url, headers=expected_headers, timeout=20
                )
                mock_print.assert_called_once_with(
                    "\tDependabot security updates enabled successfully."
                )

    def test_enable_dependabot_security_updates_failed(self):
        """
        Test the enable_dependabot_security_updates function when enabling fails.

        This test checks if the enable_dependabot_security_updates function handles the case
        when enabling Dependabot security updates fails.

        It mocks the requests.put method to simulate different scenarios.
        """
        owner = "my_owner"
        repo = "my_repo"
        access_token = "my_access_token"
        ghe = ""

        expected_url = (
            f"https://api.github.com/repos/{owner}/{repo}/automated-security-fixes"
        )
        expected_headers = {
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/vnd.github.london-preview+json",
        }

        with patch("requests.put") as mock_put:
            mock_put.return_value.status_code = 500

            with patch("builtins.print") as mock_print:
                enable_dependabot_security_updates(ghe, "", owner, repo, access_token)

                mock_put.assert_called_once_with(
                    expected_url, headers=expected_headers, timeout=20
                )
                mock_print.assert_called_once_with(
                    "\tFailed to enable Dependabot security updates."
                )


class TestCommitChanges(unittest.TestCase):
    """Test the commit_changes function in evergreen.py"""

    @patch("uuid.uuid4")
    def test_commit_changes(self, mock_uuid):
        """Test the commit_changes function."""
        mock_uuid.return_value = uuid.UUID(
            "12345678123456781234567812345678"
        )  # Mock UUID generation
        mock_repo = MagicMock()  # Mock repo object
        mock_repo.default_branch = "main"
        mock_repo.ref.return_value.object.sha = "abc123"  # Mock SHA for latest commit
        mock_repo.create_ref.return_value = True
        mock_repo.create_file.return_value = True
        mock_repo.create_pull.return_value = "MockPullRequest"
        dependabot_file_name = ".github/dependabot.yml"

        title = "Test Title"
        body = "Test Body"
        dependabot_file = 'dependencies:\n  - package_manager: "python"\n    directory: "/"\n    update_schedule: "live"'
        branch_name = "dependabot-12345678-1234-5678-1234-567812345678"
        commit_message = "Create " + dependabot_file_name
        result = commit_changes(
            title,
            body,
            mock_repo,
            dependabot_file,
            commit_message,
            dependabot_file_name,
        )

        # Assert that the methods were called with the correct arguments
        mock_repo.create_ref.assert_called_once_with(
            f"refs/heads/{branch_name}", "abc123"
        )
        mock_repo.create_file.assert_called_once_with(
            path=dependabot_file_name,
            message=commit_message,
            content=dependabot_file.encode(),
            branch=branch_name,
        )
        mock_repo.create_pull.assert_called_once_with(
            title=title,
            body=body,
            head=branch_name,
            base="main",
        )

        # Assert that the function returned the expected result
        self.assertEqual(result, "MockPullRequest")


class TestCheckPendingPullsForDuplicates(unittest.TestCase):
    """Test the check_pending_pulls_for_duplicates function."""

    def test_check_pending_pulls_for_duplicates_no_duplicates(self):
        """Test the check_pending_pulls_for_duplicates function where there are no duplicates to be found."""
        mock_repo = MagicMock()  # Mock repo object
        mock_pull_request = MagicMock()
        mock_pull_request.title = "not-dependabot-branch"
        mock_repo.pull_requests.return_value = [mock_pull_request]

        result = check_pending_pulls_for_duplicates("dependabot-branch", mock_repo)

        # Assert that the function returned the expected result
        self.assertFalse(result)

    def test_check_pending_pulls_for_duplicates_with_duplicates(self):
        """Test the check_pending_pulls_for_duplicates function where there are duplicates to be found."""
        mock_repo = MagicMock()  # Mock repo object
        mock_pull_request = MagicMock()
        mock_pull_request.title = "dependabot-branch"
        mock_repo.pull_requests.return_value = [mock_pull_request]

        result = check_pending_pulls_for_duplicates(mock_pull_request.title, mock_repo)

        # Assert that the function returned the expected result
        self.assertTrue(result)


class TestCheckPendingIssuesForDuplicates(unittest.TestCase):
    """Test the check_pending_Issues_for_duplicates function."""

    def test_check_pending_issues_for_duplicates_no_duplicates(self):
        """Test the check_pending_Issues_for_duplicates function where there are no duplicates to be found."""
        mock_issue = MagicMock()
        mock_issue.title = "Other Issue"
        mock_issue.issues.return_value = [mock_issue]

        result = check_pending_issues_for_duplicates("Enable Dependabot", mock_issue)

        mock_issue.issues.assert_called_once_with(state="open")

        # Assert that the function returned the expected result
        self.assertFalse(result)

    def test_check_pending_issues_for_duplicates_with_duplicates(self):
        """Test the check_pending_issues_for_duplicates function where there are duplicates to be found."""
        mock_issue = MagicMock()
        mock_issue.title = "Enable Dependabot"
        mock_issue.issues.return_value = [mock_issue]

        result = check_pending_issues_for_duplicates("Enable Dependabot", mock_issue)

        mock_issue.issues.assert_called_once_with(state="open")

        # Assert that the function returned the expected result
        self.assertTrue(result)


class TestGetReposIterator(unittest.TestCase):
    """Test the get_repos_iterator function in evergreen.py"""

    @patch("github3.login")
    def test_get_repos_iterator_with_organization(self, mock_github):
        """Test the get_repos_iterator function with an organization"""
        organization = "my_organization"
        repository_list = []
        search_query = ""
        github_connection = mock_github.return_value

        mock_organization = MagicMock()
        mock_repositories = MagicMock()
        mock_organization.repositories.return_value = mock_repositories
        github_connection.organization.return_value = mock_organization

        result = get_repos_iterator(
            organization, None, repository_list, search_query, github_connection
        )

        # Assert that the organization method was called with the correct argument
        github_connection.organization.assert_called_once_with(organization)

        # Assert that the repositories method was called on the organization object
        mock_organization.repositories.assert_called_once()

        # Assert that the function returned the expected result
        self.assertEqual(result, mock_repositories)

    @patch("github3.login")
    def test_get_repos_iterator_with_repository_list(self, mock_github):
        """Test the get_repos_iterator function with a repository list"""
        organization = None
        repository_list = ["org/repo1", "org/repo2"]
        search_query = ""
        github_connection = mock_github.return_value

        mock_repository = MagicMock()
        mock_repository_list = [mock_repository, mock_repository]
        github_connection.repository.side_effect = mock_repository_list

        result = get_repos_iterator(
            organization, None, repository_list, search_query, github_connection
        )

        # Assert that the repository method was called with the correct arguments for each repository in the list
        expected_calls = [
            unittest.mock.call("org", "repo1"),
            unittest.mock.call("org", "repo2"),
        ]
        github_connection.repository.assert_has_calls(expected_calls)

        # Assert that the function returned the expected result
        self.assertEqual(result, mock_repository_list)

    @patch("github3.login")
    def test_get_repos_iterator_with_team(self, mock_github):
        """Test the get_repos_iterator function with a team"""
        organization = "my_organization"
        repository_list = []
        team_name = "my_team"
        search_query = ""
        github_connection = mock_github.return_value

        mock_team_repositories = MagicMock()
        github_connection.organization.return_value.team_by_name.return_value.repositories.return_value = (
            mock_team_repositories
        )

        result = get_repos_iterator(
            organization,
            team_name,
            repository_list,
            search_query,
            github_connection,
        )

        # Assert that the organization method was called with the correct argument
        github_connection.organization.assert_called_once_with(organization)

        # Assert that the team_by_name method was called on the organization object
        github_connection.organization.return_value.team_by_name.assert_called_once_with(
            team_name
        )

        # Assert that the repositories method was called on the team object
        github_connection.organization.return_value.team_by_name.return_value.repositories.assert_called_once()

        # Assert that the function returned the expected result
        self.assertEqual(result, mock_team_repositories)

    @patch("github3.login")
    def test_get_repos_iterator_with_search_query(self, mock_github):
        """Test the get_repos_iterator function with a search query"""
        organization = "my_organization"
        repository_list = []
        team_name = None
        search_query = "org:my-org is:repository archived:false"
        github_connection = mock_github.return_value
        repo1 = MagicMock()
        repo2 = MagicMock()

        # Mock the search_repositories method to return an iterator of repositories
        github_connection.search_repositories.return_value = [repo1, repo2]

        get_repos_iterator(
            organization,
            team_name,
            repository_list,
            search_query,
            github_connection,
        )

        # Assert that the search_repositories method was called with the correct argument
        github_connection.search_repositories.assert_called_with(search_query)


class TestGetGlobalProjectId(unittest.TestCase):
    """Test the get_global_project_id function in evergreen.py"""

    @patch("requests.post")
    def test_get_global_project_id_success(self, mock_post):
        """Test the get_global_project_id function when the request is successful."""
        token = "my_token"
        organization = "my_organization"
        number = 123
        ghe = ""

        expected_url = "https://api.github.com/graphql"
        expected_headers = {"Authorization": f"Bearer {token}"}
        expected_data = {
            "query": f'query{{organization(login: "{organization}") {{projectV2(number: {number}){{id}}}}}}'
        }
        expected_response = {
            "data": {"organization": {"projectV2": {"id": "my_project_id"}}}
        }

        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = expected_response

        result = get_global_project_id(ghe, "", token, organization, number)

        mock_post.assert_called_once_with(
            expected_url, headers=expected_headers, json=expected_data, timeout=20
        )
        self.assertEqual(result, "my_project_id")

    @patch("requests.post")
    def test_get_global_project_id_request_failed(self, mock_post):
        """Test the get_global_project_id function when the request fails."""
        token = "my_token"
        organization = "my_organization"
        number = 123
        ghe = ""

        expected_url = "https://api.github.com/graphql"
        expected_headers = {"Authorization": f"Bearer {token}"}
        expected_data = {
            "query": f'query{{organization(login: "{organization}") {{projectV2(number: {number}){{id}}}}}}'
        }

        mock_post.side_effect = requests.exceptions.RequestException("Request failed")

        with patch("builtins.print") as mock_print:
            result = get_global_project_id(ghe, "", token, organization, number)

            mock_post.assert_called_once_with(
                expected_url, headers=expected_headers, json=expected_data, timeout=20
            )
            mock_print.assert_called_once_with("Request failed: Request failed")
            self.assertIsNone(result)

    @patch("requests.post")
    def test_get_global_project_id_parse_response_failed(self, mock_post):
        """Test the get_global_project_id function when parsing the response fails."""
        token = "my_token"
        organization = "my_organization"
        number = 123
        ghe = ""

        expected_url = "https://api.github.com/graphql"
        expected_headers = {"Authorization": f"Bearer {token}"}
        expected_data = {
            "query": f'query{{organization(login: "{organization}") {{projectV2(number: {number}){{id}}}}}}'
        }
        expected_response = {"data": {"organization": {"projectV2": {}}}}

        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = expected_response

        with patch("builtins.print") as mock_print:
            result = get_global_project_id(ghe, "", token, organization, number)

            mock_post.assert_called_once_with(
                expected_url, headers=expected_headers, json=expected_data, timeout=20
            )
            mock_print.assert_called_once_with("Failed to parse response: 'id'")
            self.assertIsNone(result)


class TestGetGlobalIssueId(unittest.TestCase):
    """Test the get_global_issue_id function in evergreen.py"""

    @patch("requests.post")
    def test_get_global_issue_id_success(self, mock_post):
        """Test the get_global_issue_id function for a successful request"""
        token = "my_token"
        organization = "my_organization"
        repository = "my_repository"
        issue_number = 123
        ghe = ""

        expected_response = {"data": {"repository": {"issue": {"id": "1234567890"}}}}

        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = expected_response

        result = get_global_issue_id(
            ghe, "", token, organization, repository, issue_number
        )

        mock_post.assert_called_once()
        self.assertEqual(result, "1234567890")

    @patch("requests.post")
    def test_get_global_issue_id_request_failed(self, mock_post):
        """Test the get_global_issue_id function when the request fails"""
        token = "my_token"
        organization = "my_organization"
        repository = "my_repository"
        issue_number = 123
        ghe = ""

        mock_post.side_effect = requests.exceptions.RequestException("Request failed")

        result = get_global_issue_id(
            ghe, "", token, organization, repository, issue_number
        )

        mock_post.assert_called_once()
        self.assertIsNone(result)

    @patch("requests.post")
    def test_get_global_issue_id_parse_response_failed(self, mock_post):
        """Test the get_global_issue_id function when parsing the response fails"""
        token = "my_token"
        organization = "my_organization"
        repository = "my_repository"
        issue_number = 123
        ghe = ""

        expected_response = {"data": {"repository": {"issue": {}}}}

        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = expected_response

        result = get_global_issue_id(
            ghe, "", token, organization, repository, issue_number
        )

        mock_post.assert_called_once()
        self.assertIsNone(result)


class TestGetGlobalPullRequestID(unittest.TestCase):
    """Test the get_global_pr_id function in evergreen.py"""

    @patch("requests.post")
    def test_get_global_pr_id_success(self, mock_post):
        """Test the get_global_pr_id function when the request is successful."""
        # Mock the response from requests.post
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {
            "data": {"repository": {"pullRequest": {"id": "test_id"}}}
        }
        mock_post.return_value = mock_response

        # Call the function with test data
        result = get_global_pr_id("", "", "test_token", "test_org", "test_repo", 1)

        # Check that the result is as expected
        self.assertEqual(result, "test_id")

    @patch("requests.post")
    def test_get_global_pr_id_request_exception(self, mock_post):
        """Test the get_global_pr_id function when the request fails."""
        # Mock requests.post to raise a RequestException
        mock_post.side_effect = requests.exceptions.RequestException

        # Call the function with test data
        result = get_global_pr_id("", "", "test_token", "test_org", "test_repo", 1)

        # Check that the result is None
        self.assertIsNone(result)

    @patch("requests.post")
    def test_get_global_pr_id_key_error(self, mock_post):
        """Test the get_global_pr_id function when the response cannot be parsed."""
        # Mock the response from requests.post
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {}
        mock_post.return_value = mock_response

        # Call the function with test data
        result = get_global_pr_id("", "", "test_token", "test_org", "test_repo", 1)

        # Check that the result is None
        self.assertIsNone(result)


class TestLinkItemToProject(unittest.TestCase):
    """Test the link_item_to_project function in evergreen.py"""

    @patch("requests.post")
    def test_link_item_to_project_success(self, mock_post):
        """Test linking an item to a project successfully."""
        token = "my_token"
        project_id = "my_project_id"
        item_id = "my_item_id"
        ghe = ""

        expected_url = "https://api.github.com/graphql"
        expected_headers = {"Authorization": f"Bearer {token}"}
        expected_data = {
            "query": f'mutation {{addProjectV2ItemById(input: {{projectId: "{project_id}", contentId: "{item_id}"}}) {{item {{id}}}}}}'
        }

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response

        result = link_item_to_project(ghe, "", token, project_id, item_id)

        mock_post.assert_called_once_with(
            expected_url, headers=expected_headers, json=expected_data, timeout=20
        )
        mock_response.raise_for_status.assert_called_once()

        # Assert that the function returned None
        self.assertIsNotNone(result)

    @patch("requests.post")
    def test_link_item_to_project_request_exception(self, mock_post):
        """Test handling a requests exception when linking an item to a project."""
        token = "my_token"
        project_id = "my_project_id"
        item_id = "my_item_id"
        ghe = ""

        expected_url = "https://api.github.com/graphql"
        expected_headers = {"Authorization": f"Bearer {token}"}
        expected_data = {
            "query": f'mutation {{addProjectV2ItemById(input: {{projectId: "{project_id}", contentId: "{item_id}"}}) {{item {{id}}}}}}'
        }

        mock_post.side_effect = requests.exceptions.RequestException("Request failed")

        with patch("builtins.print") as mock_print:
            result = link_item_to_project(ghe, "", token, project_id, item_id)

            mock_post.assert_called_once_with(
                expected_url, headers=expected_headers, json=expected_data, timeout=20
            )
            mock_print.assert_called_once_with("Request failed: Request failed")

            # Assert that the function returned None
            self.assertIsNone(result)


class TestIsRepoCreateDateBeforeCreatedAfterDate(unittest.TestCase):
    """Test the is_repo_create_date_before_created_after_date function in evergreen.py"""

    def test_is_repo_create_date_before_created_after_date(self):
        """Test the repo.created_at date is before created_after_date and has timezone."""
        repo_created_at = "2020-01-01T05:00:00Z"
        created_after_date = "2021-01-01"

        result = is_repo_created_date_before(repo_created_at, created_after_date)

        self.assertTrue(result)

    def test_is_repo_create_date_is_after_created_after_date(self):
        """Test the repo.created_at date is after created_after_date and has timezone."""
        repo_created_at = "2022-01-01T05:00:00Z"
        created_after_date = "2021-01-01"

        result = is_repo_created_date_before(repo_created_at, created_after_date)

        self.assertFalse(result)

    def test_is_repo_created_date_has_no_time_zone(self):
        """Test the repo.created_at date is before created_after_date with no timezone."""
        repo_created_at = "2020-01-01"
        created_after_date = "2021-01-01"

        result = is_repo_created_date_before(repo_created_at, created_after_date)

        self.assertTrue(result)

    def test_is_created_after_date_is_empty_string(self):
        """Test the repo.created_at date is after created_after_date."""
        repo_created_at = "2020-01-01"
        created_after_date = ""

        result = is_repo_created_date_before(repo_created_at, created_after_date)

        self.assertFalse(result)

    def test_is_repo_created_date_is_before_created_after_date_without_timezone_again(
        self,
    ):
        """Test the repo.created_at date is before created_after_date without timezone again."""
        repo_created_at = "2018-01-01"
        created_after_date = "2020-01-01"

        result = is_repo_created_date_before(repo_created_at, created_after_date)

        self.assertTrue(result)

    def test_is_repo_created_date_and_created_after_date_is_not_a_date(self):
        """Test the repo.created_at date and the created_after_date argument is not a date."""
        repo_created_at = "2018-01-01"
        created_after_date = "Not a date"

        with self.assertRaises(ValueError):
            is_repo_created_date_before(repo_created_at, created_after_date)


class TestCheckExistingConfig(unittest.TestCase):
    """
    Test cases for the check_existing_config function
    """

    def test_check_existing_config_with_existing_config(self):
        """
        Test the case where there is an existing configuration
        """
        mock_repo = MagicMock()
        filename = "dependabot.yaml"
        mock_repo.file_contents.return_value.size = 5

        result = check_existing_config(mock_repo, filename)

        self.assertIsNotNone(result)

    def test_check_existing_config_without_existing_config(self):
        """
        Test the case where there is no existing configuration
        """
        mock_repo = MagicMock()
        mock_response = MagicMock()
        mock_repo.file_contents.side_effect = github3.exceptions.NotFoundError(
            mock_response
        )

        result = check_existing_config(mock_repo, "dependabot.yml")

        self.assertIsNone(result)


class TestAppendToGithubSummary(unittest.TestCase):
    """Test the append_to_github_summary function in evergreen.py"""

    @patch("builtins.open", new_callable=unittest.mock.mock_open)
    def test_append_to_github_summary_with_file(self, mock_file):
        """Test that content is appended to the specified summary file."""
        content = "Test summary content"
        summary_file = "summary.md"

        append_to_github_summary(content, summary_file)

        mock_file.assert_called_once_with(summary_file, "a", encoding="utf-8")
        mock_file().write.assert_called_once_with(content + "\n")

    @patch("builtins.open", new_callable=unittest.mock.mock_open)
    def test_append_to_github_summary_without_summary_file(self, mock_file):
        """Test that content is not written when summary_file is None or empty."""
        content = "Test summary content"
        summary_file = ""

        append_to_github_summary(content, summary_file)

        mock_file.assert_not_called()

    @patch("builtins.open", new_callable=unittest.mock.mock_open)
    def test_append_to_github_summary_with_default_file(self, mock_file):
        """Test that content is appended to the default summary file when summary_file is not provided."""
        content = "Test summary content"

        append_to_github_summary(content)

        mock_file.assert_called_once_with("summary.md", "a", encoding="utf-8")
        mock_file().write.assert_called_once_with(content + "\n")


class TestCustomEnterpriseApiUrl(unittest.TestCase):
    """Test that functions use the custom GH_ENTERPRISE_API_URL when provided."""

    @patch("requests.get")
    def test_is_dependabot_security_updates_enabled_with_ghe_api_url(self, mock_get):
        """Test that the custom API URL is used instead of constructing from GHE URL."""
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {"enabled": True}

        result = is_dependabot_security_updates_enabled(
            "https://github.example.com",
            "https://api.example.ghe.com",
            "owner",
            "repo",
            "token",
        )

        mock_get.assert_called_once_with(
            "https://api.example.ghe.com/repos/owner/repo/automated-security-fixes",
            headers={
                "Authorization": "Bearer token",
                "Accept": "application/vnd.github.london-preview+json",
            },
            timeout=20,
        )
        self.assertTrue(result)

    @patch("requests.put")
    def test_enable_dependabot_security_updates_with_ghe_api_url(self, mock_put):
        """Test that the custom API URL is used for enabling security updates."""
        mock_put.return_value.status_code = 204

        with patch("builtins.print"):
            enable_dependabot_security_updates(
                "https://github.example.com",
                "https://api.example.ghe.com",
                "owner",
                "repo",
                "token",
            )

        mock_put.assert_called_once_with(
            "https://api.example.ghe.com/repos/owner/repo/automated-security-fixes",
            headers={
                "Authorization": "Bearer token",
                "Accept": "application/vnd.github.london-preview+json",
            },
            timeout=20,
        )

    @patch("requests.post")
    def test_get_global_project_id_with_ghe_api_url(self, mock_post):
        """Test that the custom API URL is used for GraphQL queries."""
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {
            "data": {"organization": {"projectV2": {"id": "proj_123"}}}
        }

        result = get_global_project_id(
            "https://github.example.com",
            "https://api.example.ghe.com",
            "token",
            "org",
            1,
        )

        mock_post.assert_called_once()
        call_url = mock_post.call_args[0][0]
        self.assertEqual(call_url, "https://api.example.ghe.com/graphql")
        self.assertEqual(result, "proj_123")

    @patch("requests.post")
    def test_link_item_to_project_with_ghe_api_url(self, mock_post):
        """Test that the custom API URL is used for linking items to projects."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response

        result = link_item_to_project(
            "https://github.example.com",
            "https://api.example.ghe.com",
            "token",
            "proj_123",
            "item_456",
        )

        call_url = mock_post.call_args[0][0]
        self.assertEqual(call_url, "https://api.example.ghe.com/graphql")
        self.assertIsNotNone(result)


if __name__ == "__main__":
    unittest.main()
