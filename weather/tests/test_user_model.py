from contextlib import contextmanager
import re
import sqlite3

import pytest

from weather.models.user_model import (
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

   mock_conn.cursor.return_value = mock_cursor
   mock_cursor.fetchone.return_value = None  
   mock_cursor.fetchall.return_value = []
   mock_conn.commit.return_value = None

   @contextmanager
   def mock_get_db_connection():
       yield mock_conn  


   mocker.patch("weather.models.user_model.get_db_connection", mock_get_db_connection)


   return mock_cursor  
######################################################
#
#    Add
#
######################################################

def test_create_user(mock_cursor):
   """ """
   create_user(id=1, username="Username", email="example@example.com", password= "Passwords")
   expected_query = normalize_whitespace("""
       INSERT INTO users (username, email, password)
       VALUES (?, ?, ?)
   """)
   actual_query = normalize_whitespace(mock_cursor.execute.call_args[0][0])
   assert actual_query == expected_query, "The SQL query did not match the expected structure."
   actual_arguments = mock_cursor.execute.call_args[0][1]
   expected_arguments = ("Username", "example@example.com", "Passwords")
   assert actual_arguments == expected_arguments, f"The SQL query arguments did not match. Expected {expected_arguments}, got {actual_arguments}."

def test_create_user_invalid_username():
   """
   """
   with pytest.raises(ValueError, match="Invalid username type provided: 1."):
       create_user(id=1,username=1, email="example@example.com", password= "Passwords")


def test_create_user_invalid_password():
   """
   """
   with pytest.raises(ValueError, match=r"Invalid password length: 4 \(must be longer than 8 characters\)\."):
       create_user(id=1, username="Username", email="example@example.com", password= "Pass")


def test_create_user_invalid_email():
   """
   """
   with pytest.raises(ValueError, match="Invalid email."):
       create_user(id=1,username="Username", email="example.com", password= "Passwords")
  
   with pytest.raises(ValueError, match="Invalid email."):
       create_user(id=1, username="Username", email=1, password= "Passwords")






def test_create_user_duplicate(mock_cursor):
   """
   """
   mock_cursor.execute.side_effect = sqlite3.IntegrityError("UNIQUE constraint failed: user.username, user.email, user.password")

   with pytest.raises(ValueError, match="Username 'Username' already exists."):
       create_user(id=1, username="Username", email="example@example.com", password= "Passwords")



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
   
   users = get_all_users()

   expected_result = [
       {"id": 1, "username": "user A", "email": "emailA@gmail.com", "password": "PasswordA" },
       {"id": 2, "username": "user B", "email": "emailB@gmail.com", "password": "PasswordB" },
       {"id": 3, "username": "user C", "email": "emailC@gmail.com", "password": "PasswordC"}
   ]
   
   expected_query = normalize_whitespace("""
       SELECT id, username, email, password FROM users
   """)
   
   actual_query = normalize_whitespace(mock_cursor.execute.call_args[0][0])
   assert actual_query == expected_query, "The SQL query did not match the expected structure."




#####################################################
#
#    Update
#
######################################################


def test_update_password(mock_cursor):
    """
    Test case for updating a user's password.
    """
    mock_cursor.fetchone.return_value = ["Username"]  
    
    user_id = 1
    new_password = "newSecurePassword"
    
    update_password(user_id, new_password)

    expected_select_query = normalize_whitespace(
        "SELECT username FROM users WHERE id = ?"
    )
    actual_select_query = normalize_whitespace(
        mock_cursor.execute.call_args_list[0][0][0]  
    )

    assert actual_select_query == expected_select_query, (
        f"The SELECT query did not match the expected structure. "
        f"Expected: {expected_select_query}, got: {actual_select_query}"
    )

    expected_update_query = normalize_whitespace(
        "UPDATE users SET password = ? WHERE id = ?"
    )
    actual_update_query = normalize_whitespace(
        mock_cursor.execute.call_args_list[1][0][0]  
    )

    assert actual_update_query == expected_update_query, (
        f"The UPDATE query did not match the expected structure. "
        f"Expected: {expected_update_query}, got: {actual_update_query}"
    )

    expected_arguments = (new_password, user_id)
    actual_arguments = mock_cursor.execute.call_args_list[1][0][1]  

    assert actual_arguments == expected_arguments, (
        f"The SQL query arguments did not match. "
        f"Expected {expected_arguments}, got {actual_arguments}."
    )



def test_update_password_invalid_id(mock_cursor):
    """
    Test case when updating password for a non-existing user.
    """
    mock_cursor.fetchone.return_value = None 
    
    user_id = 999
    new_password = "newSecurePassword"
    
    with pytest.raises(ValueError, match=f"No user found with id {user_id}."):
        update_password(user_id, new_password)




def test_update_username(mock_cursor):
    """
    Test case for updating a user's username.
    """
    mock_cursor.fetchone.return_value = ["Username"] 
    user_id = 1
    new_username = "newUsername"

    update_username(user_id, new_username)

    expected_query = normalize_whitespace(
        "UPDATE username SET username = %s WHERE id = %s"
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


def test_update_username_invalid_id(mock_cursor):
    """
    Test case when updating username for a non-existing user.
    """
    mock_cursor.fetchone.return_value = None  

    user_id = 999 
    new_username = "newUsername"

    with pytest.raises(ValueError, match=f"No user found with id {user_id}."):
        update_username(user_id, new_username)

