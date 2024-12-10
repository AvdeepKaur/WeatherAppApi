# WeatherAppApi

This application allows users to sign up and create accounts to view weather in different cities. They can save their favorite cities for quicker access to the forecast.

---

## API ROUTES

### Route: `/api/health`
**Request Type:** GET  
**Purpose:** Verifies that the service is running and returns the health status.  

**Response Format:** JSON  
- **Success Response Example:**  
  - **Code:** 200  
  - **Content:** `{ "status": "healthy" }`  

**Example Request:**
```http
GET /api/health HTTP/1.1
Host: yourservice.com

