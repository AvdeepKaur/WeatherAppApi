from dotenv import load_dotenv
from flask import Flask, jsonify, make_response, Response, request

from weather.models.user_model import user
from weather.models.favorites_model import PlaylistModel
from weather.utils.sql_utils import check_database_connection, check_table_exists


# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

playlist_model = PlaylistModel()

favorites_model = FavoritesModel()


####################################################
#
# Healthchecks
#
####################################################

@app.route('/api/health', methods=['GET'])
def healthcheck() -> Response:
    """
    Health check route to verify the service is running.

    Returns:
        JSON response indicating the health status of the service.
    """
    app.logger.info('Health check')
    return make_response(jsonify({'status': 'healthy'}), 200)


@app.route('/api/db-check', methods=['GET'])
def db_check() -> Response:
    """
    Route to check if multiple database connections and their respective tables are functional.

    Returns:
        JSON response indicating the database health status.
    Raises:
        404 error if there is an issue with the database.
    """

    try:
        app.logger.info("Checking database connection...")
        check_database_connection()
        app.logger.info("Database connection is OK.")
        app.logger.info("Checking if users table exists...")
        check_table_exists("users")
        app.logger.info("users table exists.")
        app.logger.info("Checking if user_favorites table exists...")
        check_table_exists("user_favorites")
        app.logger.info("user_favorites table exists.")
        return make_response(jsonify({'database_status': 'healthy'}), 200)
    except Exception as e:
        return make_response(jsonify({'error': str(e)}), 404)


##########################################################
#
# User Management
#
##########################################################

@app.route('/api/create-user', methods=['POST'])
def add_user() -> Response:
    """
    Route to add a new song to the playlist.

    Expected JSON Input:
        id (str): The user id.
        username (str): The username of the user.
        email (str): The email used by the user.
        password (str): The password associated with the user.

    Returns:
        JSON response indicating the success of the user addition.
    
    Raises:
        400 error if input validation fails.
        500 error if there is an issue adding the user to db.
    """
    app.logger.info('Adding a new user to the db')
    try:
        data = request.get_json()

        id = data.get('id')
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')

        if not id or not username or not email  or not password:
            return make_response(jsonify({'error': 'Invalid input, all fields are required with valid values'}), 400)

        # Add the user to the db
        app.logger.info('Adding user: %s - %s', id, username)
        user_model.create_song(id=id, username=username, email=email, password=password)
        app.logger.info("User added to db: %s - %s", id, username)
        return make_response(jsonify({'status': 'success', 'user': id}), 201)
    except Exception as e:
        app.logger.error("Failed to add user: %s", str(e))
        return make_response(jsonify({'error': str(e)}), 500)

@app.route('/api/get-all-users', methods=['GET'])
def get_all_users() -> Response:
    """
    Route to retrieve all users in the db.

    Returns:
        JSON response with the list of users or error message.
    """
    try:
        app.logger.info("Retrieving all users from the db")
        users = user_model.get_all_users()

        return make_response(jsonify({'status': 'success', 'users': users}), 200)
    except Exception as e:
        app.logger.error(f"Error retrieving users: {e}")
        return make_response(jsonify({'error': str(e)}), 500)

@app.route('/api/update-password', methods=['PUT'])
def update_password() -> Response:
    """
    Route to update passwords 

    Expected JSON Input:
        id (int): The ID of the user whose password we want to update.
        new_password(str): The new password we want to replace the old password with. 

    Returns:
        JSON response indicating success of password update

    Raises:
        400 error if input validation fails.
        404 error if the user ID does not exist.
        500 error if there is a database error.
    """
    try:
        app.logger.info("Received request to update password")
        data = request.get_json()

        id = data.get('id')
        new_password = data.get('new_password')

        if not id or not new_password:
            return make_response(jsonify({'error': 'Invalid input. ID and new_password are required.'}), 400)

        # Call the update_password function
        app.logger.info("Updating password for user with ID %d", id)
        try:
            user_model.update_password(id=id, new_password=new_password)
        except ValueError as ve:
            app.logger.error(str(ve))
            return make_response(jsonify({'error': str(ve)}), 404)

        app.logger.info("Password updated successfully for user with ID %d", id)
        return make_response(jsonify({'status': 'success', 'message': f'Password updated for user ID {id}'}), 200)

    except Exception as e:
        app.logger.error("An unexpected error occurred: %s", str(e))
        return make_response(jsonify({'error': 'An unexpected error occurred.'}), 500)

@app.route('/api/update-username', methods=['PUT'])
def update_username() -> Response:
    """
    Route to update passwords 

    Expected JSON Input:
        id (int): The ID of the user whose username we want to update.
        new_username(str): The new username we want to replace the old username with. 

    Returns:
        JSON response indicating success of username update

    Raises:
        400 error if input validation fails.
        404 error if the user ID does not exist.
        500 error if there is a database error.
    """
    try:
        app.logger.info("Received request to update username")
        data = request.get_json()

        id = data.get('id')
        new_username = data.get('new_username')

        if not id or not new_username:
            return make_response(jsonify({'error': 'Invalid input. ID and new_username are required.'}), 400)

        # Call the update_password function
        app.logger.info("Updating password for user with ID %d", id)
        try:
            user_model.update_username(id=id, new_username=new_username)
        except ValueError as ve:
            app.logger.error(str(ve))
            return make_response(jsonify({'error': str(ve)}), 404)

        app.logger.info("Username updated successfully for user with ID %d", id)
        return make_response(jsonify({'status': 'success', 'message': f'Username updated for user ID {id}'}), 200)

    except Exception as e:
        app.logger.error("An unexpected error occurred: %s", str(e))
        return make_response(jsonify({'error': 'An unexpected error occurred.'}), 500)


############################################################
#
# Favorites Management
#
############################################################

@app.route('/api/add-user', methods=['POST'])
def add_user() -> Response:
    try:
        data = request.get_json()
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')

        if not username or not email or not password:
            return make_response(jsonify({'error': 'Invalid input. Username, email, and password are required.'}), 400)

        user = User(username=username, email=email, password=password, favorite_locations=[])
        favorites_model.add_user(user)

        logger.info(f"User added: {username}")
        return make_response(jsonify({'status': 'success', 'message': f'User {username} added successfully.'}), 201)

    except Exception as e:
        logger.error(f"Error adding user: {e}")
        return make_response(jsonify({'error': str(e)}), 500)


@app.route('/api/remove-user', methods=['DELETE'])
def remove_user() -> Response:
    try:
        data = request.get_json()
        user_id = data.get('user_id')

        if not user_id:
            return make_response(jsonify({'error': 'User ID is required.'}), 400)

        favorites_model.remove_user(user_id)

        logger.info(f"User removed: {user_id}")
        return make_response(jsonify({'status': 'success', 'message': f'User {user_id} removed successfully.'}), 200)

    except Exception as e:
        logger.error(f"Error removing user: {e}")
        return make_response(jsonify({'error': str(e)}), 500)


@app.route('/api/get-user', methods=['GET'])
def get_user() -> Response:
    try:
        user_id = request.args.get('user_id', type=int)

        if not user_id:
            return make_response(jsonify({'error': 'User ID is required.'}), 400)

        user = favorites_model.get_user(user_id)

        return make_response(jsonify({
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'favorite_locations': user.favorite_locations
        }), 200)

    except Exception as e:
        logger.error(f"Error getting user: {e}")
        return make_response(jsonify({'error': str(e)}), 500)


@app.route('/api/add-favorite-location', methods=['POST'])
def add_favorite_location() -> Response:
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        location = data.get('location')

        if not user_id or not location:
            return make_response(jsonify({'error': 'User ID and location are required.'}), 400)

        favorites_model.add_favorite_location(user_id, location)

        logger.info(f"Added favorite location {location} for user {user_id}")
        return make_response(jsonify({'status': 'success', 'message': 'Location added to favorites.'}), 201)

    except Exception as e:
        logger.error(f"Error adding favorite location: {e}")
        return make_response(jsonify({'error': str(e)}), 500)


@app.route('/api/remove-favorite-location', methods=['DELETE'])
def remove_favorite_location() -> Response:
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        location = data.get('location')

        if not user_id or not location:
            return make_response(jsonify({'error': 'User ID and location are required.'}), 400)

        favorites_model.remove_favorite_location(user_id, location)

        logger.info(f"Removed favorite location {location} for user {user_id}")
        return make_response(jsonify({'status': 'success', 'message': 'Location removed from favorites.'}), 200)

    except Exception as e:
        logger.error(f"Error removing favorite location: {e}")
        return make_response(jsonify({'error': str(e)}), 500)


@app.route('/api/get-favorite-locations', methods=['GET'])
def get_favorite_locations() -> Response:
    try:
        user_id = request.args.get('user_id', type=int)

        if not user_id:
            return make_response(jsonify({'error': 'User ID is required.'}), 400)

        locations = favorites_model.get_favorite_locations(user_id)

        return make_response(jsonify({'favorite_locations': locations}), 200)

    except Exception as e:
        logger.error(f"Error getting favorite locations: {e}")
        return make_response(jsonify({'error': str(e)}), 500)


@app.route('/api/get_favorites_length', methods=['GET'])
def get_favorites_length() -> Response:
    try:
        length = favorites_model.get_favorites_length()
        return make_response(jsonify({'favorites_length': length}), 200)

    except Exception as e:
        logger.error(f"Error getting favorites length: {e}")
        return make_response(jsonify({'error': str(e)}), 500)


@app.route('/api/update_weather_data', methods=['PUT'])
def update_weather_data() -> Response:
    try:
        data = request.get_json()
        user_id = data.get('user_id')

        if not user_id:
            return make_response(jsonify({'error': 'User ID is required.'}), 400)

        favorites_model.update_weather_data(user_id)

        logger.info(f"Weather data updated for user {user_id}")
        return make_response(jsonify({'status': 'success', 'message': 'Weather data updated.'}), 200)

    except Exception as e:
        logger.error(f"Error updating weather data: {e}")
        return make_response(jsonify({'error': str(e)}), 500)


@app.route('/api/check-if-empty', methods=['GET'])
def check_if_empty() -> Response:
    try:
        favorites_model.check_if_empty()
        return make_response(jsonify({'status': 'success', 'message': 'Favorites are not empty.'}), 200)

    except Exception as e:
        logger.error(f"Error checking if empty: {e}")
        return make_response(jsonify({'error': str(e)}), 500)


# ############################################################
# #
# # Leaderboard / Stats
# #
# ############################################################

# @app.route('/api/song-leaderboard', methods=['GET'])
# def get_song_leaderboard() -> Response:
#     """
#     Route to get a list of all sorted by play count.

#     Returns:
#         JSON response with a sorted leaderboard of songs.
#     Raises:
#         500 error if there is an issue generating the leaderboard.
#     """
#     try:
#         app.logger.info("Generating song leaderboard sorted")
#         leaderboard_data = user_model.get_all_songs(sort_by_play_count=True)
#         return make_response(jsonify({'status': 'success', 'leaderboard': leaderboard_data}), 200)
#     except Exception as e:
#         app.logger.error(f"Error generating leaderboard: {e}")
#         return make_response(jsonify({'error': str(e)}), 500)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
