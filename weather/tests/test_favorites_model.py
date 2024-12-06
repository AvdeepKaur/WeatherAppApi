import pytest
from weather.models.favorites_model import FavoritesModel
from weather.models.user_model import User

@pytest.fixture
def favorites_model():
    """Fixture to provide a new instance of FavoritesModel for each test."""
    return FavoritesModel()

@pytest.fixture
def sample_user1():
    return User(1, 'username1', 'email1@email.com', 'password1')

@pytest.fixture
def sample_user2():
    return User(2, 'username2', 'email2@email.com', 'password2')

@pytest.fixture
def sample_location1():
    return {'name': 'New York', 'lat': 40.7128, 'lon': -74.0060}

@pytest.fixture
def sample_location2():
    return {'name': 'London', 'lat': 51.5074, 'lon': -0.1278}

##################################################
# User Management Test Cases
##################################################

def test_add_user(favorites_model, sample_user1):
    """Test adding a user to the FavoritesModel."""
    favorites_model.add_user(sample_user1)
    assert len(favorites_model.users) == 1
    assert favorites_model.users[0].id == 1

def test_add_duplicate_user(favorites_model, sample_user1):
    """Test error when adding a duplicate user to the FavoritesModel."""
    favorites_model.add_user(sample_user1)
    with pytest.raises(ValueError, match="User with ID 1 already exists"):
        favorites_model.add_user(sample_user1)

def test_remove_user(favorites_model, sample_user1):
    """Test removing a user from the FavoritesModel."""
    favorites_model.add_user(sample_user1)
    favorites_model.remove_user(1)
    assert len(favorites_model.users) == 0

def test_get_user(favorites_model, sample_user1):
    """Test retrieving a user from the FavoritesModel."""
    favorites_model.add_user(sample_user1)
    user = favorites_model.get_user(1)
    assert user.id == 1
    assert user.username == 'username1'

def test_get_nonexistent_user(favorites_model):
    """Test error when retrieving a nonexistent user from the FavoritesModel."""
    with pytest.raises(ValueError, match="User with ID 999 not found"):
        favorites_model.get_user(999)

##################################################
# Favorites Management Test Cases
##################################################

def test_add_favorite_location(favorites_model, sample_user1, sample_location1):
    """Test adding a favorite location for a user."""
    favorites_model.add_user(sample_user1)
    favorites_model.add_favorite_location(1, sample_location1)
    assert len(favorites_model.get_favorite_locations(1)) == 1
    assert favorites_model.get_favorite_locations(1)[0] == sample_location1

def test_add_duplicate_favorite_location(favorites_model, sample_user1, sample_location1):
    """Test error when adding a duplicate favorite location for a user."""
    favorites_model.add_user(sample_user1)
    favorites_model.add_favorite_location(1, sample_location1)
    with pytest.raises(ValueError, match="Location {'name': 'New York', 'lat': 40.7128, 'lon': -74.006} already in favorites for user 1"):
        favorites_model.add_favorite_location(1, sample_location1)

def test_remove_favorite_location(favorites_model, sample_user1, sample_location1):
    """Test removing a favorite location for a user."""
    favorites_model.add_user(sample_user1)
    favorites_model.add_favorite_location(1, sample_location1)
    favorites_model.remove_favorite_location(1, sample_location1)
    assert len(favorites_model.get_favorite_locations(1)) == 0

def test_get_favorite_locations(favorites_model, sample_user1, sample_location1, sample_location2):
    """Test retrieving all favorite locations for a user."""
    favorites_model.add_user(sample_user1)
    favorites_model.add_favorite_location(1, sample_location1)
    favorites_model.add_favorite_location(1, sample_location2)
    locations = favorites_model.get_favorite_locations(1)
    assert len(locations) == 2
    assert sample_location1 in locations
    assert sample_location2 in locations

##################################################
# Weather Data Management Test Cases
##################################################

def test_update_weather_data(favorites_model, sample_user1, sample_location1, mocker):
    """Test updating weather data for a user's favorite locations."""
    favorites_model.add_user(sample_user1)
    favorites_model.add_favorite_location(1, sample_location1)
    
    mock_requests = mocker.patch('requests.get')
    mock_response = mocker.Mock()
    mock_response.json.return_value = {'current': {'temp_c': 20}}
    mock_response.raise_for_status.return_value = None
    mock_requests.return_value = mock_response

    favorites_model.update_weather_data(1)
    
    assert 'weather' in favorites_model.get_favorite_locations(1)[0]
    assert favorites_model.get_favorite_locations(1)[0]['weather']['current']['temp_c'] == 20

##################################################
# Utility Function Test Cases
##################################################

def test_check_if_empty_non_empty_favorites(favorites_model, sample_user1, sample_location1):
    """Test check_if_empty does not raise error if favorites is not empty."""
    favorites_model.add_user(sample_user1)
    favorites_model.add_favorite_location(1, sample_location1)
    try:
        favorites_model.check_if_empty()
    except ValueError:
        pytest.fail("check_if_empty raised ValueError unexpectedly on non-empty favorites")

def test_check_if_empty_empty_favorites(favorites_model):
    """Test check_if_empty raises error when favorites is empty."""
    with pytest.raises(ValueError, match="Favorites is empty"):
        favorites_model.check_if_empty()

def test_get_favorites_length(favorites_model, sample_user1, sample_location1, sample_location2):
    """Test getting the length of the favorites."""
    favorites_model.add_user(sample_user1)
    favorites_model.add_favorite_location(1, sample_location1)
    favorites_model.add_favorite_location(1, sample_location2)
    assert favorites_model.get_favorites_length() == 2, "Expected favorites length to be 2"