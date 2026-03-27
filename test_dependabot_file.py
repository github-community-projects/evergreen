# pylint: disable=too-many-public-methods
"""Tests for the dependabot_file.py functions."""

import base64
import os
import unittest
from unittest.mock import MagicMock, patch

import github3
import ruamel.yaml
from dependabot_file import add_existing_ecosystem_to_exempt_list, build_dependabot_file

yaml = ruamel.yaml.YAML()


class TestDependabotFile(unittest.TestCase):
    """
    Test the dependabot_file.py functions.
    """

    def test_not_found_error(self):
        """Test that the dependabot.yml file is built correctly with no package manager"""
        repo = MagicMock()
        response = MagicMock()
        response.status_code = 404
        repo.file_contents.side_effect = github3.exceptions.NotFoundError(resp=response)

        result = build_dependabot_file(repo, False, [], {}, None, "", "", [], None)
        self.assertIsNone(result)

    def test_build_dependabot_file_with_schedule_day(self):
        """Test that the dependabot.yml file is built correctly with weekly schedule day"""
        repo = MagicMock()
        filename_list = ["Gemfile", "Gemfile.lock"]

        for filename in filename_list:
            repo.file_contents.side_effect = lambda f, filename=filename: f == filename
            expected_result = yaml.load(b"""
version: 2
updates:
  - package-ecosystem: 'bundler'
    directory: '/'
    schedule:
      interval: 'weekly'
      day: 'tuesday'
""")
            result = build_dependabot_file(
                repo, False, [], {}, None, "weekly", "tuesday", [], None
            )
            self.assertEqual(result, expected_result)

    def test_build_dependabot_file_with_bundler(self):
        """Test that the dependabot.yml file is built correctly with bundler"""
        repo = MagicMock()
        filename_list = ["Gemfile", "Gemfile.lock"]

        for filename in filename_list:
            repo.file_contents.side_effect = lambda f, filename=filename: f == filename
            expected_result = yaml.load(b"""
version: 2
updates:
  - package-ecosystem: 'bundler'
    directory: '/'
    schedule:
      interval: 'weekly'
""")
            result = build_dependabot_file(
                repo, False, [], {}, None, "weekly", "", [], None
            )
            self.assertEqual(result, expected_result)

    def test_build_dependabot_file_with_existing_config_bundler_no_update(self):
        """Test that the dependabot.yml file is built correctly with bundler"""
        repo = MagicMock()
        repo.file_contents.side_effect = lambda f, filename="Gemfile": f == filename

        # expected_result is None because the existing config already contains the all applicable ecosystems
        expected_result = None
        existing_config = MagicMock()
        existing_config.content = base64.b64encode(b"""
version: 2
updates:
  - package-ecosystem: "bundler"
    directory: "/"
    schedule:
      interval: "weekly"
    commit-message:
      prefix: "chore(deps)"
""")
        result = build_dependabot_file(
            repo, False, [], {}, existing_config, "weekly", "", [], None
        )
        self.assertEqual(result, expected_result)

    def test_build_dependabot_file_with_2_space_indent_existing_config_bundler_with_update(
        self,
    ):
        """Test that the dependabot.yml file is built correctly with bundler"""
        repo = MagicMock()
        repo.file_contents.side_effect = lambda f, filename="Gemfile": f == filename

        # expected_result maintains existing ecosystem with custom configuration
        # and adds new ecosystem
        expected_result = yaml.load(b"""
version: 2
updates:
  - package-ecosystem: "pip"
    directory: "/"
    schedule:
      interval: "weekly"
    commit-message:
      prefix: "chore(deps)"
  - package-ecosystem: 'bundler'
    directory: '/'
    schedule:
      interval: 'weekly'
""")
        existing_config = MagicMock()
        existing_config.content = base64.b64encode(b"""
version: 2
updates:
  - package-ecosystem: "pip"
    directory: "/"
    schedule:
      interval: "weekly"
    commit-message:
      prefix: "chore(deps)"
""")
        result = build_dependabot_file(
            repo, False, [], {}, existing_config, "weekly", "", [], None
        )
        self.assertEqual(result, expected_result)

    def test_build_dependabot_file_with_weird_space_indent_existing_config_bundler_with_update(
        self,
    ):
        """Test that the dependabot.yml file is built correctly with bundler"""
        repo = MagicMock()
        repo.file_contents.side_effect = lambda f, filename="Gemfile": f == filename

        # expected_result maintains existing ecosystem with custom configuration
        # and adds new ecosystem
        existing_config = MagicMock()
        existing_config.content = base64.b64encode(b"""
version: 2
updates:
- package-ecosystem: "pip"
directory: "/"
  schedule:
    interval: "weekly"
  commit-message:
    prefix: "chore(deps)"
  """)

        with self.assertRaises(ruamel.yaml.YAMLError):
            build_dependabot_file(
                repo, False, [], {}, existing_config, "weekly", "", [], None
            )

    def test_build_dependabot_file_with_incorrect_indentation_in_extra_dependabot_config_file(
        self,
    ):
        """Test incorrect indentation on extra_dependabot_config is caught during YAML loading"""
        # In production, extra_dependabot_config is loaded from a file via
        # ruamel.yaml in evergreen.py before being passed to build_dependabot_file.
        # Verify that malformed YAML raises an error at the loading stage.
        yaml_loader = ruamel.yaml.YAML()
        with self.assertRaises(ruamel.yaml.YAMLError):
            yaml_loader.load(b"""
npm:
type: 'npm'
  url: 'https://yourprivateregistry/npm/'
  username: '${{secrets.username}}'
  password: '${{secrets.password}}'
  """)

    @patch.dict(os.environ, {"DEPENDABOT_CONFIG_FILE": "dependabot-config.yaml"})
    def test_build_dependabot_file_with_extra_dependabot_config_file(self):
        """Test that the dependabot.yaml file is built correctly with extra configurations from extra_dependabot_config"""

        repo = MagicMock()
        repo.file_contents.side_effect = (
            lambda f, filename="package.json": f == filename
        )

        # expected_result maintains existing ecosystem with custom configuration
        # and adds new ecosystem
        extra_dependabot_config = yaml.load(b"""
npm:
  type: 'npm'
  url: 'https://yourprivateregistry/npm/'
  username: '${{secrets.username}}'
  password: '${{secrets.password}}'
    """)

        expected_result = yaml.load(b"""
version: 2
registries:
  npm:
    type: 'npm'
    url: 'https://yourprivateregistry/npm/'
    username: '${{secrets.username}}'
    password: '${{secrets.password}}'
updates:
  - package-ecosystem: "npm"
    directory: "/"
    registries:
      - 'npm'
    schedule:
      interval: "weekly"
""")

        result = build_dependabot_file(
            repo, False, [], {}, None, "weekly", "", [], extra_dependabot_config
        )
        self.assertEqual(result, expected_result)

    def test_build_dependabot_file_with_npm(self):
        """Test that the dependabot.yml file is built correctly with npm"""
        repo = MagicMock()
        filename_list = ["package.json", "package-lock.json", "yarn.lock"]

        for filename in filename_list:
            repo.file_contents.side_effect = lambda f, filename=filename: f == filename
            expected_result = yaml.load(b"""
version: 2
updates:
  - package-ecosystem: 'npm'
    directory: '/'
    schedule:
      interval: 'weekly'
""")
            result = build_dependabot_file(
                repo, False, [], {}, None, "weekly", "", [], None
            )
            self.assertEqual(result, expected_result)

    def test_build_dependabot_file_with_pip(self):
        """Test that the dependabot.yml file is built correctly with pip"""
        repo = MagicMock()
        filename_list = [
            "requirements.txt",
            "Pipfile",
            "Pipfile.lock",
            "pyproject.toml",
            "poetry.lock",
        ]

        for filename in filename_list:
            repo.file_contents.side_effect = lambda f, filename=filename: f == filename
            expected_result = yaml.load(b"""
version: 2
updates:
  - package-ecosystem: 'pip'
    directory: '/'
    schedule:
      interval: 'weekly'
""")
            result = build_dependabot_file(
                repo, False, [], {}, None, "weekly", "", [], None
            )
            self.assertEqual(result, expected_result)

    def test_build_dependabot_file_with_cargo(self):
        """Test that the dependabot.yml file is built correctly with Cargo"""
        repo = MagicMock()
        filename_list = [
            "Cargo.toml",
            "Cargo.lock",
        ]

        for filename in filename_list:
            repo.file_contents.side_effect = lambda f, filename=filename: f == filename
            expected_result = yaml.load(b"""
version: 2
updates:
  - package-ecosystem: 'cargo'
    directory: '/'
    schedule:
      interval: 'weekly'
""")
            result = build_dependabot_file(
                repo, False, [], {}, None, "weekly", "", [], None
            )
            self.assertEqual(result, expected_result)

    def test_build_dependabot_file_with_gomod(self):
        """Test that the dependabot.yml file is built correctly with Go module"""
        repo = MagicMock()
        repo.file_contents.side_effect = lambda filename: filename == "go.mod"

        expected_result = yaml.load(b"""
version: 2
updates:
  - package-ecosystem: 'gomod'
    directory: '/'
    schedule:
      interval: 'weekly'
""")
        result = build_dependabot_file(
            repo, False, [], {}, None, "weekly", "", [], None
        )
        self.assertEqual(result, expected_result)

    def test_build_dependabot_file_with_composer(self):
        """Test that the dependabot.yml file is built correctly with Composer"""
        repo = MagicMock()
        filename_list = [
            "composer.json",
            "composer.lock",
        ]

        for filename in filename_list:
            repo.file_contents.side_effect = lambda f, filename=filename: f == filename
            expected_result = yaml.load(b"""
version: 2
updates:
  - package-ecosystem: 'composer'
    directory: '/'
    schedule:
      interval: 'weekly'
""")
            result = build_dependabot_file(
                repo, False, [], {}, None, "weekly", "", [], None
            )
            self.assertEqual(result, expected_result)

    def test_build_dependabot_file_with_hex(self):
        """Test that the dependabot.yml file is built correctly with Hex"""
        repo = MagicMock()
        filename_list = [
            "mix.exs",
            "mix.lock",
        ]

        for filename in filename_list:
            repo.file_contents.side_effect = lambda f, filename=filename: f == filename
            expected_result = yaml.load(b"""
version: 2
updates:
  - package-ecosystem: 'mix'
    directory: '/'
    schedule:
      interval: 'weekly'
""")
            result = build_dependabot_file(
                repo, False, [], {}, None, "weekly", "", [], None
            )
            self.assertEqual(result, expected_result)

    def test_build_dependabot_file_with_nuget(self):
        """Test that the dependabot.yml file is built correctly with NuGet"""
        repo = MagicMock()
        repo.file_contents.side_effect = lambda filename: filename.endswith(".csproj")

        expected_result = yaml.load(b"""
version: 2
updates:
  - package-ecosystem: 'nuget'
    directory: '/'
    schedule:
      interval: 'weekly'
""")
        result = build_dependabot_file(
            repo, False, [], {}, None, "weekly", "", [], None
        )
        self.assertEqual(result, expected_result)

    def test_build_dependabot_file_with_docker(self):
        """Test that the dependabot.yml file is built correctly with Docker"""
        repo = MagicMock()
        repo.file_contents.side_effect = lambda filename: filename == "Dockerfile"

        expected_result = yaml.load(b"""
version: 2
updates:
  - package-ecosystem: 'docker'
    directory: '/'
    schedule:
      interval: 'weekly'
""")
        result = build_dependabot_file(
            repo, False, [], {}, None, "weekly", "", [], None
        )
        self.assertEqual(result, expected_result)

    def test_build_dependabot_file_with_maven(self):
        """Test that the dependabot.yml file is built correctly with maven"""
        repo = MagicMock()
        repo.file_contents.side_effect = lambda filename: filename == "pom.xml"

        expected_result = yaml.load(b"""
version: 2
updates:
  - package-ecosystem: 'maven'
    directory: '/'
    schedule:
      interval: 'weekly'
""")
        result = build_dependabot_file(
            repo, False, [], {}, None, "weekly", "", [], None
        )
        self.assertEqual(result, expected_result)

    def test_build_dependabot_file_with_gradle(self):
        """Test that the dependabot.yml file is built correctly with gradle"""
        repo = MagicMock()
        repo.file_contents.side_effect = lambda filename: filename == "build.gradle"

        expected_result = yaml.load(b"""
version: 2
updates:
  - package-ecosystem: 'gradle'
    directory: '/'
    schedule:
      interval: 'weekly'
""")
        result = build_dependabot_file(
            repo, False, [], {}, None, "weekly", "", [], None
        )
        self.assertEqual(result, expected_result)

    def test_build_dependabot_file_with_new_ecosystems(self):
        """Test that the dependabot.yml file is built correctly for newly added ecosystems.
        Each (ecosystem, manifest_file) pair gets its own subTest so every
        alternative manifest filename is verified, not just the first one."""
        ecosystems = [
            ("bazel", "MODULE.bazel"),
            ("bazel", "WORKSPACE"),
            ("bazel", "WORKSPACE.bazel"),
            ("bun", "bun.lock"),
            ("conda", "environment.yml"),
            ("conda", "environment.yaml"),
            ("docker-compose", "docker-compose.yml"),
            ("docker-compose", "docker-compose.yaml"),
            ("docker-compose", "compose.yaml"),
            ("docker-compose", "compose.yml"),
            ("dotnet-sdk", "global.json"),
            ("elm", "elm.json"),
            ("gitsubmodule", ".gitmodules"),
            ("helm", "Chart.yaml"),
            ("julia", "Project.toml"),
            ("pre-commit", ".pre-commit-config.yaml"),
            ("pre-commit", ".pre-commit-config.yml"),
            ("pre-commit", ".pre-commit.yaml"),
            ("pre-commit", ".pre-commit.yml"),
            ("pub", "pubspec.yaml"),
            ("rust-toolchain", "rust-toolchain.toml"),
            ("rust-toolchain", "rust-toolchain"),
            ("swift", "Package.swift"),
            ("uv", "uv.lock"),
            ("vcpkg", "vcpkg.json"),
            ("vcpkg", "vcpkg-configuration.json"),
        ]
        for ecosystem, manifest_file in ecosystems:
                repo = MagicMock()
                repo.file_contents.side_effect = lambda f, mf=manifest_file: f == mf

                expected_result = yaml.load(f"""
version: 2
updates:
  - package-ecosystem: '{ecosystem}'
    directory: '/'
    schedule:
      interval: 'weekly'
""".encode())
                result = build_dependabot_file(
                    repo, False, [], {}, None, "weekly", "", [], None
                )
                self.assertEqual(result, expected_result)

    def test_build_dependabot_file_with_terraform_with_files(self):
        """Test that the dependabot.yml file is built correctly with Terraform"""
        repo = MagicMock()
        response = MagicMock()
        response.status_code = 404
        repo.file_contents.side_effect = github3.exceptions.NotFoundError(resp=response)
        repo.directory_contents.side_effect = lambda path: (
            [("main.tf", None)] if path == "/" else []
        )

        expected_result = yaml.load(b"""
version: 2
updates:
  - package-ecosystem: 'terraform'
    directory: '/'
    schedule:
      interval: 'weekly'
""")
        result = build_dependabot_file(
            repo, False, [], {}, None, "weekly", "", [], None
        )
        self.assertEqual(result, expected_result)

    def test_build_dependabot_file_with_terraform_without_files(self):
        """Test that the dependabot.yml file is built correctly with Terraform"""
        repo = MagicMock()
        response = MagicMock()
        response.status_code = 404
        repo.file_contents.side_effect = github3.exceptions.NotFoundError(resp=response)

        # Test absence of Terraform files
        repo.directory_contents.side_effect = lambda path: [] if path == "/" else []
        result = build_dependabot_file(
            repo, False, [], {}, None, "weekly", "", [], None
        )
        self.assertIsNone(result)

        # Test empty repository
        response = MagicMock()
        response.status_code = 404
        repo.directory_contents.side_effect = github3.exceptions.NotFoundError(
            resp=response
        )
        result = build_dependabot_file(
            repo, False, [], {}, None, "weekly", "", [], None
        )
        self.assertIsNone(result)

    def test_build_dependabot_file_with_devcontainers(self):
        """Test that the dependabot.yml file is built correctly with devcontainers"""
        repo = MagicMock()
        response = MagicMock()
        response.status_code = 404
        repo.file_contents.side_effect = github3.exceptions.NotFoundError(resp=response)
        repo.directory_contents.side_effect = lambda path: (
            [("devcontainer.json", None)] if path == ".devcontainer" else []
        )

        expected_result = yaml.load(b"""
version: 2
updates:
  - package-ecosystem: 'devcontainers'
    directory: '/'
    schedule:
      interval: 'weekly'
""")
        result = build_dependabot_file(
            repo, False, [], None, None, "weekly", "", [], None
        )
        self.assertEqual(result, expected_result)

    def test_build_dependabot_file_with_github_actions(self):
        """Test that the dependabot.yml file is built correctly with GitHub Actions"""
        repo = MagicMock()
        response = MagicMock()
        response.status_code = 404
        repo.file_contents.side_effect = github3.exceptions.NotFoundError(resp=response)
        repo.directory_contents.side_effect = lambda path: (
            [("test.yml", None)] if path == ".github/workflows" else []
        )

        expected_result = yaml.load(b"""
version: 2
updates:
  - package-ecosystem: 'github-actions'
    directory: '/'
    schedule:
      interval: 'weekly'
""")
        result = build_dependabot_file(
            repo, False, [], None, None, "weekly", "", [], None
        )
        self.assertEqual(result, expected_result)

    def test_build_dependabot_file_with_github_actions_without_files(self):
        """Test that the dependabot.yml file is None when no YAML files are found in the .github/workflows/ directory."""
        repo = MagicMock()
        response = MagicMock()
        response.status_code = 404
        repo.file_contents.side_effect = github3.exceptions.NotFoundError(resp=response)
        repo.directory_contents.side_effect = github3.exceptions.NotFoundError(
            resp=response
        )

        result = build_dependabot_file(
            repo, False, [], None, None, "weekly", "", [], None
        )
        self.assertIsNone(result)

    def test_build_dependabot_file_with_groups(self):
        """Test that the dependabot.yml file is built correctly with grouped dependencies"""
        repo = MagicMock()
        repo.file_contents.side_effect = lambda filename: filename == "Dockerfile"

        expected_result = yaml.load(b"""
version: 2
updates:
  - package-ecosystem: 'docker'
    directory: '/'
    schedule:
      interval: 'weekly'
    groups:
      production-dependencies:
        dependency-type: 'production'
      development-dependencies:
        dependency-type: 'development'
""")
        result = build_dependabot_file(repo, True, [], {}, None, "weekly", "", [], None)
        self.assertEqual(result, expected_result)

    def test_build_dependabot_file_with_exempt_ecosystems(self):
        """Test that the dependabot.yml file is built correctly with exempted ecosystems"""
        repo = MagicMock()
        repo.file_contents.side_effect = lambda filename: filename == "Dockerfile"

        result = build_dependabot_file(
            repo, False, ["docker"], {}, None, "weekly", "", [], None
        )
        self.assertIsNone(result)

    def test_build_dependabot_file_with_repo_specific_exempt_ecosystems(self):
        """Test that the dependabot.yml file is built correctly with exempted ecosystems"""
        repo = MagicMock()
        repo.full_name = "test/test"
        repo.file_contents.side_effect = lambda filename: filename == "Dockerfile"

        result = build_dependabot_file(
            repo, False, [], {"test/test": ["docker"]}, None, "weekly", "", [], None
        )
        self.assertIsNone(result)

    def test_add_existing_ecosystem_to_exempt_list(self):
        """Test that existing ecosystems are added to the exempt list"""
        exempt_ecosystems = ["npm", "pip", "github-actions"]

        existing_config = {
            "updates": [
                {"package-ecosystem": "npm"},
                {"package-ecosystem": "pip"},
                {"package-ecosystem": "bundler"},
            ]
        }

        add_existing_ecosystem_to_exempt_list(exempt_ecosystems, existing_config)

        # Check new ecosystem is added to exempt list
        self.assertIn("bundler", exempt_ecosystems)
        # Keep existing ecosystems in exempt list
        for ecosystem in exempt_ecosystems:
            self.assertIn(ecosystem, exempt_ecosystems)

    def test_build_dependabot_file_for_multiple_repos_with_few_existing_config(self):
        """
        Test the case where there are multiple repos with few existing dependabot config
        """
        existing_config_repo = MagicMock()

        existing_config_repo.file_contents.side_effect = (
            lambda f, filename="Gemfile": f == filename
        )

        existing_config = MagicMock()
        existing_config.content = base64.b64encode(b"""
version: 2
updates:
  - package-ecosystem: 'bundler'
    directory: '/'
    schedule:
      interval: 'weekly'
""")

        exempt_ecosystems = []
        result = build_dependabot_file(
            existing_config_repo,
            False,
            exempt_ecosystems,
            {},
            existing_config,
            "weekly",
            "",
            [],
            None,
        )
        self.assertIsNone(result)

        no_existing_config_repo = MagicMock()
        filename_list = ["package.json", "package-lock.json", "yarn.lock"]
        for filename in filename_list:
            no_existing_config_repo.file_contents.side_effect = (
                lambda f, filename=filename: f == filename
            )
            yaml.preserve_quotes = True
            expected_result = yaml.load(b"""
version: 2
updates:
  - package-ecosystem: 'npm'
    directory: '/'
    schedule:
      interval: 'weekly'
""")
        result = build_dependabot_file(
            no_existing_config_repo,
            False,
            exempt_ecosystems,
            {},
            None,
            "weekly",
            "",
            [],
            None,
        )
        self.assertEqual(result, expected_result)

    def test_check_multiple_repos_with_no_dependabot_config(self):
        """
        Test the case where there is a single repo
        """
        mock_repo_1 = MagicMock()
        mock_repo_1.file_contents.side_effect = lambda filename: filename == "go.mod"

        expected_result = yaml.load(b"""
version: 2
updates:
  - package-ecosystem: 'gomod'
    directory: '/'
    schedule:
      interval: 'weekly'
""")
        exempt_ecosystems = []
        result = build_dependabot_file(
            mock_repo_1, False, exempt_ecosystems, {}, None, "weekly", "", [], None
        )
        self.assertEqual(result, expected_result)

        no_existing_config_repo = MagicMock()
        filename_list = ["package.json", "package-lock.json", "yarn.lock"]
        for filename in filename_list:
            no_existing_config_repo.file_contents.side_effect = (
                lambda f, filename=filename: f == filename
            )
            expected_result = yaml.load(b"""
version: 2
updates:
  - package-ecosystem: 'npm'
    directory: '/'
    schedule:
      interval: 'weekly'
""")
        result = build_dependabot_file(
            no_existing_config_repo,
            False,
            exempt_ecosystems,
            {},
            None,
            "weekly",
            "",
            [],
            None,
        )
        self.assertEqual(result, expected_result)

    def test_build_dependabot_file_with_label(self):
        """Test that the dependabot.yml file is built correctly with one label set"""
        repo = MagicMock()
        filename_list = ["Gemfile", "Gemfile.lock"]

        for filename in filename_list:
            repo.file_contents.side_effect = lambda f, filename=filename: f == filename
            expected_result = yaml.load(b"""
version: 2
updates:
  - package-ecosystem: 'bundler'
    directory: '/'
    schedule:
      interval: 'weekly'
    labels:
      - "dependencies"
""")
            result = build_dependabot_file(
                repo, False, [], {}, None, "weekly", "", ["dependencies"], None
            )
            self.assertEqual(result, expected_result)

    def test_build_dependabot_file_with_labels(self):
        """Test that the dependabot.yml file is built correctly with multiple labels set"""
        repo = MagicMock()
        filename_list = ["Gemfile", "Gemfile.lock"]

        for filename in filename_list:
            repo.file_contents.side_effect = lambda f, filename=filename: f == filename
            expected_result = yaml.load(b"""
version: 2
updates:
  - package-ecosystem: 'bundler'
    directory: '/'
    schedule:
      interval: 'weekly'
    labels:
      - "dependencies"
      - "test1"
      - "test2"
""")
            result = build_dependabot_file(
                repo,
                False,
                [],
                {},
                None,
                "weekly",
                "",
                ["dependencies", "test1", "test2"],
                None,
            )
            self.assertEqual(result, expected_result)

    def test_build_dependabot_file_preserves_existing_registries(self):
        """Test that existing registries are preserved when adding new ecosystems"""
        repo = MagicMock()
        repo.file_contents.side_effect = lambda filename: filename == "Gemfile"

        # Create existing config with registries but no bundler ecosystem
        existing_config = MagicMock()
        existing_config.content = base64.b64encode(b"""
version: 2
registries:
  gradle-artifactory:
    type: maven-repository
    url: https://acme.jfrog.io/artifactory/my-gradle-registry
    username: octocat
    password: ${{secrets.MY_ARTIFACTORY_PASSWORD}}
updates:
  - package-ecosystem: "npm"
    directory: "/"
    schedule:
      interval: "weekly"
""")

        expected_result = yaml.load(b"""
version: 2
registries:
  gradle-artifactory:
    type: maven-repository
    url: https://acme.jfrog.io/artifactory/my-gradle-registry
    username: octocat
    password: ${{secrets.MY_ARTIFACTORY_PASSWORD}}
updates:
  - package-ecosystem: "npm"
    directory: "/"
    schedule:
      interval: "weekly"
  - package-ecosystem: 'bundler'
    directory: '/'
    schedule:
      interval: 'weekly'
""")

        result = build_dependabot_file(
            repo, False, [], {}, existing_config, "weekly", "", [], None
        )
        self.assertEqual(result, expected_result)

    def test_build_dependabot_file_with_cooldown_default_days_only(self):
        """Test that cooldown with only default-days is added correctly"""
        repo = MagicMock()
        repo.file_contents.side_effect = lambda filename: filename == "Dockerfile"

        cooldown = {"default-days": 3}
        expected_result = yaml.load(b"""
version: 2
updates:
  - package-ecosystem: 'docker'
    directory: '/'
    schedule:
      interval: 'weekly'
    cooldown:
      default-days: 3
""")
        result = build_dependabot_file(
            repo, False, [], {}, None, "weekly", "", [], None, cooldown
        )
        self.assertEqual(result, expected_result)

    def test_build_dependabot_file_with_cooldown_all_params(self):
        """Test that cooldown with all semver day parameters is added correctly"""
        repo = MagicMock()
        repo.file_contents.side_effect = lambda filename: filename == "Dockerfile"

        cooldown = {
            "default-days": 3,
            "semver-major-days": 7,
            "semver-minor-days": 3,
            "semver-patch-days": 1,
        }
        expected_result = yaml.load(b"""
version: 2
updates:
  - package-ecosystem: 'docker'
    directory: '/'
    schedule:
      interval: 'weekly'
    cooldown:
      default-days: 3
      semver-major-days: 7
      semver-minor-days: 3
      semver-patch-days: 1
""")
        result = build_dependabot_file(
            repo, False, [], {}, None, "weekly", "", [], None, cooldown
        )
        self.assertEqual(result, expected_result)

    def test_build_dependabot_file_with_cooldown_include_exclude(self):
        """Test that cooldown with include/exclude lists is added correctly"""
        repo = MagicMock()
        repo.file_contents.side_effect = lambda filename: filename == "Dockerfile"

        cooldown = {
            "default-days": 5,
            "include": ["lodash", "react*"],
            "exclude": ["critical-pkg"],
        }
        expected_result = yaml.load(b"""
version: 2
updates:
  - package-ecosystem: 'docker'
    directory: '/'
    schedule:
      interval: 'weekly'
    cooldown:
      default-days: 5
      include:
        - 'lodash'
        - 'react*'
      exclude:
        - 'critical-pkg'
""")
        result = build_dependabot_file(
            repo, False, [], {}, None, "weekly", "", [], None, cooldown
        )
        self.assertEqual(result, expected_result)

    def test_build_dependabot_file_with_cooldown_and_groups(self):
        """Test that cooldown works alongside grouped dependencies"""
        repo = MagicMock()
        repo.file_contents.side_effect = lambda filename: filename == "Dockerfile"

        cooldown = {"default-days": 3}
        expected_result = yaml.load(b"""
version: 2
updates:
  - package-ecosystem: 'docker'
    directory: '/'
    schedule:
      interval: 'weekly'
    groups:
      production-dependencies:
        dependency-type: 'production'
      development-dependencies:
        dependency-type: 'development'
    cooldown:
      default-days: 3
""")
        result = build_dependabot_file(
            repo, True, [], {}, None, "weekly", "", [], None, cooldown
        )
        self.assertEqual(result, expected_result)

    def test_build_dependabot_file_with_cooldown_and_registries(self):
        """Test that cooldown works alongside private registries"""
        repo = MagicMock()
        repo.file_contents.side_effect = lambda filename: filename == "package.json"

        extra_config = yaml.load(b"""
npm:
  type: 'npm'
  url: 'https://registry.example.com'
""")
        cooldown = {"default-days": 2}
        expected_result = yaml.load(b"""
version: 2
registries:
  npm:
    type: 'npm'
    url: 'https://registry.example.com'
updates:
  - package-ecosystem: 'npm'
    directory: '/'
    registries:
      - 'npm'
    schedule:
      interval: 'weekly'
    cooldown:
      default-days: 2
""")
        result = build_dependabot_file(
            repo, False, [], {}, None, "weekly", "", [], extra_config, cooldown
        )
        self.assertEqual(result, expected_result)

    def test_build_dependabot_file_without_cooldown(self):
        """Test that no cooldown section is added when cooldown is None"""
        repo = MagicMock()
        repo.file_contents.side_effect = lambda filename: filename == "Dockerfile"

        expected_result = yaml.load(b"""
version: 2
updates:
  - package-ecosystem: 'docker'
    directory: '/'
    schedule:
      interval: 'weekly'
""")
        result = build_dependabot_file(
            repo, False, [], {}, None, "weekly", "", [], None, None
        )
        self.assertEqual(result, expected_result)


if __name__ == "__main__":
    unittest.main()
