# URL Shortener API

A clean, minimal, production-quality REST API for shortening URLs, built with FastAPI, PostgreSQL, and Docker.

---

## 1. Project Overview

This service provides basic URL shortening capabilities. It allows clients to submit a long URL, receive a unique 6-character short code and short URL, and follow that short URL (using HTTP redirects) to navigate directly to the original destination.

---

## 2. Features

* **URL Shortening**: Generates a random, unique, 6-character alphanumeric short code for any valid HTTP/HTTPS URL.
* **Redirection**: Seamlessly redirects requests using the short code (via `HTTP 307 Temporary Redirect`) to the original destination.
* **Validation**: Restricts input utilizing Pydantic constraints to reject malformed or non-HTTP/HTTPS URLs.
* **Uniqueness / Collision Safety**: Proactively checks the database to prevent duplicate short codes, generating replacements in the event of collisions.
* **Containerized Development**: Configured to run entirely in Docker using Docker Compose.
* **Auto-generated Documentation**: Real-time Swagger and ReDoc UI generated dynamically by FastAPI.
* **Health Check**: Simple status endpoint (`GET /health`) for container and deployment health verification.

---

## 3. Tech Stack

* **Python**: 3.12+
* **FastAPI**: Modern, fast web framework
* **Uvicorn**: High-performance HTTP server
* **PostgreSQL**: Production-grade relational database
* **SQLAlchemy**: 2.x object-relational mapper (ORM)
* **Pydantic**: Data validation and setting management
* **Docker & Docker Compose**: Service orchestration

---

## 4. Architecture

```
                 +--------------------------------+
                 |          Client / Browser      |
                 +--------------------------------+
                               |    ^
               HTTP / Shorten  |    |  HTTP Redirect (307)
                               v    |
                 +--------------------------------+
                 |        FastAPI (App Port 8000) |
                 +--------------------------------+
                               |
                   SQLAlchemy  | (Port 5432)
                               v
                 +--------------------------------+
                 |      PostgreSQL (Database)     |
                 +--------------------------------+
```

---

## 5. Project Structure

```text
url-shortener/
├── app/
│   ├── __init__.py      # App package initializer
│   ├── main.py          # FastAPI application routes and startup setup
│   ├── database.py      # SQLAlchemy connection, Engine, and DeclarativeBase
│   ├── models.py        # SQLAlchemy relational URL schema definition
│   ├── schemas.py       # Pydantic validation and serializing schemas
│   └── crud.py          # Database operations and short code generators
├── .dockerignore        # Bypasses local logs/caches in Docker builds
├── .env.example         # Example configuration for environment setup
├── .gitignore           # Ignores .env and host virtual environments
├── Dockerfile           # Package template for the FastAPI container
├── docker-compose.yml   # Multi-service setup for postgres & app
└── requirements.txt     # Python run dependencies
```

---

## 6. Environment Configuration

The application reads its database connection parameters from the `DATABASE_URL` environment variable.

An example file is provided at `.env.example`. Duplicate this file and name the copy `.env` in the root workspace directory before starting:
```bash
cp .env.example .env
```
Inside the container, PostgreSQL is referenced using the Docker service name `postgres`:
```env
DATABASE_URL=postgresql://postgres:postgres@postgres:5432/url_shortener
```

---

## 7. How to Run

No local Python installation is required. Simply spin up the services using Docker Compose:

```bash
docker compose up --build
```
This builds the FastAPI container, downloads the PostgreSQL image, configures safety networks, executes the startup healthcheck, and starts both servers.
* FastAPI app is exposed at: `http://localhost:8000`
* PostgreSQL database is exposed at: `http://localhost:5432`

To run in the background (detached mode), use:
```bash
docker compose up -d --build
```

---

## 8. API Documentation

Interactive documentation is served directly from the FastAPI application container:
* **Swagger UI**: [http://localhost:8000/docs](http://localhost:8000/docs)
* **ReDoc**: [http://localhost:8000/redoc](http://localhost:8000/redoc)

---

## 9. API Endpoints

### GET /health
Checks service status.
* **Response Status**: `200 OK`
* **Response Body**:
  ```json
  {
    "status": "ok"
  }
  ```

### POST /shorten
Shortens a provided web link.
* **Payload Constraints**: Must be a valid HTTP or HTTPS string.
* **Request Header**: `Content-Type: application/json`
* **Request Body**:
  ```json
  {
    "url": "https://www.example.com/some/very/long/url"
  }
  ```
* **Response Status**: `200 OK`
* **Response Body**:
  ```json
  {
    "short_code": "aB3xYz",
    "short_url": "http://localhost:8000/aB3xYz",
    "original_url": "https://www.example.com/some/very/long/url"
  }
  ```

### GET /{short_code}
Retrieves original URL and performs redirect.
* **Response Status**: `307 Temporary Redirect` (redirects browser automatically)
* **Error Response** (when `short_code` does not exist):
  * **Status**: `404 Not Found`
  * **Body**:
    ```json
    {
      "detail": "Short URL not found"
    }
    ```

---

## 10. Error Handling

* **Invalid URL Format**: Submitting an invalid URL structure returns a `422 Unprocessable Entity` response with Pydantic validation details.
* **Bad Path Token**: Accessing an unregistered short code returns a `404 Not Found` response.

---

## 11. Manual Testing Instructions

You can invoke the application endpoints using standard tools such as `curl`, Postman, or the Swagger UI.

### Test 1: Healthcheck Route
```bash
curl -i http://localhost:8000/health
```
*(Verify that status code is 200 and the body is `{"status": "ok"}`)*

### Test 2: Create a Short Code
```bash
curl -i -X POST http://localhost:8000/shorten \
  -H "Content-Type: application/json" \
  -d '{"url":"https://www.google.com/search?q=fastapi"}'
```
*(Verify response is 200, checks the returned JSON format, and note the generated `short_code`)*

### Test 3: Follow the Redirection
Replace `<short_code>` with the token received from the previous step:
```bash
curl -i http://localhost:8000/<short_code>
```
*(Verify output returns an HTTP `307` status and check that the `location` header points to `https://www.google.com/search?q=fastapi`)*

### Test 4: Invalid URL Check
Submitting structured payloads that aren't HTTP/HTTPS scheme should trigger a `422`:
```bash
curl -i -X POST http://localhost:8000/shorten \
  -H "Content-Type: application/json" \
  -d '{"url":"ftp://not-supported"}'
```
*(Verify target returns `422 Unprocessable Entity`)*

### Test 5: Persistence Validation
1. Create a short code and confirm redirection.
2. Restart the app and db containers:
   ```bash
   docker compose restart
   ```
3. Test that redirection to the original URL still completes successfully using the same short code. This confirms SQL state was saved in the volume `postgres_data`.

---

## 12. Stopping the Application

Spin down the environment and remove containers/networks:
```bash
docker compose down
```
By default, this command preserves the database volume `postgres_data`. If you ever need to clear the volume and start with a fresh database, run:
```bash
docker compose down -v
```
