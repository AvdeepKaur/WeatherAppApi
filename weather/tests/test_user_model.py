from contextlib import contextmanager
import re
import sqlite3

import pytest

from weather.weather.models.user_model import (
    user,
    create_user,
    get_all_users,
    update_password,
    update_username,
)

######################################################
#
#    Fixtures
#
######################################################

def normalize_whitespace(sql_query: str) -> str:
    return re.sub(r'\s+', ' ', sql_query).strip()

@pytest.fixture
def mock_cursor(mocker):
    mock_conn = mocker.Mock()
    mock_cursor = mocker.Mock()

    # Mock the connection's cursor
    mock_conn.cursor.return_value = mock_cursor
    mock_cursor.fetchone.return_value = None  # Default return for queries
    mock_cursor.fetchall.return_value = []
    mock_conn.commit.return_value = None

    # Mock the get_db_connection context manager from sql_utils
    @contextmanager
    def mock_get_db_connection():
        yield mock_conn  # Yield the mocked connection object

    mocker.patch("weather.models.user_model.get_db_connection", mock_get_db_connection)

    return mock_cursor  # Return the mock cursor so we can set expectations per test
######################################################
#
#    Add
#
######################################################

def test_create_user(mock_cursor):
    """ """
    create_user(username="Username", email="example@example.com", password= "Password")
    expected_query = normalize_whitespace("""
        INSERT INTO users (username, email, password)
        VALUES (?, ?, ?)
    """)
    actual_query = normalize_whitespace(mock_cursor.execute.call_args[0][0])
    assert actual_query == expected_query, "The SQL query did not match the expected structure."
    actual_arguments = mock_cursor.execute.call_args[0][1]
    expected_arguments = ("Username", "example@example.com", "Password")
    assert actual_arguments == expected_arguments, f"The SQL query arguments did not match. Expected {expected_arguments}, got {actual_arguments}."

def test_create_user_invalid_username():

def test_create_user_invalid_password():

def test_create_user_invalid_email():

def test_create_user_duplicate():
"""
"""


