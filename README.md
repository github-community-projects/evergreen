# Evergreen action

> [!IMPORTANT]
> This repository has moved from `github/evergreen` to `github-community-projects/evergreen`.
> Please update your git remote:
>
> ```shell
> git remote set-url origin git@github.com:github-community-projects/evergreen.git
> ```
>
> Note: replace `origin` with the name of your remote if it's different.

[![CodeQL](https://github.com/github-community-projects/evergreen/actions/workflows/github-code-scanning/codeql/badge.svg)](https://github.com/github-community-projects/evergreen/actions/workflows/github-code-scanning/codeql)
[![Lint Code Base](https://github.com/github-community-projects/evergreen/actions/workflows/super-linter.yaml/badge.svg)](https://github.com/github-community-projects/evergreen/actions/workflows/super-linter.yaml)
[![Python package](https://github.com/github-community-projects/evergreen/actions/workflows/python-ci.yml/badge.svg)](https://github.com/github-community-projects/evergreen/actions/workflows/python-ci.yml)
[![OpenSSF Scorecard](https://api.scorecard.dev/projects/github.com/github-community-projects/evergreen/badge)](https://scorecard.dev/viewer/?uri=github.com/github-community-projects/evergreen)
[![OpenSSF Best Practices](https://www.bestpractices.dev/projects/9523/badge)](https://www.bestpractices.dev/projects/9523)

This is a GitHub Action that given an organization, team, or specified repositories, opens an issue/PR if dependabot is not enabled, or there are more package ecosystems that could be added. It also enables [automated security updates](https://docs.github.com/en/code-security/dependabot/dependabot-security-updates/configuring-dependabot-security-updates#managing-dependabot-security-updates-for-your-repositories) for the repository.

This action was developed by the GitHub OSPO for our own use and developed in a way that we could open source it that it might be useful to you as well! If you want to know more about how we use it, reach out in an issue in this repository.

## Example use cases

- As a part of the security team for my company, I want to make sure that all of the repositories in the company organizations are regularly updating their dependencies to ensure they are using the most secure version of the dependency available.
- As an OSPO or maintainer, I want to automate everything I can to keep maintaining my project(s) easy and efficient.

## Support

If you need support using this project or have questions about it, please [open up an issue in this repository](https://github.com/github-community-projects/evergreen/issues). Requests made directly to GitHub staff or support team will be redirected here to open an issue. GitHub SLAs and support/services contracts do not apply to this repository.

### OSPO GitHub Actions as a Whole

All feedback regarding our GitHub Actions, as a whole, should be communicated through [issues on our github-ospo repository](https://github.com/github/github-ospo/issues/new).

## Use as a GitHub Action

1. Create a repository to host this GitHub Action or select an existing repository.
1. Select a best fit workflow file from the [examples below](#example-workflows).
1. Copy that example into your repository (from step 1) and into the proper directory for GitHub Actions: `.github/workflows/` directory with the file extension `.yml` (ie. `.github/workflows/evergreen.yml`)
1. Edit the values below from the sample workflow with your information:

   - `ORGANIZATION`
   - `TEAM_NAME`
   - `REPOSITORY`
   - `EXEMPT_REPOS`
   - `TYPE`
   - `TITLE`
   - `BODY`

   If running on a whole **organization** then no repository is needed.  
   If running the action on just **one repository** or a **list of repositories**, then no organization is needed.  
   If running the action on a **team**, then an organization is required and no repository is needed.  
   The type should be either `issue` or `pull` representing the action that you want taken after discovering a repository that should enable dependabot.

1. Optionally, edit the value `CREATED_AFTER_DATE` if you are setting up this action to run regularly and only want newly created repositories to be considered.
   Otherwise, if you want all specified repositories regardless of when they were created to be considered, then leave it blank.
1. Optionally edit the value `UPDATE_EXISTING` (default value `false`) if you want to update existing dependabot configuration files.
   If set to `true`, the action will update the existing dependabot configuration file with any package ecosystems that are detected but not configured yet.
   If set to `false`, the action will only create a new dependabot configuration file if there is not an existing one.
1. Also edit the value for `GH_ENTERPRISE_URL` if you are using a GitHub Server and not using github.com.
   For github.com users, leave it empty.
1. Update the value of `GH_TOKEN`. Do this by creating a [GitHub API token](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens#creating-a-personal-access-token-classic) with the following permissions:

   - If using **classic tokens**:
     - `workflow`, this will set also all permissions for `repo`
     - under `admin`, `read:org` and `write:org`
   - If using **fine grain tokens**:
     - `Administration` - Read and Write (Needed to activate the [automated security updates](https://docs.github.com/en/code-security/dependabot/dependabot-security-updates/configuring-dependabot-security-updates#managing-dependabot-security-updates-for-your-repositories) )
     - `Pull Requests` - Read and Write (If `TYPE` input is set to `pull`)
     - `Issues` - Read and Write (If `TYPE` input is set to `issue`)
     - `Workflows` - Read and Write (Needed to create the `dependabot.yml` file)

   Then take the value of the API token you just created, and [create a repository secret](https://docs.github.com/en/actions/security-guides/encrypted-secrets) where the name of the secret is `GH_TOKEN` and the value of the secret the API token.
   Then finally update the workflow file to use that repository secret by changing `GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}` to `GH_TOKEN: ${{ secrets.GH_TOKEN }}`.
   The name of the secret can really be anything, it just needs to match between when you create the secret name and when you refer to it in the workflow file.

1. If you want the resulting issue with the output to appear in a different repository other than the one the workflow file runs in, update the line `token: ${{ secrets.GITHUB_TOKEN }}` with your own GitHub API token stored as a repository secret. This process is the same as described in the step above. More info on creating secrets can be found in the [GitHub documentation on encrypted secrets](https://docs.github.com/en/actions/security-guides/encrypted-secrets).
1. Commit the workflow file to the default branch (often `master` or `main`)
1. Wait for the action to trigger based on the `schedule` entry or manually trigger the workflow as shown in the [documentation](https://docs.github.com/en/actions/using-workflows/manually-running-a-workflow).

### Configuration

Below are the allowed configuration options:

#### Authentication

This action can be configured to authenticate with GitHub App Installation or Personal Access Token (PAT). If all configuration options are provided, the GitHub App Installation configuration has precedence. You can choose one of the following methods to authenticate:

##### GitHub App Installation

| field                        | required | default | description                                                                                                                                                                                             |
| ---------------------------- | -------- | ------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `GH_APP_ID`                  | True     | `""`    | GitHub Application ID. See [documentation](https://docs.github.com/en/apps/creating-github-apps/authenticating-with-a-github-app/about-authentication-with-a-github-app) for more details.              |
| `GH_APP_INSTALLATION_ID`     | True     | `""`    | GitHub Application Installation ID. See [documentation](https://docs.github.com/en/apps/creating-github-apps/authenticating-with-a-github-app/about-authentication-with-a-github-app) for more details. |
| `GH_APP_PRIVATE_KEY`         | True     | `""`    | GitHub Application Private Key. See [documentation](https://docs.github.com/en/apps/creating-github-apps/authenticating-with-a-github-app/about-authentication-with-a-github-app) for more details.     |
| `GITHUB_APP_ENTERPRISE_ONLY` | False    | false   | Set this input to `true` if your app is created in GHE and communicates with GHE.                                                                                                                       |

The needed GitHub app permissions are the following under `Repository permissions`:

- `Administration` - Read and Write (Needed to activate the [automated security updates](https://docs.github.com/en/code-security/dependabot/dependabot-security-updates/configuring-dependabot-security-updates#managing-dependabot-security-updates-for-your-repositories) )
- `Pull Requests` - Read and Write (If `TYPE` input is set to `pull`)
- `Issues` - Read and Write (If `TYPE` input is set to `issue`)
- `Workflows` - Read and Write (Needed to create the `dependabot.yml` file)
- `Contents` - Read and Write (Needed to create a commit)

##### Personal Access Token (PAT)

| field      | required | default | description                                                                                                                                                                                   |
| ---------- | -------- | ------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `GH_TOKEN` | True     | `""`    | The GitHub Token used to scan the repository. Must have read access to all the repositories you are interested in scanning, `repo:write`, and `workflow` privileges to create a pull request. |

#### Other Configuration Options

| field                      | required                                                                     | default                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               | description                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          |
| -------------------------- | ---------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `GH_ENTERPRISE_URL`        | False                                                                        | ""                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    | The `GH_ENTERPRISE_URL` is used to connect to an enterprise server instance of GitHub, ex: `https://yourgheserver.com`.<br>github.com users should not enter anything here.                                                                                                                                                                                                                                                                                                                                                                                                                                                          |
| `ORGANIZATION`             | Required to have `ORGANIZATION` or `REPOSITORY` or `REPOSITORY_SEARCH_QUERY` |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       | The name of the GitHub organization which you want this action to work from. ie. github.com/github would be `github`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 |
| `REPOSITORY`               | Required to have `ORGANIZATION` or `REPOSITORY` or `REPOSITORY_SEARCH_QUERY` |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       | The name of the repository and organization which you want this action to work from. ie. `github-community-projects/evergreen` or a comma separated list of multiple repositories `github-community-projects/evergreen,super-linter/super-linter`                                                                                                                                                                                                                                                                                                                                                                                    |
| `REPOSITORY_SEARCH_QUERY`  | Required to have `ORGANIZATION` or `REPOSITORY` or `REPOSITORY_SEARCH_QUERY` | ""                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    | When set, directs the action to use the GitHub Search API to search repositories matching this query instead of enumerating all organization repositories. This overrides anything set in the `REPOSITORY` and `ORGANIZATION` variables. Example: `org:my-org is:repository archived:false created:>2025-07-01`.                                                                                                                                                                                                                                                                                                                     |
| `EXEMPT_REPOS`             | False                                                                        | ""                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    | These repositories will be exempt from this action considering them for dependabot enablement. ex: If my org is set to `github-community-projects` then I might want to exempt a few of the repos but get the rest by setting `EXEMPT_REPOS` to `github-community-projects/evergreen,github-community-projects/contributors`                                                                                                                                                                                                                                                                                                           |
| `TYPE`                     | False                                                                        | pull                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  | Type refers to the type of action you want taken if this workflow determines that dependabot could be enabled. Valid values are `pull` or `issue`.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   |
| `TITLE`                    | False                                                                        | "Enable Dependabot"                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   | The title of the issue or pull request that will be created if dependabot could be enabled.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          |
| `BODY`                     | False                                                                        | <ul><li>**Pull Request:** "Dependabot could be enabled for this repository. Please enable it by merging this pull request so that we can keep our dependencies up to date and secure."</li><li>**Issue:** "Please update the repository to include a Dependabot configuration file. This will ensure our dependencies remain updated and secure. Follow the guidelines in [creating Dependabot configuration files](https://docs.github.com/en/code-security/dependabot/dependabot-version-updates/configuration-options-for-the-dependabot.yml-file) to set it up properly.Here's an example of the code:"</li></ul> | The body of the issue or pull request that will be created if dependabot could be enabled.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           |
| `COMMIT_MESSAGE`           | False                                                                        | "Create dependabot.yaml"                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              | The commit message for the pull request that will be created if dependabot could be enabled.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         |
| `CREATED_AFTER_DATE`       | False                                                                        | none                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  | If a value is set, this action will only consider repositories created on or after this date for dependabot enablement. This is useful if you want to only consider newly created repositories. If I set up this action to run weekly and I only want to scan for repos created in the last week that need dependabot enabled, then I would set `CREATED_AFTER_DATE` to 7 days ago. That way only repositories created after 7 days ago will be considered for dependabot enablement. If not set or set to nothing, all repositories will be scanned and a duplicate issue/pull request may occur. Ex: 2023-12-31 for Dec. 31st 2023 |
| `UPDATE_EXISTING`          | False                                                                        | False                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 | If set to true, this action will update the existing dependabot configuration file with any package ecosystems that are detected but not configured yet. If set to false, the action will only create a new dependabot configuration file if there is not an existing one.                                                                                                                                                                                                                                                                                                                                                           |
| `PROJECT_ID`               | False                                                                        | ""                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    | If set, this will assign the issue or pull request to the project with the given ID. ( The project ID on GitHub can be located by navigating to the respective project and observing the URL's end.) **The `ORGANIZATION` variable is required**                                                                                                                                                                                                                                                                                                                                                                                     |
| `DRY_RUN`                  | False                                                                        | False                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 | If set to true, this action will not create any issues or pull requests. It will only log the repositories that could have dependabot enabled. This is useful for testing.                                                                                                                                                                                                                                                                                                                                                                                                                                                           |
| `GROUP_DEPENDENCIES`       | False                                                                        | false                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 | If set to true, dependabot configuration will group dependencies updates based on [dependency type](https://docs.github.com/en/code-security/dependabot/dependabot-version-updates/configuration-options-for-the-dependabot.yml-file#groups) (production or development, where supported)                                                                                                                                                                                                                                                                                                                                            |
| `FILTER_VISIBILITY`        | False                                                                        | "public,private,internal"                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             | Use this flag to filter repositories in scope by their visibility (`public`, `private`, `internal`). By default all repository are targeted. ex: to ignore public repositories set this value to `private,internal`.                                                                                                                                                                                                                                                                                                                                                                                                                 |
| `BATCH_SIZE`               | False                                                                        | None                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  | Set this to define the maximum amount of eligible repositories for every run. This is useful if you are targeting large organizations and you don't want to flood repositories with pull requests / issues. ex: if you want to target 20 repositories per time, set this to 20.                                                                                                                                                                                                                                                                                                                                                      |
| `ENABLE_SECURITY_UPDATES`  | False                                                                        | true                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  | If set to true, Evergreen will enable [Dependabot security updates](https://docs.github.com/en/code-security/dependabot/dependabot-security-updates/configuring-dependabot-security-updates) on target repositories. Note that the GitHub token needs to have the `administration:write` permission on every repository in scope to successfully enable security updates.                                                                                                                                                                                                                                                            |
| `EXEMPT_ECOSYSTEMS`        | False                                                                        | ""                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    | A list of [package ecosystems](https://docs.github.com/en/code-security/dependabot/dependabot-version-updates/configuration-options-for-the-dependabot.yml-file#package-ecosystem) to exempt from the generated dependabot configuration. To ignore ecosystems set this to one or more of `bundler`,`cargo`, `composer`, `pip`, `docker`, `npm`, `gomod`, `mix`, `nuget`, `maven`, `github-actions` and `terraform`. ex: if you don't want Dependabot to update Dockerfiles and Github Actions you can set this to `docker,github-actions`.                                                                                          |
| `REPO_SPECIFIC_EXEMPTIONS` | False                                                                        | ""                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    | A list of repositories that should be exempt from specific package ecosystems similar to EXEMPT_ECOSYSTEMS but those apply to all repositories. ex: `org1/repo1:docker,github-actions;org1/repo2:pip` would set exempt_ecosystems for `org1/repo1` to be `['docker', 'github-actions']`, and for `org1/repo2` it would be `['pip']`, while for every other repository evaluated, it would be set by the env variable `EXEMPT_ECOSYSTEMS`. NOTE: If you want specific exemptions to be added on top of the already specified global exemptions, you need to add the global exemptions to each repo specific exemption.                |
| `SCHEDULE`                 | False                                                                        | `weekly`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              | Schedule interval by which to check for dependency updates via Dependabot. Allowed values are `daily`, `weekly`, or `monthly`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        |
| `SCHEDULE_DAY`             | False                                                                        | ''                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    | Scheduled day by which to check for dependency updates via Dependabot. Allowed values are days of the week full names (i.e., `monday`)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               |
| `LABELS`                   | False                                                                        | ""                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    | A comma separated list of labels that should be added to pull requests opened by dependabot.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         |
| `DEPENDABOT_CONFIG_FILE`   | False                                                                        | ""                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    | Location of the configuration file for `dependabot.yml` configurations. If the file is present locally it takes precedence over the one in the repository.                                                                                                                                                                                                                                                                                                                                                                                                                                                                           |

### Private repositories configuration

Dependabot allows the configuration of [private registries](https://docs.github.com/en/code-security/dependabot/dependabot-version-updates/configuration-options-for-the-dependabot.yml-file#configuration-options-for-private-registries) for dependabot to use.  
To add a private registry configuration to the dependabot file the `DEPENDABOT_CONFIG_FILE` needs to be set with the path of the configuration file.

This configuration file needs to exist on the repository where the action runs. It can also be created locally to test some configurations (if created locally it takes precedence over the file on the repository).

#### Usage

Set the input variable:

```yaml
DEPENDABOT_CONFIG_FILE = "dependabot-config.yaml"
```

Create a file on your repository in the same path:

```yaml
npm:
  type: "npm"
  url: "https://yourprivateregistry/npm/"
  username: "${{secrets.username}}"
  password: "${{secrets.password}}"
  key: <used if necessary>
  token: <used if necessary>
  replaces-base: <used if necessary>
maven:
  type: "maven"
  url: "https://yourprivateregistry/maven/"
  username: "${{secrets.username}}"
  password: "${{secrets.password}}"
```

The principal key of each configuration need to match the package managers that the [script is looking for](https://docs.github.com/en/code-security/dependabot/dependabot-version-updates/configuration-options-for-the-dependabot.yml-file#package-ecosystem).

The `dependabot.yaml` created file will look like the following with the `registries:` key added:

```yaml
updates:
  - package-ecosystem: "npm"
    directory: "/"
    registries: --> added configuration
      - 'npm'    --> added configuration
    schedule:
      interval: "weekly"
    labels:
      - "test"
      - "dependabot"
      - "new"
```

### Example workflows

#### Basic

```yaml
---
name: Weekly dependabot checks
on:
  workflow_dispatch:
  schedule:
    - cron: "3 2 * * 6"

permissions:
  contents: read

jobs:
  evergreen:
    name: evergreen
    runs-on: ubuntu-latest
    permissions:
      issues: write

    steps:
      - name: Run evergreen action
        uses: github-community-projects/evergreen@v2
        env:
          GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          ORGANIZATION: <YOUR_ORGANIZATION_GOES_HERE>

      - name: Post evergreen job summary
        run: cat summary.md >> $GITHUB_STEP_SUMMARY
```

#### Advanced

```yaml
---
name: Weekly dependabot checks
on:
  workflow_dispatch:
  schedule:
    - cron: "3 2 * * 6"

permissions:
  contents: read

jobs:
  evergreen:
    name: evergreen
    runs-on: ubuntu-latest
    permissions:
      issues: write

    steps:
      - shell: bash
        run: |
          # Get the current date
          current_date=$(date +'%Y-%m-%d')

          # Calculate the previous month
          previous_date=$(date -d "$current_date -7 day" +'%Y-%m-%d')

          echo "$previous_date..$current_date"
          echo "one_week_ago=$previous_date" >> "$GITHUB_ENV"

      - name: Run evergreen action
        uses: github-community-projects/evergreen@v2
        env:
          GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          ORGANIZATION: <YOUR_ORGANIZATION_GOES_HERE>
          EXEMPT_REPOS: "org_name/repo_name_1, org_name/repo_name_2"
          TITLE: "Add dependabot configuration"
          BODY: "Please add this dependabot configuration so that we can keep the dependencies in this repo up to date and secure. for help, contact XXX"
          CREATED_AFTER_DATE: ${{ env.one_week_ago }}

      - name: Post evergreen job summary
        run: cat summary.md >> $GITHUB_STEP_SUMMARY
```

#### Using REPOSITORY_SEARCH_QUERY

```yaml
---
name: Weekly dependabot checks
on:
  workflow_dispatch:
  schedule:
    - cron: "3 2 * * 6"

permissions:
  contents: read

jobs:
  evergreen:
    name: evergreen
    runs-on: ubuntu-latest
    permissions:
      issues: write

    steps:
      - shell: bash
        run: |
          # Get the current date
          current_date=$(date +'%Y-%m-%d')

          # Calculate the previous month
          previous_date=$(date -d "$current_date -7 day" +'%Y-%m-%d')

          echo "$previous_date..$current_date"
          echo "one_week_ago=$previous_date" >> "$GITHUB_ENV"

      - name: Run evergreen action
        uses: github-community-projects/evergreen@v2
        env:
          GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          REPOSITORY_SEARCH_QUERY: "org:your_organization is:repository is:public archived:false created:>${{ env.one_week_ago }}"
          TITLE: "Add dependabot configuration"
          BODY: "Please add this dependabot configuration so that we can keep the dependencies in this repo up to date and secure. for help, contact XXX"

      - name: Post evergreen job summary
        run: cat summary.md >> $GITHUB_STEP_SUMMARY
```

#### Using GitHub app

```yaml
name: Evergreen
on:
  workflow_dispatch:
  schedule:
    - cron: "3 2 * * 6"

permissions:
  contents: read

jobs:
  evergreen:
    name: "Create dependabot.yml"
    runs-on: ubuntu-latest

    steps:
      - name: Run evergreen action for tools
        uses: github-community-projects/evergreen@v2
        env:
          GH_APP_ID: ${{ secrets.GH_APP_ID }}
          GH_APP_INSTALLATION_ID: ${{ secrets.GH_APP_INSTALLATION_ID }}
          GH_APP_PRIVATE_KEY: ${{ secrets.GH_APP_PRIVATE_KEY }}
          # GITHUB_APP_ENTERPRISE_ONLY: True --> Set to true when created GHE App needs to communicate with GHE api
          GH_ENTERPRISE_URL: ${{ github.server_url }}
          # GH_TOKEN: ${{ secrets.GITHUB_TOKEN }} --> the token input is not used if the github app inputs are set
          ORGANIZATION: your_organization
          UPDATE_EXISTING: True
          GROUP_DEPENDENCIES: True

      - name: Post evergreen job summary
        run: cat summary.md >> $GITHUB_STEP_SUMMARY
```

## Local usage without Docker

1. Make sure you have at least Python3.11 installed
1. Copy `.env-example` to `.env`
1. Fill out the `.env` file with a _token_ from a user that has access to the organization to scan (listed below). Tokens should have at least write:org access for organization scanning and write:repository for repository scanning.
1. Fill out the `.env` file with the configuration parameters you want to use
1. `pip3 install -r requirements.txt`
1. Run `python3 ./evergreen.py`, which will output everything in the terminal

## License

[MIT](LICENSE)

## More OSPO Tools

Looking for more resources for your open source program office (OSPO)? Check out the [`github-ospo`](https://github.com/github/github-ospo) repo for a variety of tools designed to support your needs.
