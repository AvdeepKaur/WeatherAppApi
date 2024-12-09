from dotenv import load_dotenv
from flask import Flask, jsonify, make_response, Response, request

from weather.models.user_model import user
from weather.models.favorites_model import PlaylistModel
from weather.utils.sql_utils import check_database_connection, check_table_exists


# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

playlist_model = PlaylistModel()


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

@app.route('/api/add-song-to-playlist', methods=['POST'])
def add_song_to_playlist() -> Response:
    """
    Route to add a song to the playlist by compound key (artist, title, year).

    Expected JSON Input:
        - artist (str): The artist's name.
        - title (str): The song title.
        - year (int): The year the song was released.

    Returns:
        JSON response indicating success of the addition or error message.
    """
    try:
        data = request.get_json()

        artist = data.get('artist')
        title = data.get('title')
        year = data.get('year')

        if not artist or not title or not year:
            return make_response(jsonify({'error': 'Invalid input. Artist, title, and year are required.'}), 400)

        # Lookup the song by compound key
        song = user_model.get_song_by_compound_key(artist, title, year)

        # Add song to playlist
        playlist_model.add_song_to_playlist(song)

        app.logger.info(f"Song added to playlist: {artist} - {title} ({year})")
        return make_response(jsonify({'status': 'success', 'message': 'Song added to playlist'}), 201)

    except Exception as e:
        app.logger.error(f"Error adding song to playlist: {e}")
        return make_response(jsonify({'error': str(e)}), 500)

@app.route('/api/remove-song-from-playlist', methods=['DELETE'])
def remove_song_by_song_id() -> Response:
    """
    Route to remove a song from the playlist by compound key (artist, title, year).

    Expected JSON Input:
        - artist (str): The artist's name.
        - title (str): The song title.
        - year (int): The year the song was released.

    Returns:
        JSON response indicating success of the removal or error message.
    """
    try:
        data = request.get_json()

        artist = data.get('artist')
        title = data.get('title')
        year = data.get('year')

        if not artist or not title or not year:
            return make_response(jsonify({'error': 'Invalid input. Artist, title, and year are required.'}), 400)

        # Lookup the song by compound key
        song = user_model.get_song_by_compound_key(artist, title, year)

        # Remove song from playlist
        playlist_model.remove_song_by_song_id(song.id)

        app.logger.info(f"Song removed from playlist: {artist} - {title} ({year})")
        return make_response(jsonify({'status': 'success', 'message': 'Song removed from playlist'}), 200)

    except Exception as e:
        app.logger.error(f"Error removing song from playlist: {e}")
        return make_response(jsonify({'error': str(e)}), 500)

@app.route('/api/remove-song-from-playlist-by-track-number/<int:track_number>', methods=['DELETE'])
def remove_song_by_track_number(track_number: int) -> Response:
    """
    Route to remove a song from the playlist by track number.

    Path Parameter:
        - track_number (int): The track number of the song to remove.

    Returns:
        JSON response indicating success of the removal or an error message.
    """
    try:
        app.logger.info(f"Removing song from playlist by track number: {track_number}")

        # Remove song by track number
        playlist_model.remove_song_by_track_number(track_number)

        return make_response(jsonify({'status': 'success', 'message': f'Song at track number {track_number} removed from playlist'}), 200)

    except ValueError as e:
        app.logger.error(f"Error removing song by track number: {e}")
        return make_response(jsonify({'error': str(e)}), 404)
    except Exception as e:
        app.logger.error(f"Error removing song from playlist: {e}")
        return make_response(jsonify({'error': str(e)}), 500)

@app.route('/api/clear-playlist', methods=['POST'])
def clear_playlist() -> Response:
    """
    Route to clear all songs from the playlist.

    Returns:
        JSON response indicating success of the operation or an error message.
    """
    try:
        app.logger.info('Clearing the playlist')

        # Clear the entire playlist
        playlist_model.clear_playlist()

        return make_response(jsonify({'status': 'success', 'message': 'Playlist cleared'}), 200)

    except Exception as e:
        app.logger.error(f"Error clearing the playlist: {e}")
        return make_response(jsonify({'error': str(e)}), 500)

############################################################
#
# Play Playlist
#
############################################################

@app.route('/api/play-current-song', methods=['POST'])
def play_current_song() -> Response:
    """
    Route to play the current song in the playlist.

    Returns:
        JSON response indicating success of the operation.
    Raises:
        500 error if there is an issue playing the current song.
    """
    try:
        app.logger.info('Playing current song')
        current_song = playlist_model.get_current_song()
        playlist_model.play_current_song()

        return make_response(jsonify({
            'status': 'success',
            'song': {
                'id': current_song.id,
                'artist': current_song.artist,
                'title': current_song.title,
                'year': current_song.year,
                'genre': current_song.genre,
                'duration': current_song.duration
            }
        }), 200)
    except Exception as e:
        app.logger.error(f"Error playing current song: {e}")
        return make_response(jsonify({'error': str(e)}), 500)


@app.route('/api/play-entire-playlist', methods=['POST'])
def play_entire_playlist() -> Response:
    """
    Route to play all songs in the playlist.

    Returns:
        JSON response indicating success of the operation.
    Raises:
        500 error if there is an issue playing the playlist.
    """
    try:
        app.logger.info('Playing entire playlist')
        playlist_model.play_entire_playlist()
        return make_response(jsonify({'status': 'success'}), 200)
    except Exception as e:
        app.logger.error(f"Error playing playlist: {e}")
        return make_response(jsonify({'error': str(e)}), 500)

@app.route('/api/play-rest-of-playlist', methods=['POST'])
def play_rest_of_playlist() -> Response:
    """
    Route to play the rest of the playlist from the current track.

    Returns:
        JSON response indicating success of the operation.
    Raises:
        500 error if there is an issue playing the rest of the playlist.
    """
    try:
        app.logger.info('Playing rest of the playlist')
        playlist_model.play_rest_of_playlist()
        return make_response(jsonify({'status': 'success'}), 200)
    except Exception as e:
        app.logger.error(f"Error playing rest of the playlist: {e}")
        return make_response(jsonify({'error': str(e)}), 500)

@app.route('/api/rewind-playlist', methods=['POST'])
def rewind_playlist() -> Response:
    """
    Route to rewind the playlist to the first song.

    Returns:
        JSON response indicating success of the operation.
    Raises:
        500 error if there is an issue rewinding the playlist.
    """
    try:
        app.logger.info('Rewinding playlist to the first song')
        playlist_model.rewind_playlist()
        return make_response(jsonify({'status': 'success'}), 200)
    except Exception as e:
        app.logger.error(f"Error rewinding playlist: {e}")
        return make_response(jsonify({'error': str(e)}), 500)

@app.route('/api/get-all-songs-from-playlist', methods=['GET'])
def get_all_songs_from_playlist() -> Response:
    """
    Route to retrieve all songs in the playlist.

    Returns:
        JSON response with the list of songs or an error message.
    """
    try:
        app.logger.info("Retrieving all songs from the playlist")

        # Get all songs from the playlist
        songs = playlist_model.get_all_songs()

        return make_response(jsonify({'status': 'success', 'songs': songs}), 200)

    except Exception as e:
        app.logger.error(f"Error retrieving songs from playlist: {e}")
        return make_response(jsonify({'error': str(e)}), 500)

@app.route('/api/get-song-from-playlist-by-track-number/<int:track_number>', methods=['GET'])
def get_song_by_track_number(track_number: int) -> Response:
    """
    Route to retrieve a song by its track number from the playlist.

    Path Parameter:
        - track_number (int): The track number of the song.

    Returns:
        JSON response with the song details or error message.
    """
    try:
        app.logger.info(f"Retrieving song from playlist by track number: {track_number}")

        # Get the song by track number
        song = playlist_model.get_song_by_track_number(track_number)

        return make_response(jsonify({'status': 'success', 'song': song}), 200)

    except ValueError as e:
        app.logger.error(f"Error retrieving song by track number: {e}")
        return make_response(jsonify({'error': str(e)}), 404)
    except Exception as e:
        app.logger.error(f"Error retrieving song from playlist: {e}")
        return make_response(jsonify({'error': str(e)}), 500)

@app.route('/api/get-current-song', methods=['GET'])
def get_current_song() -> Response:
    """
    Route to retrieve the current song being played.

    Returns:
        JSON response with the current song details or error message.
    """
    try:
        app.logger.info("Retrieving the current song from the playlist")

        # Get the current song
        current_song = playlist_model.get_current_song()

        return make_response(jsonify({'status': 'success', 'current_song': current_song}), 200)

    except Exception as e:
        app.logger.error(f"Error retrieving current song: {e}")
        return make_response(jsonify({'error': str(e)}), 500)

@app.route('/api/get-playlist-length-duration', methods=['GET'])
def get_playlist_length_and_duration() -> Response:
    """
    Route to retrieve both the length (number of songs) and the total duration of the playlist.

    Returns:
        JSON response with the playlist length and total duration or error message.
    """
    try:
        app.logger.info("Retrieving playlist length and total duration")

        # Get playlist length and duration
        playlist_length = playlist_model.get_playlist_length()
        playlist_duration = playlist_model.get_playlist_duration()

        return make_response(jsonify({
            'status': 'success',
            'playlist_length': playlist_length,
            'playlist_duration': playlist_duration
        }), 200)

    except Exception as e:
        app.logger.error(f"Error retrieving playlist length and duration: {e}")
        return make_response(jsonify({'error': str(e)}), 500)

@app.route('/api/go-to-track-number/<int:track_number>', methods=['POST'])
def go_to_track_number(track_number: int) -> Response:
    """
    Route to set the playlist to start playing from a specific track number.

    Path Parameter:
        - track_number (int): The track number to set as the current song.

    Returns:
        JSON response indicating success or an error message.
    """
    try:
        app.logger.info(f"Going to track number: {track_number}")

        # Set the playlist to start at the given track number
        playlist_model.go_to_track_number(track_number)

        return make_response(jsonify({'status': 'success', 'track_number': track_number}), 200)
    except ValueError as e:
        app.logger.error(f"Error going to track number {track_number}: {e}")
        return make_response(jsonify({'error': str(e)}), 400)
    except Exception as e:
        app.logger.error(f"Error going to track number: {e}")
        return make_response(jsonify({'error': str(e)}), 500)

############################################################
#
# Arrange Playlist
#
############################################################

@app.route('/api/move-song-to-beginning', methods=['POST'])
def move_song_to_beginning() -> Response:
    """
    Route to move a song to the beginning of the playlist.

    Expected JSON Input:
        - artist (str): The artist of the song.
        - title (str): The title of the song.
        - year (int): The year the song was released.

    Returns:
        JSON response indicating success or an error message.
    """
    try:
        data = request.get_json()

        artist = data.get('artist')
        title = data.get('title')
        year = data.get('year')

        app.logger.info(f"Moving song to beginning: {artist} - {title} ({year})")

        # Retrieve song by compound key and move it to the beginning
        song = user_model.get_song_by_compound_key(artist, title, year)
        playlist_model.move_song_to_beginning(song.id)

        return make_response(jsonify({'status': 'success', 'song': f'{artist} - {title}'}), 200)
    except Exception as e:
        app.logger.error(f"Error moving song to beginning: {e}")
        return make_response(jsonify({'error': str(e)}), 500)

@app.route('/api/move-song-to-end', methods=['POST'])
def move_song_to_end() -> Response:
    """
    Route to move a song to the end of the playlist.

    Expected JSON Input:
        - artist (str): The artist of the song.
        - title (str): The title of the song.
        - year (int): The year the song was released.

    Returns:
        JSON response indicating success or an error message.
    """
    try:
        data = request.get_json()

        artist = data.get('artist')
        title = data.get('title')
        year = data.get('year')

        app.logger.info(f"Moving song to end: {artist} - {title} ({year})")

        # Retrieve song by compound key and move it to the end
        song = user_model.get_song_by_compound_key(artist, title, year)
        playlist_model.move_song_to_end(song.id)

        return make_response(jsonify({'status': 'success', 'song': f'{artist} - {title}'}), 200)
    except Exception as e:
        app.logger.error(f"Error moving song to end: {e}")
        return make_response(jsonify({'error': str(e)}), 500)

@app.route('/api/move-song-to-track-number', methods=['POST'])
def move_song_to_track_number() -> Response:
    """
    Route to move a song to a specific track number in the playlist.

    Expected JSON Input:
        - artist (str): The artist of the song.
        - title (str): The title of the song.
        - year (int): The year the song was released.
        - track_number (int): The new track number to move the song to.

    Returns:
        JSON response indicating success or an error message.
    """
    try:
        data = request.get_json()

        artist = data.get('artist')
        title = data.get('title')
        year = data.get('year')
        track_number = data.get('track_number')

        app.logger.info(f"Moving song to track number {track_number}: {artist} - {title} ({year})")

        # Retrieve song by compound key and move it to the specified track number
        song = user_model.get_song_by_compound_key(artist, title, year)
        playlist_model.move_song_to_track_number(song.id, track_number)

        return make_response(jsonify({'status': 'success', 'song': f'{artist} - {title}', 'track_number': track_number}), 200)
    except Exception as e:
        app.logger.error(f"Error moving song to track number: {e}")
        return make_response(jsonify({'error': str(e)}), 500)

@app.route('/api/swap-songs-in-playlist', methods=['POST'])
def swap_songs_in_playlist() -> Response:
    """
    Route to swap two songs in the playlist by their track numbers.

    Expected JSON Input:
        - track_number_1 (int): The track number of the first song.
        - track_number_2 (int): The track number of the second song.

    Returns:
        JSON response indicating success or an error message.
    """
    try:
        data = request.get_json()

        track_number_1 = data.get('track_number_1')
        track_number_2 = data.get('track_number_2')

        app.logger.info(f"Swapping songs at track numbers {track_number_1} and {track_number_2}")

        # Retrieve songs by track numbers and swap them
        song_1 = playlist_model.get_song_by_track_number(track_number_1)
        song_2 = playlist_model.get_song_by_track_number(track_number_2)
        playlist_model.swap_songs_in_playlist(song_1.id, song_2.id)

        return make_response(jsonify({
            'status': 'success',
            'swapped_songs': {
                'track_1': {'id': song_1.id, 'artist': song_1.artist, 'title': song_1.title},
                'track_2': {'id': song_2.id, 'artist': song_2.artist, 'title': song_2.title}
            }
        }), 200)
    except Exception as e:
        app.logger.error(f"Error swapping songs in playlist: {e}")
        return make_response(jsonify({'error': str(e)}), 500)

############################################################
#
# Leaderboard / Stats
#
############################################################

@app.route('/api/song-leaderboard', methods=['GET'])
def get_song_leaderboard() -> Response:
    """
    Route to get a list of all sorted by play count.

    Returns:
        JSON response with a sorted leaderboard of songs.
    Raises:
        500 error if there is an issue generating the leaderboard.
    """
    try:
        app.logger.info("Generating song leaderboard sorted")
        leaderboard_data = user_model.get_all_songs(sort_by_play_count=True)
        return make_response(jsonify({'status': 'success', 'leaderboard': leaderboard_data}), 200)
    except Exception as e:
        app.logger.error(f"Error generating leaderboard: {e}")
        return make_response(jsonify({'error': str(e)}), 500)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
