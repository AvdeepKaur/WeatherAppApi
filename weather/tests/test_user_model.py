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


   mocker.patch("weather.weather.models.user_model.get_db_connection", mock_get_db_connection)


   return mock_cursor  # Return the mock cursor so we can set expectations per test
######################################################
#
#    Add
#
######################################################

def test_create_user(mock_cursor):
   """ """
   create_user(id=1, username="Username", email="example@example.com", password= "Password")
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
   """
   """
   with pytest.raises(ValueError, match="Invalid username type provided: 1."):
       create_user(username=1, email="example@example.com", password= "Password")


def test_create_user_invalid_password():
   """
   """
   with pytest.raises(ValueError, match="Invalid password length: 4 (must be longer than 8 characters)."):
       create_user(username="Username", email="example@example.com", password= "Pass")


   with pytest.raises(ValueError, match="Invalid password length: 4 (must be longer than 8 characters)."):
       create_user(username="Username", email="example@example.com", password= 1)


def test_create_user_invalid_email():
   """
   """
   with pytest.raises(ValueError, match="Invalid email."):
       create_user(username="Username", email="example.com", password= "Password")
  
   with pytest.raises(ValueError, match="Invalid email."):
       create_user(username="Username", email=1, password= "Password")






def test_create_user_duplicate():
   """
   """
   mock_cursor.execute.side_effect = sqlite3.IntegrityError("UNIQUE constraint failed: user.username, user.email, user.password")
  
   with pytest.raises(ValueError, match="Username 'Username' already exists."):
       create_user(username="Username", email="example@example.com", password= "Password")


#####################################################
#
#    Get user
#
######################################################
def test_get_all_users(mock_cursor):
   """
   """
   mock_cursor.fetchall.return_value = [
       (1, "user A", "emailA@gmail.com", "PasswordA"),
       (2, "user B", "emailB@gmail.com", "PasswordB"),
       (3, "user C", "emailC@gmail.com", "PasswordC")
   ]
   songs = get_all_songs()


   expected_result = [
       {"id": 1, "username": "user A", "email": "emailA@gmail.com", "password": "PasswordA" },
       {"id": 2, "username": "user B", "email": "emailB@gmail.com", "password": "PasswordB" },
       {"id": 3, "username": "user C", "email": "emailC@gmail.com", "password": "PasswordC"}
   ]
   actual_query = normalize_whitespace(mock_cursor.execute.call_args[0][0])
   assert actual_query == expected_query, "The SQL query did not match the expected structure."




#####################################################
#
#    Update
#
######################################################


def test_update_password():
   """
   """
   mock_cursor.fetchone.return_value = ["Username"]  # Mock that the user exists
   user_id = 1
   new_password = "newSecurePassword"


   update_password(user_id, new_password)


   expected_query = normalize_whitespace(
       "UPDATE password SET password = ? WHERE id = ?"
   )
   actual_query = normalize_whitespace(
       mock_cursor.execute.call_args_list[1][0][0]
   )
   assert actual_query == expected_query, "The SQL query did not match the expected structure."


   expected_arguments = (new_password, user_id)
   actual_arguments = mock_cursor.execute.call_args_list[1][0][1]
   assert actual_arguments == expected_arguments, (
       f"The SQL query arguments did not match. "
       f"Expected {expected_arguments}, got {actual_arguments}."
   )


def test_update_password_invalid_id():
   """
   """
   mock_cursor.fetchone.return_value = None  # Simulate that the user does not exist


   user_id = 999  # Non-existent user ID
   new_password = "newSecurePassword"


   with pytest.raises(ValueError, match=f"No user found with id {user_id}."):
       update_password(user_id, new_password)


def test_update_username():
   """
   """
   mock_cursor.fetchone.return_value = ["Username"]  # Mock that the user exists
   user_id = 1
   new_username = "newUsername"


   update_username(user_id, new_username)


   expected_query = normalize_whitespace(
       "UPDATE users SET username = ? WHERE id = ?"
   )
   actual_query = normalize_whitespace(
       mock_cursor.execute.call_args_list[1][0][0]
   )
   assert actual_query == expected_query, "The SQL query did not match the expected structure."


   expected_arguments = (new_username, user_id)
   actual_arguments = mock_cursor.execute.call_args_list[1][0][1]
   assert actual_arguments == expected_arguments, (
       f"The SQL query arguments did not match. "
       f"Expected {expected_arguments}, got {actual_arguments}."
   )


def test_update_username_invalid_id():
   """
   """
   mock_cursor.fetchone.return_value = None  # Simulate that the user does not exist


   user_id = 999  # Non-existent user ID
   new_username = "newUsername"


   with pytest.raises(ValueError, match=f"No user found with id {user_id}."):
       update_username(user_id, new_username)




