from dataclasses import dataclass
import logging
import os
import sqlite3
from typing import List, Dict

from weather.utils.logger import configure_logger
from weather.utils.sql_utils import get_db_connection


logger = logging.getLogger(__name__)
configure_logger(logger)


@dataclass
class user:
    id: int
    username: str
    email: str
    password: str


def create_user(id: str, username: str, email: str, password: str) -> None:
    """
    Creates a new user in the users table.

    Args:
        artist (str): The artist's name.
        title (str): The song title.
        year (int): The year the song was released.
        genre (str): The song genre.
        duration (int): The duration of the song in seconds.

    Raises:
        ValueError: If year or duration are invalid.
        sqlite3.IntegrityError: If a song with the same compound key (artist, title, year) already exists.
        sqlite3.Error: For any other database errors.
    """
    # Validate the required fields
    ## check if it's in the database?
    if not isinstance(username, str):
        raise ValueError(f"Invalid username type provided: {username}.")
    if not isinstance(password, str) or len(password) <= 8:
        raise ValueError(f"Invalid password length: {len(password)} (must be longer than 8 characters).")
    if not isinstance(email, str) or '@' in email:
        raise ValueError(f"Invalid email.")

    try:
        # Use the context manager to handle the database connection
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO users (username, email, password)
                VALUES (?, ?, ?, ?, ?)
            """, (username, email, password))
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
    Retrieves all songs that are not marked as deleted from the catalog.

    Args:
        sort_by_play_count (bool): If True, sort the songs by play count in descending order.

    Returns:
        list[dict]: A list of dictionaries representing all non-deleted songs with play_count.

    Logs:
        Warning: If the catalog is empty.
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            logger.info("Attempting to retrieve all non-deleted songs from the catalog")

            # Determine the sort order based on the 'sort_by_play_count' flag
            query = """
                SELECT id, username, email, password
                FROM users
            """

            cursor.execute(query)
            rows = cursor.fetchall()

            if not rows:
                logger.warning("The song catalog is empty.")
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
    Increments the play count of a song by song ID.

    Args:
        song_id (int): The ID of the song whose play count should be incremented.

    Raises:
        ValueError: If the song does not exist or is marked as deleted.
        sqlite3.Error: If there is a database error.
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            logger.info("Attempting to update password for username with ID %d", id)

            # Check if the song exists and if it's deleted
            try: 
                cursor.execute("SELECT username FROM users WHERE id = ?", (id))
            except TypeError:
                logger.info("Username with ID %d not found", id)
                raise ValueError(f"Username with ID {id} not found")
            

            # Increment the play count
            cursor.execute("UPDATE password SET password = %s WHERE id = %s", (new_password, id))
            conn.commit()

            logger.info("Password for user with ID: %d", id)

    except sqlite3.Error as e:
        logger.error("Database error while updating password for user with ID %d: %s", id, str(e))
        raise e
    

def update_username(id: int, new_username: str) -> None:
    """
    Increments the play count of a song by song ID.

    Args:
        song_id (int): The ID of the song whose play count should be incremented.

    Raises:
        ValueError: If the song does not exist or is marked as deleted.
        sqlite3.Error: If there is a database error.
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            logger.info("Attempting to update username for email with ID %d", id)

            # Check if the song exists and if it's deleted
            try: 
                cursor.execute("SELECT email FROM users WHERE id = ?", (id))
            except TypeError:
                logger.info("Email with ID %d not found", id)
                raise ValueError(f"Email with ID {id} not found")
            

            # Increment the play count
            cursor.execute("UPDATE username SET username = %s WHERE id = %s", (new_username, id))
            conn.commit()

            logger.info("Password for user with ID: %d", id)

    except sqlite3.Error as e:
        logger.error("Database error while updating password for user with ID %d: %s", id, str(e))
        raise e

