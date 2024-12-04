import pytest
import requests
from meal_max.utils.random_utils import get_random

RANDOM_NUMBER = "0.42" 

@pytest.fixture
def mock_random_org(mocker):
    """Fixture to mock a requests.get call for valid responses."""
    mock_response = mocker.Mock()
    mock_response.text = RANDOM_NUMBER
    mock_response.status_code = 200

    mocker.patch("requests.get", return_value=mock_response)
    return mock_response

def test_get_random_success(mock_random_org):
    """Test get_random() when a valid number is returned."""
    random_number = get_random()
    
    assert random_number == float(RANDOM_NUMBER)
    requests.get.assert_called_once_with(
        "https://www.random.org/decimal-fractions/?num=1&dec=2&col=1&format=plain&rnd=new",
        timeout=5
    )

def test_get_random_invalid_response(mocker):
    """Test get_random() when there's an invalid response."""
    mock_response = mocker.Mock()
    mock_response.text = "invalid_response"
    mock_response.status_code = 200

    mocker.patch("requests.get", return_value=mock_response)

    with pytest.raises(ValueError, match="Invalid response from random.org"):
        get_random()

def test_get_random_timeout(mocker):
    """Test get_random() request times out."""
    mocker.patch("requests.get", side_effect=requests.exceptions.Timeout)

    with pytest.raises(RuntimeError, match="Request to random.org timed out"):
        get_random()

def test_get_random_request_exception(mocker):
    """Test get_random() when the request fails due to a network error."""
    mocker.patch("requests.get", side_effect=requests.exceptions.RequestException("Network error"))

    with pytest.raises(RuntimeError, match="Request to random.org failed: Network error"):
        get_random()
