from dataclasses import dataclass, field
import logging
import os
import sqlite3
from typing import List, Dict

from weather.utils.logger import configure_logger
from weather.utils.sql_utils import get_db_connection

import bcrypt


logger = logging.getLogger(__name__)
configure_logger(logger)


@dataclass
class User:
    id: int
    username: str
    email: str
    password: str
    salt: str
    favorite_locations: List[Dict] = field(default_factory=list)


def create_user(id: str, username: str, email: str, password: str) -> None:
    """
    Creates a new user in the users table.

    Args:
        id (str): The user id.
        username (str): The username of the user.
        email (str): The email used by the user.
        password (str): The password associated with the user.
        salt (str): Password salt to decode.

    Raises:
        ValueError: If username is invalid.
        ValueError: If password is invalid.
        ValueError: If email is invalid
        ValueError: If username already exists. 
        sqlite3.Error: Error when creating a database for that user. 
    """
    # Validate the required fields
    ## check if it's in the database?
    if not isinstance(username, str):
        raise ValueError(f"Invalid username type provided: {username}.")
    if not isinstance(password, str) or len(password) <= 8:
        raise ValueError(f"Invalid password length: {len(password)} (must be longer than 8 characters).")
    if not isinstance(email, str) or '@' not in email:
        raise ValueError(f"Invalid email.")
    
    try:
        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)

        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO users (username, email, password, salt)
                VALUES (?, ?, ?, ?)
            """, (username, email, hashed_password.decode('utf-8'), salt.decode('utf-8')))
            conn.commit()

            logger.info("User created successfully: %s", username)

    except sqlite3.IntegrityError as e:
        logger.error("Username with '%s' already exists.", username)
        raise ValueError(f"Username '{username}' already exists.") from e
    except sqlite3.Error as e:
        logger.error("Database error while creating user: %s", str(e))
        raise sqlite3.Error(f"Database error: {str(e)}")


def get_all_users() -> list[dict]:
    """
    Retrieves all users that have created an account.

    Returns:
        list[dict]: A list of dictionaries representing all users.

    Logs:
        Warning: If the catalog is empty.
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            logger.info("Attempting to retrieve all non-users from the db")

            # Determine the sort order based on the 'sort_by_play_count' flag
            query = """
                SELECT id, username, email, password
                FROM users
            """

            cursor.execute(query)
            rows = cursor.fetchall()

            if not rows:
                logger.warning("The user catalog is empty.")
                return []

            users = [
                {
                    "id": row[0],
                    "username": row[1],
                    "email": row[2],
                }
                for row in rows
            ]
            logger.info("Retrieved %d users from the catalog", len(users))
            return users

    except sqlite3.Error as e:
        logger.error("Database error while retrieving all users: %s", str(e))
        raise e


def update_password(id: int, new_password: str) -> None:
    """
    Updates password of user by user id.

    Args:
        id (int): The ID of the user whose password we want to update.
        new_password(str): The new password we want to replace the old password with. 

    Raises:
        ValueError: If the username with the id does not exist.
        sqlite3.Error: If there is a database error.
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            logger.info("Attempting to update password for user with ID %d", id)

            cursor.execute("SELECT username FROM users WHERE id = ?", (id,))
            result = cursor.fetchone()
            if result is None:
                logger.info("User with ID %d not found", id)
                raise ValueError(f"No user found with id {id}.")
            
            salt = bcrypt.gensalt()
            hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), salt)

            cursor.execute(
                "UPDATE users SET password = ?, salt = ? WHERE id = ?",
                (hashed_password.decode('utf-8'), salt.decode('utf-8'), id)
            )
            conn.commit()

            logger.info("Password updated for user with ID: %d", id)

    except sqlite3.Error as e:
        logger.error("Database error while updating password for user with ID %d: %s", id, str(e))
        raise e
    

def update_username(id: int, new_username: str) -> None:
    """
    Updates the username by user ID.

    Args:
        id (int): The ID of the user whose username should be updated.
        new_username (str): The new username we want.

    Raises:
        ValueError: If the user does not exist.
        sqlite3.Error: If there is a database error.
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            logger.info("Attempting to update username for user with ID %d", id)

            cursor.execute("SELECT username FROM users WHERE id = ?", (id,))
            user = cursor.fetchone()

            if user is None:
                logger.info("User with ID %d not found", id)
                raise ValueError(f"No user found with id {id}.")

            cursor.execute("UPDATE users SET username = ? WHERE id = ?", (new_username, id))
            conn.commit()

            logger.info("Username updated for user with ID: %d", id)

    except sqlite3.Error as e:
        logger.error("Database error while updating username for user with ID %d: %s", id, str(e))
        raise e
