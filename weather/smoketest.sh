#!/bin/bash

# Define the base URL for the Flask API
BASE_URL="http://localhost:5001/api"

# Flag to control whether to echo JSON output
ECHO_JSON=false

# Parse command-line arguments
while [ "$#" -gt 0 ]; do
  case $1 in
    --echo-json) ECHO_JSON=true ;;
    *) echo "Unknown parameter passed: $1"; exit 1 ;;
  esac
  shift
done


###############################################
#
# Health checks
#
###############################################

# Function to check the health of the service
check_health() {
  echo "Checking health status..."
  curl -s -X GET "$BASE_URL/health" | grep -q '"status": "healthy"'
  if [ $? -eq 0 ]; then
    echo "Service is healthy."
  else
    echo "Health check failed."
    exit 1
  fi
}

# Function to check the database connection
check_db() {
  echo "Checking database connection..."
  curl -s -X GET "$BASE_URL/db-check" | grep -q '"database_status": "healthy"'
  if [ $? -eq 0 ]; then
    echo "Database connection is healthy."
  else
    echo "Database check failed."
    exit 1
  fi
}


##########################################################
#
# User Management
#
##########################################################

add_user() {
  id=$1
  username=$2
  email=$3
  password=$4

  echo "Adding user ($id - $username, $email) to the system..."
  curl -s -X POST "$BASE_URL/create-user" -H "Content-Type: application/json" \
    -d "{\"id\":\"$id\", \"username\":\"$username\", \"email\":\"$email\", \"password\":\"$password\"}" | grep -q '"status": "success"'

  if [ $? -eq 0 ]; then
    echo "User added successfully."
  else
    echo "Failed to add user."
    exit 1
  fi
}

get_all_users() {
  echo "Getting all users in the db..."
  response=$(curl -s -X GET "$BASE_URL/get-all-users")
  if echo "$response" | grep -q '"status": "success"'; then
    echo "All users retrieved successfully."
    if [ "$ECHO_JSON" = true ]; then
      echo "Users JSON:"
      echo "$response" | jq .
    fi
  else
    echo "Failed to get users."
    exit 1
  fi
}

update_password() {
  id=$1
  new_password=$2

  echo "Updating password for user with ID $id..."
  response=$(curl -s -X PUT "$BASE_URL/api/update-password" -H "Content-Type: application/json" \
    -d "{\"id\": $id, \"new_password\": \"$new_password\"}")

  if echo "$response" | grep -q '"status": "success"'; then
    echo "Password updated successfully for user ID $id."
    if [ "$ECHO_JSON" = true ]; then
      echo "Response JSON:"
      echo "$response" | jq .
    fi
  elif echo "$response" | grep -q '"error":'; then
    error_message=$(echo "$response" | jq -r '.error')
    echo "Failed to update password: $error_message"
    exit 1
  else
    echo "Failed to update password due to an unknown error."
    exit 1
  fi
}

update_username() {
  id=$1
  new_username=$2

  echo "Updating username for user with ID $id..."
  response=$(curl -s -X PUT "$BASE_URL/api/update-username" -H "Content-Type: application/json" \
    -d "{\"id\": $id, \"new_username\": \"$new_username\"}")

  if echo "$response" | grep -q '"status": "success"'; then
    echo "Username updated successfully for user ID $id."
    if [ "$ECHO_JSON" = true ]; then
      echo "Response JSON:"
      echo "$response" | jq .
    fi
  elif echo "$response" | grep -q '"error":'; then
    error_message=$(echo "$response" | jq -r '.error')
    echo "Failed to update username: $error_message"
    exit 1
  else
    echo "Failed to update username due to an unknown error."
    exit 1
  fi
}

##########################################################
# Favorites Management
##########################################################

add_favorite_location() {
    user_id=$1
    location_name=$2
    echo "Adding favorite location ($location_name) for user $user_id..."
    curl -s -X POST "$BASE_URL/add-favorite-location" -H "Content-Type: application/json" \
    -d "{\"user_id\":$user_id, \"location\":{\"name\":\"$location_name\"}}" | grep -q '"status": "success"'
    if [ $? -eq 0 ]; then
        echo "Favorite location added successfully."
    else
        echo "Failed to add favorite location."
        exit 1
    fi
}

get_favorite_locations() {
    user_id=$1
    echo "Getting favorite locations for user $user_id..."
    response=$(curl -s -X GET "$BASE_URL/get-favorite-locations/$user_id")
    if echo "$response" | grep -q '"status": "success"'; then
        echo "Favorite locations retrieved successfully."
        if [ "$ECHO_JSON" = true ]; then
            echo "Locations JSON:"
            echo "$response" | jq .
        fi
    else
        echo "Failed to get favorite locations."
        exit 1
    fi
}

update_weather_data() {
    user_id=$1
    echo "Updating weather data for user $user_id..."
    curl -s -X POST "$BASE_URL/update-weather-data/$user_id" | grep -q '"status": "success"'
    if [ $? -eq 0 ]; then
        echo "Weather data updated successfully."
    else
        echo "Failed to update weather data."
        exit 1
    fi
}

# Health checks
check_health
check_db

# Add users
add_user 1 "JohnDoe" "jdoe@example.com" "password123"
add_user 2 "JaneSmith" "jsmith@example.com" "securepass456"

# Get all users
get_all_users

# Add favorite locations
add_favorite_location 1 "New York"
add_favorite_location 1 "London"
add_favorite_location 2 "Tokyo"

# Get favorite locations
get_favorite_locations 1
get_favorite_locations 2

# Update weather data
update_weather_data 1
update_weather_data 2

echo "All tests passed successfully!"