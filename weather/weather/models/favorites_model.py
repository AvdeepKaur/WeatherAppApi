import logging
from typing import List, Dict

import requests
import sqlite3
from weather.models.user_model import User
from weather.utils.logger import configure_logger
from weather.utils.geocoding_utils import get_latitude_longitude

logger = logging.getLogger(__name__)
configure_logger(logger)

class FavoritesModel:
    """
    A class to manage the favorited locations for users.

    Attributes:
        db_path: path to the user database
    """

    def __init__(self, db_path):
        self.db_path = db_path


    ##################################################
    # User Management Functions
    ##################################################
    def get_user(self, user_id: int) -> dict:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, username, email FROM users WHERE id = ?", (user_id,))
            user = cursor.fetchone()
            if user is None:
                raise ValueError(f"User with ID {user_id} not found")
            return {"id": user[0], "username": user[1], "email": user[2]}
    
    ##################################################
    # Favorites Retrieval Functions
    ##################################################
        
    def add_favorite_location(self, user_id: int, location: dict) -> None:
        """
        Adds a favorite location for a user to the database.

        Args:
        user_id (int): The ID of the user adding the favorite location.
        location (dict): A dictionary containing the location details.

        Raises:
            sqlite3.Error: If there is an error executing the SQL query or committing the transaction.
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO user_favorites (user_id, location_name, latitude, longitude) VALUES (?, ?, ?, ?)",
                (user_id, location['name'], location.get('lat'), location.get('lon'))
            )
            conn.commit()


    def remove_favorite_location(self, user_id: int, location: Dict) -> None:
        """
        Removes a favorite location for a user.

        Args:
            user_id (int): The ID of the user.
            location (Dict): The location to remove from favorites.
        """
        user = self.get_user(user_id)
        user.favorite_locations = [loc for loc in user.favorite_locations if loc != location]
        logger.info(f"Removed location {location} from favorites for user {user_id}")

    def get_favorite_locations(self, user_id: int) -> List[Dict]:
        """
        Retrieves all favorite locations for a user.

        Args:
            user_id (int): The ID of the user.

        Returns:
            List[Dict]: A list of favorite locations for the user.
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT location_name, latitude, longitude
                FROM user_favorites
                WHERE user_id = ?
            """, (user_id,))
            locations = cursor.fetchall()
            return [
                {
                    "name": loc[0],
                    "lat": loc[1],
                    "lon": loc[2]
                }
                for loc in locations
            ]
    
    def get_favorites_length(self) -> int:
        """
        Returns the total number of favorite locations across all users.
        """
        return sum(len(user.favorite_locations) for user in self.users)
    
    ##################################################
    # Weather Data Management Functions
    ##################################################

    def update_weather_data(self, user_id: int) -> None:
        """
        Updates the weather data for all favorite locations of a user.

        Args:
            user_id (int): The ID of the user.

        Note:
            This method makes API calls to update weather data.
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # Fetch user's favorite locations
            cursor.execute("""
                SELECT location_name, latitude, longitude
                FROM user_favorites
                WHERE user_id = ?
            """, (user_id,))
            favorite_locations = cursor.fetchall()

            if not favorite_locations:
                logger.error(f"No favorite locations found for user {user_id}")
                raise ValueError(f"No favorite locations found for user {user_id}")

            base_url = "https://api.weatherapi.com/v1/current.json"

            for location in favorite_locations:
                location_name, lat, lon = location

                # Get coordinates if missing
                if lat is None or lon is None:
                    coordinates = get_latitude_longitude(location_name)
                    if coordinates:
                        lat, lon = coordinates
                        # Update database with new coordinates
                        cursor.execute("""
                            UPDATE user_favorites
                            SET latitude = ?, longitude = ?
                            WHERE user_id = ? AND location_name = ?
                        """, (lat, lon, user_id, location_name))
                        conn.commit()
                    else:
                        logger.error(f"Failed to get coordinates for {location_name}")
                        continue

                # Fetch weather data
                params = {
                    "q": f"{lat},{lon}"
                }
                try:
                    response = requests.get(base_url, params=params)
                    response.raise_for_status()
                    weather_data = response.json()

                    # Log weather data update (you can store it in your database if needed)
                    logger.info(f"Updated weather data for location {location_name} for user {user_id}")
                except requests.RequestException as e:
                    logger.error(f"Failed to update weather data for location {location_name} for user {user_id}: {str(e)}")

    ##################################################
    # Utility Functions
    ##################################################

    def check_if_empty(self) -> None:
        """
        Checks if there are any users with favorite locations.

        Raises:
            ValueError: If there are no favorite locations.
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM user_favorites")
            count = cursor.fetchone()[0]

        if count == 0:
            logger.error("No favorite locations found")
            raise ValueError("No favorite locations found")