##https://open-meteo.com/en/docs/geocoding-api/#name 
## to find the lat and long given the name of the city

import requests
import json

def get_latitude_longitude(city):
  """
  Fetches latitude and longitude for a given city using Open-Meteo's Geocoding API.

  Args:
      city (str): The city name for which to retrieve coordinates.

  Returns:
      tuple: A tuple containing (latitude, longitude) if successful,
             or None if an error occurs.
  """

  url = f"https://geocoding-api.open-meteo.com/v1/search?name={city}"

  try:
    response = requests.get(url)
    response.raise_for_status()  # Raise an exception for non-200 status codes
  except requests.exceptions.RequestException as e:
    print(f"Error fetching data from Open-Meteo API: {e}")
    return None

  data = response.json()

  if not data.get("results"):
    print(f"City '{city}' not found in Open-Meteo Geocoding API results.")
    return None

  # Extract latitude and longitude from the first result (assuming uniqueness)
  latitude = data["results"][0]["latitude"]
  longitude = data["results"][0]["longitude"]

  return latitude, longitude

def main():
  """
  Prompts the user for a city, fetches coordinates, and constructs the weather data URL.
  """

  city = input("Enter a city: ")

  latitude, longitude = get_latitude_longitude(city)

  if latitude and longitude:
    weather_url = f"https://open-meteo.com/en/docs#latitude={latitude}&longitude={longitude}"
    print("Weather data URL based on retrieved coordinates:")
    print(weather_url)
  else:
    print("Unable to retrieve coordinates for the entered city.")

if __name__ == "__main__":
  main()
