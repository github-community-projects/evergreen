"""Test the get_bool_env_var and get_int_env_var functions"""

import os
import unittest
from unittest.mock import patch

from env import get_bool_env_var, get_int_env_var


class TestEnv(unittest.TestCase):
    """Test the get_bool_env_var function"""

    @patch.dict(
        os.environ,
        {
            "TEST_BOOL": "true",
        },
        clear=True,
    )
    def test_get_bool_env_var_that_exists_and_is_true(self):
        """Test that gets a boolean environment variable that exists and is true"""
        result = get_bool_env_var("TEST_BOOL", False)
        self.assertTrue(result)

    @patch.dict(
        os.environ,
        {
            "TEST_BOOL": "false",
        },
        clear=True,
    )
    def test_get_bool_env_var_that_exists_and_is_false(self):
        """Test that gets a boolean environment variable that exists and is false"""
        result = get_bool_env_var("TEST_BOOL", False)
        self.assertFalse(result)

    @patch.dict(
        os.environ,
        {
            "TEST_BOOL": "nope",
        },
        clear=True,
    )
    def test_get_bool_env_var_that_exists_and_is_false_due_to_invalid_value(self):
        """Test that gets a boolean environment variable that exists and is false
        due to an invalid value
        """
        result = get_bool_env_var("TEST_BOOL", False)
        self.assertFalse(result)

    @patch.dict(
        os.environ,
        {
            "TEST_BOOL": "false",
        },
        clear=True,
    )
    def test_get_bool_env_var_that_does_not_exist_and_default_value_returns_true(self):
        """Test that gets a boolean environment variable that does not exist
        and default value returns: true
        """
        result = get_bool_env_var("DOES_NOT_EXIST", True)
        self.assertTrue(result)

    @patch.dict(
        os.environ,
        {
            "TEST_BOOL": "true",
        },
        clear=True,
    )
    def test_get_bool_env_var_that_does_not_exist_and_default_value_returns_false(self):
        """Test that gets a boolean environment variable that does not exist
        and default value returns: false
        """
        result = get_bool_env_var("DOES_NOT_EXIST", False)
        self.assertFalse(result)


class TestGetIntEnvVar(unittest.TestCase):
    """Test the get_int_env_var function"""

    @patch.dict(
        os.environ,
        {
            "TEST_INT": "not_a_number",
        },
        clear=True,
    )
    def test_get_int_env_var_with_non_integer_value(self):
        """Test that get_int_env_var returns None for non-integer values"""
        result = get_int_env_var("TEST_INT")
        self.assertIsNone(result)


if __name__ == "__main__":
    unittest.main()
