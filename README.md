# WeatherAppApi

This application allows users to sign up and create accounts to view weather in different cities. They can save their favorite cities for quicker access to the forecast.

-------------------------------

Route: /api/health   
Request Type: GET    
Purpose: Verifies that the service is running and returns the health status.    

Response Format: JSON  
Success Response Example:  
Code: 200  
Content: { "status": "healthy" }    
  
Example Request:   
GET /api/health HTTP/1.1  
Host: yourservice.com  
  
Example Response:  
{  
"status": "healthy"  
}  
  
---  
  
Route: /api/db-check  
Request Type: GET  
Purpose: Checks the health of database connections and verifies the existence of required tables (users and user_favorites).  
  
Request Body: None  

Response Format: JSON  
Success Response Example:  
Code: 200  
Content: { "database_status": "healthy" }  
  
Example Request:  
GET /api/db-check HTTP/1.1  
Host: yourservice.com   
  
Example Success Response:  
{  
"database_status": "healthy"  
}  

---

Route: /api/create-user  
Request Type: POST  
Purpose: Creates a new user and adds the user to the database.  
  
Request Body:  
    id (String): The unique ID of the user.  
    username (String): The username of the user.  
    email (String): The email of the user.  
    password (String): The password for the user.   
  
Response Format: JSON  
Success Response Example:  
Code: 201  
Content: { "status": "success", "user": "<user_id>" }  
  
Example Request:  
POST /api/create-user HTTP/1.1  
Host: yourservice.com  
Content-Type: application/json  
{  
"id": "12345",  
"username": "johndoe",  
"email": "johndoe@example.com",  
"password": "securepassword"  
}  
  
Example Success Response:  
{  
"status": "success",  
"user": "12345"   
}  
  
---

Route: /api/get-all-users  
Request Type: GET  
Purpose: Retrieves all users in the db.  
  
Request Body:  
None  
  
Response Format: JSON  
  
Success Response Example:  
Code: 200  
Content: { "status": "success", "users": [<list_of_users>] }  
  
Example Request:  
GET /api/get-all-users HTTP/1.1  
Host: yourservice.com  
  
Example Success Response:  
{  
"status": "success",  
"users": [
{ "id": "12345", "username": "johndoe", "email": "johndoe@example.com" },
{ "id": "67890", "username": "janedoe", "email": "janedoe@example.com" }
]
}

---

Route: /api/update-password
Request Type: PUT
Purpose: Updates the password of a user in the database.

Request Body:
id (Integer): The ID of the user whose password is to be updated.
new_password (String): The new password to replace the old one.

Response Format:
Success Response Example:
Code: 200
Content: { "status": "success", "message": "Password updated for user ID <id>" }

Example Request:
PUT /api/update-password HTTP/1.1
Host: yourservice.com
Content-Type: application/json
{
"id": 12345,
"new_password": "newSecurePassword"
}

Example Success Response:
{
"status": "success",
"message": "Password updated for user ID 12345"
}

---

Route: /api/update-username
Request Type: PUT
Purpose: Updates the username of a user in the database.

Request Body:
id (Integer): The ID of the user whose username is to be updated.
new_username (String): The new username to replace the old one.

Response Format:
Success Response Example:
Code: 200
Content: { "status": "success", "message": "Username updated for user ID <id>" }

Example Request:
PUT /api/update-username HTTP/1.1
Host: yourservice.com
Content-Type: application/json
{
"id": 12345,
"username": "jondoe2"
}

Example Success Response:
{
"status": "success",
"message": "Username updated for user ID 12345"
}

---

Route: /api/add-favorite-location
Request Type: POST
Purpose: Adds a new favorite location for a user.

Request Body:

user_id (String): The ID of the user adding the favorite location.
location (String): The name or identifier of the location to be added to the user's favorites.
Response Format:
Success Response Example:
Code: 201
Content: { "status": "success", "message": "Location added to favorites." }

Example Request:
POST /api/add-favorite-location HTTP/1.1
Host: yourservice.com
Content-Type: application/json
{
"user_id": "12345",
"location": "New York"
}

Example Success Response:
{
"status": "success",
"message": "Location added to favorites."
}

---


Route: /api/remove-favorite-location
Request Type: DELETE
Purpose: Removes a favorite location for a user.

Request Body:

user_id (String): The ID of the user removing the favorite location.
location (String): The name or identifier of the location to be removed from the user's favorites.
Response Format:
Success Response Example:
Code: 200
Content: { "status": "success", "message": "Location removed from favorites." }

Example Request:
DELETE /api/remove-favorite-location HTTP/1.1
Host: yourservice.com
Content-Type: application/json
{
"user_id": "12345",
"location": "New York"
}

Example Success Response:
{
"status": "success",
"message": "Location removed from favorites."
}

---

Route: /api/get-favorite-locations  
Request Type: GET  
Purpose: Retrieves the list of favorite locations for a specific user.  

Request Parameters:  
- user_id (Integer): The ID of the user whose favorite locations are being retrieved.  

Response Format:  
Success Response Example:  
Code: 200  
Content: { "favorite_locations": [<list_of_locations>] }  

Example Request:  
GET /api/get-favorite-locations?user_id=12345 HTTP/1.1  
Host: yourservice.com  

Example Success Response:  
{  
  "favorite_locations": ["New York", "San Francisco", "Los Angeles"]  
}  

---

Route: /api/get_favorites_length
Request Type: GET
Purpose: Retrieves the total number of favorite locations across all users.

Request Body: None

Response Format:
Success Response Example:
Code: 200
Content: { "favorites_length": <total_count> }

Example Request:
GET /api/get_favorites_length HTTP/1.1
Host: yourservice.com

Example Success Response:
{
"favorites_length": 42
}

---

Route: /api/update_weather_data
Request Type: PUT
Purpose: Updates the weather data for all favorite locations of a specific user.

Request Body:

user_id (String): The ID of the user whose favorite locations' weather data needs to be updated.
Response Format:
Success Response Example:
Code: 200
Content: { "status": "success", "message": "Weather data updated." }

Example Request:
PUT /api/update_weather_data HTTP/1.1
Host: yourservice.com
Content-Type: application/json
{
"user_id": "12345"
}

Example Success Response:
{
"status": "success",
"message": "Weather data updated."
}

---

Route: /api/check-if-empty
Request Type: GET
Purpose: Checks if the favorites list is empty.

Request Body: None

Response Format:
Success Response Example:
Code: 200
Content: { "status": "success", "message": "Favorites are not empty." }

Example Request:
GET /api/check-if-empty HTTP/1.1
Host: yourservice.com

Example Success Response:
{
"status": "success",
"message": "Favorites are not empty."
}
