"""This file contains the main() and other functions needed to open an issue/PR dependabot is not enabled but could be"""

import io
import sys
import uuid
from datetime import datetime

import auth
import env
import github3
import requests
import ruamel.yaml
from dependabot_file import build_dependabot_file, validate_cooldown_config
from exceptions import OptionalFileNotFoundError, check_optional_file


def main():  # pragma: no cover
    """Run the main program"""

    # Get the environment variables
    (
        organization,
        repository_list,
        search_query,
        gh_app_id,
        gh_app_installation_id,
        gh_app_private_key,
        gh_app_enterprise_only,
        token,
        ghe,
        exempt_repositories_list,
        follow_up_type,
        title,
        body,
        created_after_date,
        dry_run,
        commit_message,
        project_id,
        group_dependencies,
        filter_visibility,
        batch_size,
        enable_security_updates,
        exempt_ecosystems,
        update_existing,
        repo_specific_exemptions,
        schedule,
        schedule_day,
        team_name,
        labels,
        dependabot_config_file,
    ) = env.get_env_vars()

    # Auth to GitHub.com or GHE
    github_connection = auth.auth_to_github(
        token,
        gh_app_id,
        gh_app_installation_id,
        gh_app_private_key,
        ghe,
        gh_app_enterprise_only,
    )

    if not token and gh_app_id and gh_app_installation_id and gh_app_private_key:
        token = auth.get_github_app_installation_token(
            ghe, gh_app_id, gh_app_private_key, gh_app_installation_id
        )

    # Set the project_global_id to None by default
    project_global_id = None

    # If Project ID is set, lookup the global project ID
    if project_id:
        # Check Organization is set as it is required for linking to a project
        if not organization:
            raise ValueError(
                "ORGANIZATION environment variable was not set. Please set it"
            )
        project_global_id = get_global_project_id(ghe, token, organization, project_id)

    # Get the repositories from the organization, team name, or list of repositories
    repos = get_repos_iterator(
        organization, team_name, repository_list, search_query, github_connection
    )

    # Setting up the action summary content
    summary_content = f"""
## 🚀 Job Summary
- **Organization:** {organization}
- **Follow Up Type:** {follow_up_type}
- **Dry Run:** {dry_run}
- **Enable Security Updates:** {enable_security_updates}\n
    """
    # Add optional parameters to the summary
    if project_id:
        project_link = f"https://github.com/orgs/{organization}/projects/{project_id}"
        summary_content += f"- **Project ID:** [{project_id}]({project_link})\n"
    if batch_size:
        summary_content += f"- **Batch Size:** {batch_size}\n"

    # Add the updated repositories table header
    summary_content += (
        "\n\n## 📋 Updated Repositories\n\n"
        "| Repository | 🔒 Security Updates Enabled | 🔄 Follow Up Type | 🔗 Link |\n"
        "| --- | --- | --- | --- |\n"
    )

    # Iterate through the repositories and open an issue/PR if dependabot is not enabled
    count_eligible = 0
    count_prs_created = 0
    for repo in repos:
        # if batch_size is defined, ensure we break if we exceed the number of eligible repos
        if batch_size and count_eligible >= batch_size:
            print(f"Batch size met at {batch_size} eligible repositories.")
            break

        # Check all the things to see if repo is eligible for a pr/issue
        if repo.full_name in exempt_repositories_list:
            print(f"Skipping {repo.full_name} (exempted)")
            continue
        if repo.archived:
            print(f"Skipping {repo.full_name} (archived)")
            continue
        if repo.visibility.lower() not in filter_visibility:
            print(f"Skipping {repo.full_name} (visibility-filtered)")
            continue
        existing_config = None
        filename_list = [".github/dependabot.yaml", ".github/dependabot.yml"]
        dependabot_filename_to_use = filename_list[0]  # Default to the first filename
        for filename in filename_list:
            existing_config = check_existing_config(repo, filename)
            if existing_config:
                dependabot_filename_to_use = filename
                break

        if existing_config and not update_existing:
            print(
                f"Skipping {repo.full_name} (dependabot file already exists and update_existing is False)"
            )
            continue

        if created_after_date and is_repo_created_date_before(
            repo.created_at, created_after_date
        ):
            print(f"Skipping {repo.full_name} (created after filter)")
            continue

        # Check if there is any extra configuration to be added to the dependabot file by checking the DEPENDABOT_CONFIG_FILE env variable
        if dependabot_config_file:
            yaml = ruamel.yaml.YAML()
            yaml.preserve_quotes = True
            # If running locally on a computer the local file takes precedence over the one existent on the repository
            try:
                with open(
                    dependabot_config_file, "r", encoding="utf-8"
                ) as extra_dependabot_config:
                    extra_dependabot_config = yaml.load(extra_dependabot_config)
            except ruamel.yaml.YAMLError as e:
                print(f"YAML indentation error: {e}")
                continue

        else:
            # If no dependabot configuration file is present set the variable empty
            extra_dependabot_config = None

        # Extract cooldown config if present (it's not a registry/ecosystem key)
        cooldown = None
        if extra_dependabot_config and "cooldown" in extra_dependabot_config:
            cooldown = extra_dependabot_config.pop("cooldown")
            try:
                validate_cooldown_config(cooldown)
            except ValueError as e:
                print(f"Invalid cooldown configuration: {e}")
                cooldown = None

        print(f"Checking {repo.full_name} for compatible package managers")
        # Try to detect package managers and build a dependabot file
        dependabot_file = build_dependabot_file(
            repo,
            group_dependencies,
            exempt_ecosystems,
            repo_specific_exemptions,
            existing_config,
            schedule,
            schedule_day,
            labels,
            extra_dependabot_config,
            cooldown,
        )

        yaml = ruamel.yaml.YAML()
        stream = io.StringIO()
        yaml.indent(mapping=2, sequence=4, offset=2)

        # create locally the dependabot file
        with open("dependabot-output.yaml", "w", encoding="utf-8") as yaml_file:
            yaml.dump(dependabot_file, yaml_file)

        if dependabot_file is None:
            print("\tNo (new) compatible package manager found")
            continue

        dependabot_file = yaml.dump(dependabot_file, stream)
        dependabot_file = stream.getvalue()

        # If dry_run is set, just print the dependabot file
        if dry_run:
            if follow_up_type == "issue":
                skip = check_pending_issues_for_duplicates(title, repo)
                if not skip:
                    print("\tEligible for configuring dependabot.")
                    count_eligible += 1
                    print(f"\tConfiguration:\n {dependabot_file}")
            if follow_up_type == "pull":
                # Try to detect if the repo already has an open pull request for dependabot
                skip = check_pending_pulls_for_duplicates(title, repo)
                if not skip:
                    print("\tEligible for configuring dependabot.")
                    count_eligible += 1
                    print(f"\tConfiguration:\n {dependabot_file}")
            continue

        # Get dependabot security updates enabled if possible
        if enable_security_updates:
            if not is_dependabot_security_updates_enabled(
                ghe, repo.owner, repo.name, token
            ):
                enable_dependabot_security_updates(ghe, repo.owner, repo.name, token)

        if follow_up_type == "issue":
            skip = check_pending_issues_for_duplicates(title, repo)
            if not skip:
                count_eligible += 1
                body_issue = f"{body}\n\n```yaml\n# {dependabot_filename_to_use} \n{dependabot_file}\n```"
                issue = repo.create_issue(title, body_issue)
                print(f"\tCreated issue {issue.html_url}")
                summary_content += f"| {repo.full_name} | {'✅' if enable_security_updates else '❌'} | {follow_up_type} | [Link]({issue.html_url}) |\n"
                if project_global_id:
                    issue_id = get_global_issue_id(
                        ghe, token, organization, repo.name, issue.number
                    )
                    link_item_to_project(ghe, token, project_global_id, issue_id)
                    print(f"\tLinked issue to project {project_global_id}")
        else:
            # Try to detect if the repo already has an open pull request for dependabot
            skip = check_pending_pulls_for_duplicates(title, repo)

            # Create a dependabot.yaml file, a branch, and a PR
            if not skip:
                count_eligible += 1
                try:
                    pull = commit_changes(
                        title,
                        body,
                        repo,
                        dependabot_file,
                        commit_message,
                        dependabot_filename_to_use,
                        existing_config,
                    )
                    print(f"\tCreated pull request {pull.html_url}")
                    count_prs_created += 1
                    summary_content += (
                        f"| {repo.full_name} | "
                        f"{'✅' if enable_security_updates else '❌'} | "
                        f"{follow_up_type} | "
                        f"[Link]({pull.html_url}) |\n"
                    )
                    if project_global_id:
                        pr_id = get_global_pr_id(
                            ghe, token, organization, repo.name, pull.number
                        )
                        response = link_item_to_project(
                            ghe, token, project_global_id, pr_id
                        )
                        if response:
                            print(
                                f"\tLinked pull request to project {project_global_id}"
                            )
                except github3.exceptions.NotFoundError:
                    print("\tFailed to create pull request. Check write permissions.")
                    continue

    print(f"Done. {str(count_eligible)} repositories were eligible.")
    print(f"{str(count_prs_created)} pull requests were created.")
    # Append the summary content to the GitHub step summary file
    append_to_github_summary(summary_content)


def is_repo_created_date_before(repo_created_at: str, created_after_date: str):
    """Check if the repository was created before the created_after_date"""
    repo_created_at_date = datetime.fromisoformat(repo_created_at).replace(tzinfo=None)
    return created_after_date and repo_created_at_date < datetime.strptime(
        created_after_date, "%Y-%m-%d"
    )


def is_dependabot_security_updates_enabled(ghe, owner, repo, access_token):
    """
    Check if Dependabot security updates are enabled at the /repos/:owner/:repo/automated-security-fixes endpoint using the requests library
    API: https://docs.github.com/en/rest/repos/repos?apiVersion=2022-11-28#check-if-automated-security-fixes-are-enabled-for-a-repository
    """
    api_endpoint = f"{ghe}/api/v3" if ghe else "https://api.github.com"
    url = f"{api_endpoint}/repos/{owner}/{repo}/automated-security-fixes"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/vnd.github.london-preview+json",
    }

    response = requests.get(url, headers=headers, timeout=20)
    if response.status_code == 200:
        return response.json()["enabled"]
    return False


def check_existing_config(repo, filename):
    """
    Check if a file already exists in the
    repository and return the existing config if it does

    Args:
        repo (github3.repos.repo.Repository): The repository to check
        filename (str): The configuration filename to check

    Returns:
        github3.repos.contents.Contents | None: The existing config if it exists, otherwise None
    """
    existing_config = None
    try:
        existing_config = check_optional_file(repo, filename)
        if existing_config:
            return existing_config
    except OptionalFileNotFoundError:
        # The file does not exist and is not required,
        # so we should continue to the next one rather than raising error or logging
        pass
    return None


def enable_dependabot_security_updates(ghe, owner, repo, access_token):
    """
    Enable Dependabot security updates at the /repos/:owner/:repo/automated-security-fixes endpoint using the requests library
    API: https://docs.github.com/en/rest/repos/repos?apiVersion=2022-11-28#enable-automated-security-fixes
    """
    api_endpoint = f"{ghe}/api/v3" if ghe else "https://api.github.com"
    url = f"{api_endpoint}/repos/{owner}/{repo}/automated-security-fixes"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/vnd.github.london-preview+json",
    }

    response = requests.put(url, headers=headers, timeout=20)
    if response.status_code == 204:
        print("\tDependabot security updates enabled successfully.")
    else:
        print("\tFailed to enable Dependabot security updates.")


def get_repos_iterator(
    organization, team_name, repository_list, search_query, github_connection
):
    """Get the repositories from the organization, team_name, repository_list, or via search query"""
    # Use GitHub search API if REPOSITORY_SEARCH_QUERY is set
    if search_query:
        # Return repositories matching the search query
        repos = []
        # Search results need to be converted to a list of repositories since they are returned as a search iterator
        for repo in github_connection.search_repositories(search_query):
            repos.append(repo.repository)
        return repos

    repos = []
    # Default behavior: list all organization/team repositories or specific repository list
    if organization and not repository_list and not team_name:
        repos = github_connection.organization(organization).repositories()
    elif team_name and organization:
        # Get the repositories from the team
        team = github_connection.organization(organization).team_by_name(team_name)
        if team.repos_count == 0:
            print(f"Team {team_name} has no repositories")
            sys.exit(1)
        repos = team.repositories()
    else:
        # Get the repositories from the repository_list
        for repo in repository_list:
            repos.append(
                github_connection.repository(repo.split("/")[0], repo.split("/")[1])
            )

    return repos


def check_pending_pulls_for_duplicates(title, repo) -> bool:
    """Check if there are any open pull requests for dependabot and return the bool skip"""
    pull_requests = repo.pull_requests(state="open")
    skip = False
    for pull_request in pull_requests:
        if pull_request.title.startswith(title):
            print(f"\tPull request already exists: {pull_request.html_url}")
            skip = True
            break
    return skip


def check_pending_issues_for_duplicates(title, repo) -> bool:
    """Check if there are any open issues for dependabot and return the bool skip"""
    issues = repo.issues(state="open")
    skip = False
    for issue in issues:
        if issue.title.startswith(title):
            print(f"\tIssue already exists: {issue.html_url}")
            skip = True
            break
    return skip


def commit_changes(
    title,
    body,
    repo,
    dependabot_file,
    message,
    dependabot_filename=".github/dependabot.yml",
    existing_config=None,
):
    """Commit the changes to the repo and open a pull request and return the pull request object"""
    default_branch = repo.default_branch
    # Get latest commit sha from default branch
    default_branch_commit = repo.ref("heads/" + default_branch).object.sha
    front_matter = "refs/heads/"
    branch_name = "dependabot-" + str(uuid.uuid4())
    repo.create_ref(front_matter + branch_name, default_branch_commit)
    if existing_config:
        repo.file_contents(dependabot_filename).update(
            message=message,
            content=dependabot_file.encode(),  # Convert to bytes object
            branch=branch_name,
        )
    else:
        repo.create_file(
            path=dependabot_filename,
            message=message,
            content=dependabot_file.encode(),  # Convert to bytes object
            branch=branch_name,
        )

    pull = repo.create_pull(
        title=title, body=body, head=branch_name, base=repo.default_branch
    )
    return pull


def get_global_project_id(ghe, token, organization, number):
    """
    Fetches the project ID from GitHub's GraphQL API.
    API: https://docs.github.com/en/graphql/guides/forming-calls-with-graphql
    """
    api_endpoint = f"{ghe}/api/v3" if ghe else "https://api.github.com"
    url = f"{api_endpoint}/graphql"
    headers = {"Authorization": f"Bearer {token}"}
    data = {
        "query": f'query{{organization(login: "{organization}") {{projectV2(number: {number}){{id}}}}}}'
    }

    try:
        response = requests.post(url, headers=headers, json=data, timeout=20)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return None

    try:
        return response.json()["data"]["organization"]["projectV2"]["id"]
    except KeyError as e:
        print(f"Failed to parse response: {e}")
        return None


def get_global_issue_id(ghe, token, organization, repository, issue_number):
    """
    Fetches the issue ID from GitHub's GraphQL API
    API: https://docs.github.com/en/graphql/guides/forming-calls-with-graphql
    """
    api_endpoint = f"{ghe}/api/v3" if ghe else "https://api.github.com"
    url = f"{api_endpoint}/graphql"
    headers = {"Authorization": f"Bearer {token}"}
    data = {"query": f"""
        query {{
          repository(owner: "{organization}", name: "{repository}") {{
            issue(number: {issue_number}) {{
              id
            }}
          }}
        }}
        """}

    try:
        response = requests.post(url, headers=headers, json=data, timeout=20)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return None

    try:
        return response.json()["data"]["repository"]["issue"]["id"]
    except KeyError as e:
        print(f"Failed to parse response: {e}")
        return None


def get_global_pr_id(ghe, token, organization, repository, pr_number):
    """
    Fetches the pull request ID from GitHub's GraphQL API
    API: https://docs.github.com/en/graphql/guides/forming-calls-with-graphql
    """
    api_endpoint = f"{ghe}/api/v3" if ghe else "https://api.github.com"
    url = f"{api_endpoint}/graphql"
    headers = {"Authorization": f"Bearer {token}"}
    data = {"query": f"""
        query {{
          repository(owner: "{organization}", name: "{repository}") {{
            pullRequest(number: {pr_number}) {{
              id
            }}
          }}
        }}
        """}

    try:
        response = requests.post(url, headers=headers, json=data, timeout=20)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return None

    try:
        return response.json()["data"]["repository"]["pullRequest"]["id"]
    except KeyError as e:
        print(f"Failed to parse response: {e}")
        return None


def link_item_to_project(ghe, token, project_global_id, item_id):
    """
    Links an item (issue or pull request) to a project in GitHub.
    API: https://docs.github.com/en/graphql/guides/forming-calls-with-graphql
    """
    api_endpoint = f"{ghe}/api/v3" if ghe else "https://api.github.com"
    url = f"{api_endpoint}/graphql"
    headers = {"Authorization": f"Bearer {token}"}
    data = {
        "query": f'mutation {{addProjectV2ItemById(input: {{projectId: "{project_global_id}", contentId: "{item_id}"}}) {{item {{id}}}}}}'
    }

    try:
        response = requests.post(url, headers=headers, json=data, timeout=20)
        response.raise_for_status()
        return response
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return None


def append_to_github_summary(content, summary_file="summary.md"):
    """
    Append content to the GitHub step summary file
    """
    if summary_file:
        with open(summary_file, "a", encoding="utf-8") as f:
            f.write(content + "\n")


if __name__ == "__main__":
    main()  # pragma: no cover
