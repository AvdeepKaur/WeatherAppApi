import pytest
import sqlite3
from weather.models.favorites_model import FavoritesModel


######################################################
#
#    Fixtures
#
######################################################

@pytest.fixture
def db_path(tmp_path):
    """Fixture to provide a temporary database path."""
    return str(tmp_path / "test.db")

@pytest.fixture
def favorites_model(db_path):
    """Fixture to provide a new instance of FavoritesModel for each test."""
    model = FavoritesModel(db_path)
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                username TEXT NOT NULL,
                email TEXT NOT NULL,
                password TEXT NOT NULL
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_favorites (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                location_name TEXT,
                latitude REAL,
                longitude REAL,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        """)
    return model

@pytest.fixture
def sample_user1(db_path):
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users (id, username, email, password) VALUES (?, ?, ?, ?)",
                       (1, 'username1', 'email1@email.com', 'password1'))
    return {"id": 1, "username": 'username1', "email": 'email1@email.com'}

@pytest.fixture
def sample_location1():
    return {'name': 'New York', 'lat': 40.7128, 'lon': -74.0060}

@pytest.fixture
def sample_location2():
    return {'name': 'London', 'lat': 51.5074, 'lon': -0.1278}

##################################################
# User Management Test Cases
##################################################

def test_get_user(favorites_model, sample_user1):
    """Test retrieving a user from the FavoritesModel."""
    user = favorites_model.get_user(1)
    assert user['id'] == 1
    assert user['username'] == 'username1'

def test_get_nonexistent_user(favorites_model):
    """Test error when retrieving a nonexistent user from the FavoritesModel."""
    with pytest.raises(ValueError, match="User with ID 999 not found"):
        favorites_model.get_user(999)

##################################################
# Favorites Management Test Cases
##################################################

def test_add_favorite_location(favorites_model, sample_user1, sample_location1):
    """Test adding a favorite location for a user."""
    favorites_model.add_favorite_location(1, sample_location1)
    locations = favorites_model.get_favorite_locations(1)
    assert len(locations) == 1
    assert locations[0]['name'] == sample_location1['name']

def test_get_favorite_locations(favorites_model, sample_user1, sample_location1, sample_location2):
    """Test retrieving all favorite locations for a user."""
    favorites_model.add_favorite_location(1, sample_location1)
    favorites_model.add_favorite_location(1, sample_location2)
    locations = favorites_model.get_favorite_locations(1)
    assert len(locations) == 2
    assert any(loc['name'] == sample_location1['name'] for loc in locations)
    assert any(loc['name'] == sample_location2['name'] for loc in locations)

##################################################
# Weather Data Management Test Cases
##################################################

def test_update_weather_data(favorites_model, sample_user1, sample_location1, mocker):
    """Test updating weather data for a user's favorite locations."""
    favorites_model.add_favorite_location(1, sample_location1)
    
    mock_requests = mocker.patch('requests.get')
    mock_response = mocker.Mock()
    mock_response.json.return_value = {'current': {'temp_c': 20}}
    mock_response.raise_for_status.return_value = None
    mock_requests.return_value = mock_response

    favorites_model.update_weather_data(1)
    
    # Note: This test might need to be adjusted based on how weather data is stored
    # You might need to add a method to retrieve weather data or modify get_favorite_locations to include it

##################################################
# Utility Function Test Cases
##################################################

def test_check_if_empty_with_full_favorites(favorites_model, sample_location1):
    """Test check_if_empty does not raise error if favorites is not empty."""
    favorites_model.add_favorite_location(1, sample_location1)
    try:
        favorites_model.check_if_empty()
    except ValueError:
        pytest.fail("check_if_empty raised ValueError unexpectedly on non-empty favorites")

def test_check_if_empty_with_empty_favorites(favorites_model):
    """Test check_if_empty raises error when favorites is empty."""
    with pytest.raises(ValueError, match="No favorite locations found"):
        favorites_model.check_if_empty()