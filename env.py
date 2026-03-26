"""
Sets up the environment variables for the action.
"""

import os
import re
from os.path import dirname, join

from dotenv import load_dotenv

MAX_TITLE_LENGTH = 70
MAX_BODY_LENGTH = 65536
MAX_COMMIT_MESSAGE_LENGTH = 65536

SUPPORTED_PACKAGE_ECOSYSTEMS = [
    "bundler",
    "cargo",
    "composer",
    "devcontainers",
    "docker",
    "github-actions",
    "gomod",
    "gradle",
    "maven",
    "mix",
    "npm",
    "nuget",
    "pip",
    "terraform",
]


def get_bool_env_var(env_var_name: str, default: bool = False) -> bool:
    """Get a boolean environment variable.

    Args:
        env_var_name: The name of the environment variable to retrieve.
        default: The default value to return if the environment variable is not set.

    Returns:
        The value of the environment variable as a boolean.
    """
    ev = os.environ.get(env_var_name, "")
    if ev == "" and default:
        return default
    return ev.strip().lower() == "true"


def get_int_env_var(env_var_name: str) -> int | None:
    """Get an integer environment variable.

    Args:
        env_var_name: The name of the environment variable to retrieve.

    Returns:
        The value of the environment variable as an integer or None.
    """
    env_var = os.environ.get(env_var_name)
    if env_var is None or not env_var.strip():
        return None
    try:
        return int(env_var)
    except ValueError:
        return None


def parse_repo_specific_exemptions(repo_specific_exemptions_str: str) -> dict:
    """Parse the REPO_SPECIFIC_EXEMPTIONS environment variable into a dictionary.

    Args:
        repo_specific_exemptions_str: The REPO_SPECIFIC_EXEMPTIONS environment variable as a string.

    Returns:
        A dictionary where keys are repository names and values are lists of exempt ecosystems.
    """
    exemptions_dict = {}
    if repo_specific_exemptions_str:
        # if repo_specific_exemptions_str doesn't have a ; and : character, it's not valid
        separators = [";", ":"]
        if not all(sep in repo_specific_exemptions_str for sep in separators):
            raise ValueError(
                "REPO_SPECIFIC_EXEMPTIONS environment variable not formatted correctly"
            )
        exemptions_list = repo_specific_exemptions_str.split(";")
        for exemption in exemptions_list:
            if (
                exemption == ""
            ):  # Account for final ; in the repo_specific_exemptions_str
                continue
            repo, ecosystems = exemption.split(":")
            cleaned_ecosystems = []
            for ecosystem in ecosystems.split(","):
                ecosystem = ecosystem.strip().lower()
                if ecosystem not in SUPPORTED_PACKAGE_ECOSYSTEMS:
                    raise ValueError(
                        "REPO_SPECIFIC_EXEMPTIONS environment variable not formatted correctly. Unrecognized package-ecosystem."
                    )
                cleaned_ecosystems.append(ecosystem)
            exemptions_dict[repo.strip()] = cleaned_ecosystems
    return exemptions_dict


def get_env_vars(
    test: bool = False,
) -> tuple[
    str | None,
    list[str],
    str | None,
    int | None,
    int | None,
    bytes,
    bool,
    str,
    str,
    list[str],
    str,
    str,
    str,
    str,
    bool,
    str,
    str | None,
    bool | None,
    list[str] | None,
    int | None,
    bool | None,
    list[str],
    bool | None,
    dict,
    str,
    str,
    str | None,
    list[str],
    str | None,
]:
    """
    Get the environment variables for use in the action.

    Args:
        None

    Returns:
        organization (str): The organization to search for repositories in
        repository_list (list[str]): A list of repositories to search for
        search_query (str): A search query string to filter repositories by
        gh_app_id (int | None): The GitHub App ID to use for authentication
        gh_app_installation_id (int | None): The GitHub App Installation ID to use for authentication
        gh_app_private_key_bytes (bytes): The GitHub App Private Key as bytes to use for authentication
        gh_app_enterprise_only (bool): Set this to true if the GH APP is created on GHE and needs to communicate with GHE api only
        token (str): The GitHub token to use for authentication
        ghe (str): The GitHub Enterprise URL to use for authentication
        exempt_repositories_list (list[str]): A list of repositories to exempt from the action
        follow_up_type (str): The type of follow up to open (issue or pull)
        title (str): The title of the follow up
        body (str): The body of the follow up
        created_after_date (str): The date to filter repositories by
        dry_run (bool): Whether or not to actually open issues/pull requests
        commit_message (str): The commit message of the follow up
        group_dependencies (bool): Whether to group dependencies in the dependabot.yml file
        filter_visibility (list[str]): Run the action only on repositories with the specified listed visibility
        batch_size (int): The max number of repositories in scope
        enable_security_updates (bool): Whether to enable security updates in target repositories
        exempt_ecosystems_list (list[str]): A list of package ecosystems to exempt from the action
        update_existing (bool): Whether to update existing dependabot configuration files
        repo_specific_exemptions (dict): A dictionary of per repository ecosystem exemptions
        schedule (str): The schedule to run the action on
        schedule_day (str): The day of the week to run the action on if schedule is daily
        team_name (str): The team to search for repositories in
        labels (list[str]): A list of labels to be added to dependabot configuration
        dependabot_config_file (str): Dependabot extra configuration file location path
    """

    if not test:  # pragma: no cover
        # Load from .env file if it exists and not testing
        dotenv_path = join(dirname(__file__), ".env")
        load_dotenv(dotenv_path)

    organization = os.getenv("ORGANIZATION")
    repositories_str = os.getenv("REPOSITORY")
    search_query = os.getenv("REPOSITORY_SEARCH_QUERY", "").strip()
    team_name = os.getenv("TEAM_NAME")
    # Either organization, repository, or search_query must be set
    if not organization and not repositories_str and not search_query:
        raise ValueError(
            "ORGANIZATION, REPOSITORY, and REPOSITORY_SEARCH_QUERY environment variables were not set. Please set one"
        )
    # Team name and repository are mutually exclusive
    if repositories_str and team_name:
        raise ValueError(
            "TEAM_NAME environment variable cannot be used with REPOSITORY"
        )

    # Separate repositories_str into a list based on the comma separator
    repositories_list = []
    if repositories_str:
        repositories_list = [
            repository.strip() for repository in repositories_str.split(",")
        ]

    gh_app_id = get_int_env_var("GH_APP_ID")
    gh_app_private_key_bytes = os.environ.get("GH_APP_PRIVATE_KEY", "").encode("utf8")
    gh_app_installation_id = get_int_env_var("GH_APP_INSTALLATION_ID")
    gh_app_enterprise_only = get_bool_env_var("GITHUB_APP_ENTERPRISE_ONLY")

    if gh_app_id and (not gh_app_private_key_bytes or not gh_app_installation_id):
        raise ValueError(
            "GH_APP_ID set and GH_APP_INSTALLATION_ID or GH_APP_PRIVATE_KEY variable not set"
        )

    token = os.getenv("GH_TOKEN", "")
    if (
        not gh_app_id
        and not gh_app_private_key_bytes
        and not gh_app_installation_id
        and not token
    ):
        raise ValueError("GH_TOKEN environment variable not set")

    ghe = os.getenv("GH_ENTERPRISE_URL", default="").strip()

    exempt_repos = os.getenv("EXEMPT_REPOS")
    exempt_repositories_list = []
    if exempt_repos:
        exempt_repositories_list = [
            repository.strip() for repository in exempt_repos.split(",")
        ]

    follow_up_type = os.getenv("TYPE")
    # make sure that follow_up_type is either "issue" or "pull"
    if follow_up_type:
        if follow_up_type not in ("issue", "pull"):
            raise ValueError("TYPE environment variable not 'issue' or 'pull'")
    else:
        follow_up_type = "pull"

    title = os.getenv("TITLE")
    # make sure that title is a string with less than MAX_TITLE_LENGTH characters
    if title:
        if len(title) > MAX_TITLE_LENGTH:
            raise ValueError("TITLE environment variable is too long")
    else:
        title = "Enable Dependabot"

    body = os.getenv("BODY")
    if body and len(body) > MAX_BODY_LENGTH:
        raise ValueError("BODY environment variable is too long")

    if not body:
        default_bodies = {
            "pull": "Dependabot could be enabled for this repository. \
Please enable it by merging this pull request so that we can keep our dependencies up to date and secure.",
            "issue": (
                "Please update the repository to include a Dependabot configuration file.\n"
                "This will ensure our dependencies remain updated and secure.\n"
                "Follow the guidelines in [creating Dependabot configuration files]"
                "(https://docs.github.com/en/code-security/dependabot/dependabot-version-updates/configuration-options-for-the-dependabot.yml-file) "
                "to set it up properly.\n\n"
                "Here's an example of the code:"
            ),
        }
        body = body = default_bodies[follow_up_type]

    commit_message = os.getenv("COMMIT_MESSAGE")
    if commit_message:
        if len(commit_message) > MAX_COMMIT_MESSAGE_LENGTH:
            raise ValueError("COMMIT_MESSAGE environment variable is too long")
    else:
        commit_message = "Create/Update dependabot.yaml"

    created_after_date = os.getenv("CREATED_AFTER_DATE", "")
    is_match = re.match(r"\d{4}-\d{2}-\d{2}", created_after_date)
    if created_after_date and not is_match:
        raise ValueError(
            f"CREATED_AFTER_DATE '{created_after_date}' environment variable not in YYYY-MM-DD"
        )

    group_dependencies_bool = get_bool_env_var("GROUP_DEPENDENCIES")
    enable_security_updates_bool = get_bool_env_var(
        "ENABLE_SECURITY_UPDATES", default=True
    )
    dry_run_bool = get_bool_env_var("DRY_RUN")

    batch_size_str = os.getenv("BATCH_SIZE")
    batch_size = int(batch_size_str) if batch_size_str else None
    if batch_size and batch_size <= 0:
        raise ValueError("BATCH_SIZE environment variable is 0 or lower")

    filter_visibility = os.getenv("FILTER_VISIBILITY")
    filter_visibility_list = []
    if filter_visibility:
        filter_visibility_set = set()
        for visibility in filter_visibility.split(","):
            if visibility.strip().lower() not in ["public", "private", "internal"]:
                raise ValueError(
                    "FILTER_VISIBILITY environment variable not 'public', 'private', or 'internal'"
                )
            filter_visibility_set.add(visibility.strip().lower())
        filter_visibility_list = sorted(list(filter_visibility_set))
    else:
        filter_visibility_list = sorted(["public", "private", "internal"])  # all

    exempt_ecosystems = os.getenv("EXEMPT_ECOSYSTEMS")
    exempt_ecosystems_list = []
    if exempt_ecosystems:
        for ecosystem in exempt_ecosystems.split(","):
            ecosystem = ecosystem.lower().strip()
            if ecosystem not in SUPPORTED_PACKAGE_ECOSYSTEMS:
                raise ValueError(
                    f"EXEMPT_ECOSYSTEMS environment variable contains an unrecognized package-ecosystem: '{ecosystem}'."
                )
            exempt_ecosystems_list.append(ecosystem)

    project_id = os.getenv("PROJECT_ID")
    if project_id and not project_id.isnumeric():
        raise ValueError("PROJECT_ID environment variable is not numeric")

    update_existing = get_bool_env_var("UPDATE_EXISTING")

    repo_specific_exemptions_str = os.getenv("REPO_SPECIFIC_EXEMPTIONS", "")
    repo_specific_exemptions = parse_repo_specific_exemptions(
        repo_specific_exemptions_str
    )

    schedule = os.getenv("SCHEDULE", "").strip().lower()
    if schedule and schedule not in ["daily", "weekly", "monthly"]:
        raise ValueError(
            "SCHEDULE environment variable not 'daily', 'weekly', or 'monthly'"
        )
    if not schedule:
        schedule = "weekly"
    schedule_day = os.getenv("SCHEDULE_DAY", "").strip().lower()
    if schedule != "weekly" and schedule_day:
        raise ValueError(
            "SCHEDULE_DAY environment variable not needed when SCHEDULE is not 'weekly'"
        )
    if (
        schedule == "weekly"
        and schedule_day
        and schedule_day
        not in [
            "monday",
            "tuesday",
            "wednesday",
            "thursday",
            "friday",
            "saturday",
            "sunday",
        ]
    ):
        raise ValueError(
            "SCHEDULE_DAY environment variable not 'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', or 'sunday'"
        )

    labels_str = os.getenv("LABELS")
    labels_list = []
    if labels_str:
        labels_list = [label.lower().strip() for label in labels_str.split(",")]

    dependabot_config_file = os.getenv("DEPENDABOT_CONFIG_FILE")
    if dependabot_config_file and not os.path.exists(dependabot_config_file):
        raise ValueError(
            f"No dependabot extra configuration found. Please create one in {dependabot_config_file}"
        )

    return (
        organization,
        repositories_list,
        search_query,
        gh_app_id,
        gh_app_installation_id,
        gh_app_private_key_bytes,
        gh_app_enterprise_only,
        token,
        ghe,
        exempt_repositories_list,
        follow_up_type,
        title,
        body,
        created_after_date,
        dry_run_bool,
        commit_message,
        project_id,
        group_dependencies_bool,
        filter_visibility_list,
        batch_size,
        enable_security_updates_bool,
        exempt_ecosystems_list,
        update_existing,
        repo_specific_exemptions,
        schedule,
        schedule_day,
        team_name,
        labels_list,
        dependabot_config_file,
    )
