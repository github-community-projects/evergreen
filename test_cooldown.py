"""Tests for the cooldown validation in dependabot_file.py."""

import unittest

from dependabot_file import validate_cooldown_config
from ruamel.yaml import YAML


class TestValidateCooldownConfig(unittest.TestCase):
    """Test the validate_cooldown_config function."""

    def test_valid_default_days_only(self):
        """Test valid cooldown with just default-days"""
        validate_cooldown_config({"default-days": 3})

    def test_valid_ruamel_commented_map(self):
        """Test that ruamel.yaml CommentedMap is accepted as a valid mapping"""
        yaml = YAML()
        cooldown = yaml.load(b"default-days: 5\nsemver-major-days: 14\n")
        validate_cooldown_config(cooldown)

    def test_valid_all_days(self):
        """Test valid cooldown with all day parameters"""
        validate_cooldown_config(
            {
                "default-days": 3,
                "semver-major-days": 7,
                "semver-minor-days": 3,
                "semver-patch-days": 1,
            }
        )

    def test_valid_with_include_exclude(self):
        """Test valid cooldown with include and exclude lists"""
        validate_cooldown_config(
            {
                "default-days": 5,
                "include": ["lodash", "react*"],
                "exclude": ["critical-pkg"],
            }
        )

    def test_valid_zero_days(self):
        """Test that zero is below the minimum and raises ValueError"""
        with self.assertRaises(ValueError):
            validate_cooldown_config({"default-days": 0})

    def test_valid_boundary_min(self):
        """Test that 1 day is the minimum valid value"""
        validate_cooldown_config({"default-days": 1})

    def test_valid_boundary_max(self):
        """Test that 90 days is the maximum valid value"""
        validate_cooldown_config({"default-days": 90})

    def test_invalid_not_a_dict(self):
        """Test that non-dict cooldown raises ValueError"""
        with self.assertRaises(ValueError):
            validate_cooldown_config("not a dict")

    def test_invalid_no_days_keys(self):
        """Test that cooldown without any days key raises ValueError"""
        with self.assertRaises(ValueError):
            validate_cooldown_config({"include": ["lodash"]})

    def test_invalid_negative_days(self):
        """Test that negative days raises ValueError"""
        with self.assertRaises(ValueError):
            validate_cooldown_config({"default-days": -1})

    def test_invalid_days_exceed_max(self):
        """Test that days above 90 raises ValueError"""
        with self.assertRaises(ValueError):
            validate_cooldown_config({"default-days": 91})

    def test_invalid_days_not_int(self):
        """Test that non-integer days raises ValueError"""
        with self.assertRaises(ValueError):
            validate_cooldown_config({"default-days": "three"})

    def test_invalid_days_bool(self):
        """Test that boolean days raises ValueError"""
        with self.assertRaises(ValueError):
            validate_cooldown_config({"default-days": True})

    def test_invalid_unknown_key(self):
        """Test that unknown keys raise ValueError"""
        with self.assertRaises(ValueError):
            validate_cooldown_config({"default-days": 3, "unknown-key": 1})

    def test_invalid_include_not_list(self):
        """Test that non-list include raises ValueError"""
        with self.assertRaises(ValueError):
            validate_cooldown_config({"default-days": 3, "include": "lodash"})

    def test_invalid_include_item_not_string(self):
        """Test that non-string include items raise ValueError"""
        with self.assertRaises(ValueError):
            validate_cooldown_config({"default-days": 3, "include": [123]})

    def test_invalid_include_too_many_items(self):
        """Test that include with more than 150 items raises ValueError"""
        with self.assertRaises(ValueError):
            validate_cooldown_config(
                {
                    "default-days": 3,
                    "include": [f"pkg-{i}" for i in range(151)],
                }
            )

    def test_invalid_exclude_too_many_items(self):
        """Test that exclude with more than 150 items raises ValueError"""
        with self.assertRaises(ValueError):
            validate_cooldown_config(
                {
                    "default-days": 3,
                    "exclude": [f"pkg-{i}" for i in range(151)],
                }
            )


if __name__ == "__main__":
    unittest.main()
