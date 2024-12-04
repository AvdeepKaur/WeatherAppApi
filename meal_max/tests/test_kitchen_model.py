from contextlib import contextmanager
import re
import sqlite3

import pytest

from meal_max.models.kitchen_model import (
    Meal, 
    create_meal, 
    clear_meals, 
    delete_meal, 
    get_leaderboard, 
    get_meal_by_id, 
    get_meal_by_name, 
    update_meal_stats
)

######################################################
#
#    Fixtures
#
######################################################

def normalize_whitespace(sql_query: str) -> str:
    return re.sub(r'\s+', ' ', sql_query).strip()

# Mocking the database connection for tests
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

    mocker.patch("meal_max.models.kitchen_model.get_db_connection", mock_get_db_connection)

    return mock_cursor  # Return the mock cursor so we can set expectations per test

######################################################
#
#    Add and delete
#
######################################################

def test_create_meal(mock_cursor):
    """Testing creating a new meal in the catalog."""
    
    create_meal(meal="Ramen", cuisine= "Japanese", price=10, difficulty="LOW")
    
    expected_query = normalize_whitespace("""
        INSERT INTO meals (meal, cuisine, price, difficulty)
        VALUES (?, ?, ?, ?)
    """)

    actual_query = normalize_whitespace(mock_cursor.execute.call_args[0][0])
    assert actual_query == expected_query, "The SQL query did not match the expected structure."

    actual_arguments = mock_cursor.execute.call_args[0][1]
    expected_arguments = ("Ramen", "Japanese", 10, "LOW")
    assert actual_arguments == expected_arguments, f"The SQL query arguments did not match. Expected {expected_arguments}, got {actual_arguments}."

def test_create_meal_duplicate(mock_cursor):
    """Test creating a duplicate meal (should raise an error)."""
    mock_cursor.execute.side_effect = sqlite3.IntegrityError("UNIQUE constraint failed: meals.meal")
    with pytest.raises(ValueError, match=r"Meal with name 'Ramen' already exists.*"):
        create_meal(meal="Ramen", cuisine="Japanese", price=10, difficulty="LOW")

def test_create_meal_invalid_price():
    """Test error when trying to create a meal with an invalid price (e.g., negative duration)"""
    
    with pytest.raises(ValueError, match = "Invalid price: -10. Price must be a positive number."):
        create_meal(meal="Ramen", cuisine= "Japanese", price=-10, difficulty="LOW")

def test_create_meal_invalid_diffuctly():
    """Test error when trying to create a meal with an invalid diffuctly. """
    with pytest.raises(ValueError, match="Invalid difficulty level: invalid. Must be 'LOW', 'MED', or 'HIGH'."):
        create_meal(meal="Ramen", cuisine= "Japanese", price=10, difficulty="invalid")

def test_clear_meals(mock_cursor, mocker):
    """Test clearing the entire meal catalog (removes all meals)."""
    mocker.patch.dict('os.environ', {'SQL_CREATE_TABLE_PATH': 'sql/create_meal_table.sql'})
    mock_open = mocker.patch('builtins.open', mocker.mock_open(read_data="The body of the create statement"))
    clear_meals()
    mock_open.assert_called_once_with('sql/create_meal_table.sql', 'r')
    mock_cursor.executescript.assert_called_once()

def test_delete_meal(mock_cursor): 
    """Test soft delete a meal from the catalog by meal ID."""
    
    mock_cursor.fetchone.return_value = ([False])

    delete_meal(1)

    expected_select_sql = normalize_whitespace("SELECT deleted FROM meals WHERE id = ?")
    expected_update_sql = normalize_whitespace("UPDATE meals SET deleted = TRUE WHERE id = ?")

    actual_select_sql = normalize_whitespace(mock_cursor.execute.call_args_list[0][0][0])
    actual_update_sql = normalize_whitespace(mock_cursor.execute.call_args_list[1][0][0])
    assert actual_select_sql == expected_select_sql, f"The SELECT query did not match the expected structure. Expected: {expected_select_sql}, Got: {actual_select_sql}"
    assert actual_update_sql == expected_update_sql, f"The UPDATE query did not match the expected structure. Expected: {expected_update_sql}, Got: {actual_update_sql}"
    expected_select_args = (1,)
    expected_update_args = (1,)
    actual_select_args = mock_cursor.execute.call_args_list[0][0][1]
    actual_update_args = mock_cursor.execute.call_args_list[1][0][1]
    
    assert actual_select_args == expected_select_args, f"The SELECT query arguments did not match. Expected {expected_select_args}, got {actual_select_args}."
    assert actual_update_args == expected_update_args, f"The UPDATE query arguments did not match. Expected {expected_update_args}, got {actual_update_args}."

def test_delete_meal_bad_id(mock_cursor):
    """Test error when trying to delete a non-existent meal."""
    mock_cursor.fetchone.return_value = None
    with pytest.raises(ValueError, match="Meal with ID 9999 not found"):
        delete_meal(9999)

def test_delete_meal_already_deleted(mock_cursor):
    """Test error when trying to delete a meal that's already marked as deleted."""
    mock_cursor.fetchone.return_value = ([True],)  # Note the comma to make it a tuple
    with pytest.raises(ValueError, match="Meal with ID 9999 has been deleted"):
        delete_meal(9999)



######################################################
#
#    Get Song
#
######################################################

def test_get_leaderboard(mock_cursor):
    mock_cursor.fetchall.return_value = [
        (1, "Pizza", "Italian", 12.99, "Medium", 10, 8, 0.8),
        (2, "Tacos", "Mexican", 9.99, "Easy", 15, 10, 0.6667)
    ]
    result = get_leaderboard(sort_by="wins")
    expected_leaderboard_wins = [
        {
            'id': 1,
            'meal': "Pizza",
            'cuisine': "Italian",
            'price': 12.99,
            'difficulty': "Medium",
            'battles': 10,
            'wins': 8,
            'win_pct': 80.0
        },
        {
            'id': 2,
            'meal': "Tacos",
            'cuisine': "Mexican",
            'price': 9.99,
            'difficulty': "Easy",
            'battles': 15,
            'wins': 10,
            'win_pct': 66.7
        }
    ]
    assert result == expected_leaderboard_wins, "Leaderboard did not match expected result when sorted by 'wins'."
    expected_query = normalize_whitespace("SELECT id, meal, cuisine, price, difficulty, battles, wins, (wins * 1.0 / battles) AS win_pct FROM meals WHERE deleted = false AND battles > 0")
    actual_query = normalize_whitespace(mock_cursor.execute.call_args[0][0])
   

def test_get_leaderboard_bad_sorting(mock_cursor):
    """Test that an invalid sorting parameter raises a ValueError."""
    with pytest.raises(ValueError, match="Invalid sort_by parameter: invalid_sort"):
        get_leaderboard(sort_by="invalid_sort")

def test_get_meal_by_id(mock_cursor):
    """Test retrieving a meal by its ID."""
    mock_cursor.fetchone.return_value = (1, "Pizza", "Italian", 12.99, "MED", False)
    
    result = get_meal_by_id(meal_id=1)
    
    expected_result = Meal(
        id=1,
        meal="Pizza",
        cuisine="Italian",
        price=12.99,
        difficulty="MED"
    )
    
    assert result == expected_result, f"Expected {expected_result}, but got {result}"
    
    expected_query = normalize_whitespace("SELECT id, meal, cuisine, price, difficulty, deleted FROM meals WHERE id = ?")
    actual_query = normalize_whitespace(mock_cursor.execute.call_args[0][0])
    assert actual_query == expected_query, f"Expected query: {expected_query}, but got: {actual_query}"

    actual_arguments = mock_cursor.execute.call_args[0][1]
    assert actual_arguments == (1,), f"Expected arguments: (1,), but got {actual_arguments}"

def test_get_meal_by_id_deleted(mock_cursor):
    mock_cursor.fetchone.return_value = (1, "Pizza", "Italian", 12.99, "MED", True)
    with pytest.raises(ValueError, match="Meal with ID 1 has been deleted"):
        get_meal_by_id(meal_id=1)

def test_get_meal_by_id_bad_id(mock_cursor):
    mock_cursor.fetchone.return_value = None
    with pytest.raises(ValueError, match="Meal with ID 9999 not found"):
        get_meal_by_id(meal_id=9999)

def test_get_meal_by_name(mock_cursor):
    """Test retrieving a meal by its name."""
    mock_cursor.fetchone.return_value = (1, "Pizza", "Italian", 12.99, "MED", False)
    
    result = get_meal_by_name(meal_name="Pizza")
    
    expected_result = Meal(id=1, meal="Pizza", cuisine="Italian", price=12.99, difficulty="MED")
    
    assert result == expected_result, f"Expected {expected_result}, but got {result}"
    
    expected_query = normalize_whitespace("SELECT id, meal, cuisine, price, difficulty, deleted FROM meals WHERE meal = ?")
    actual_query = normalize_whitespace(mock_cursor.execute.call_args[0][0])
    assert actual_query == expected_query, f"Expected query: {expected_query}, but got: {actual_query}"

    actual_arguments = mock_cursor.execute.call_args[0][1]
    assert actual_arguments == ("Pizza",), f"Expected arguments: ('Pizza',), but got {actual_arguments}"


def test_get_meal_by_name_deleted(mock_cursor):
    mock_cursor.fetchone.return_value = (1, "Pizza", "Italian", 12.99, "MED", True)
    with pytest.raises(ValueError, match="Meal with name Pizza has been deleted"):
        get_meal_by_name(meal_name="Pizza")

def test_get_meal_by_name_bad_name(mock_cursor):
    mock_cursor.fetchone.return_value = None
    with pytest.raises(ValueError, match="Meal with name NonexistentMeal not found"):
        get_meal_by_name(meal_name="NonexistentMeal")

def test_update_meal_stats(mock_cursor):
    """Test updating meal statistics."""
    mock_cursor.fetchone.return_value = (False,) 
    update_meal_stats(meal_id=1, result='win')
    
    expected_select_query = normalize_whitespace("SELECT deleted FROM meals WHERE id = ?")
    expected_update_query = normalize_whitespace("UPDATE meals SET battles = battles + 1, wins = wins + 1 WHERE id = ?")
    
    actual_select_query = normalize_whitespace(mock_cursor.execute.call_args_list[0][0][0])
    actual_update_query = normalize_whitespace(mock_cursor.execute.call_args_list[1][0][0])
    
    assert actual_select_query == expected_select_query, f"Expected select query: {expected_select_query}, got: {actual_select_query}"
    assert actual_update_query == expected_update_query, f"Expected update query: {expected_update_query}, got: {actual_update_query}"
    
    mock_cursor.reset_mock()
    mock_cursor.fetchone.return_value = (False,)  
    update_meal_stats(meal_id=1, result='loss')
    
    expected_update_query = normalize_whitespace("UPDATE meals SET battles = battles + 1 WHERE id = ?")
    actual_update_query = normalize_whitespace(mock_cursor.execute.call_args_list[1][0][0])
    
    assert actual_update_query == expected_update_query, f"Expected update query: {expected_update_query}, got: {actual_update_query}"
    
def test_update_meal_stats_deleted(mock_cursor):
    mock_cursor.fetchone.return_value = (True,) 
    with pytest.raises(ValueError, match="Meal with ID 1 has been deleted"):
        update_meal_stats(meal_id=1, result='win')
    
def test_update_meal_stats_bad_id(mock_cursor):
    mock_cursor.fetchone.return_value = None  
    with pytest.raises(ValueError, match="Meal with ID 1 not found"):
        update_meal_stats(meal_id=1, result='win')
    
def test_update_meal_stats_invalid(mock_cursor):
    mock_cursor.fetchone.return_value = (False,)  
    with pytest.raises(ValueError, match="Invalid result: invalid. Expected 'win' or 'loss'."):
        update_meal_stats(meal_id=1, result='invalid')