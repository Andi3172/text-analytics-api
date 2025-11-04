# Text Analytics API

A high-performance API built with FastAPI that provides advanced Natural Language Processing (NLP) capabilities using Hugging Face Transformers, spaCy, and PyTorch.

This API exposes endpoints for:
* **Sentiment Analysis** (Positive/Negative)
* **Named Entity Recognition (NER)** (Detecting People, Places, Organizations, etc.)
* **Zero-Shot Classification** (Classifying text against custom, user-defined labels)
* **Secure Authentication** (Cookie-based API key access)

The project is fully containerized with **Docker** for consistent and reliable deployment.

## Tech Stack

* **Backend:** Python 3.13
* **API Framework:** FastAPI
* **Server:** Uvicorn
* **NLP Models:**
    * Hugging Face Transformers (for Sentiment & Zero-Shot Classification)
    * spaCy (for Named Entity Recognition)
    * PyTorch (as the backend for Transformers)
* **Containerization:** Docker

---

## How to Run

You can run this project in two ways: locally with a Python virtual environment (ideal for development) or inside a Docker container (recommended for production and testing).

### Method 1: Run with Docker (Recommended)

This is the simplest way to run the application, as all dependencies are handled inside the container.

**Prerequisites:** [Docker Desktop](https://www.docker.com/products/docker-desktop/) must be installed and running.

1.  **Build the Docker image:**
    This command reads the `Dockerfile` and builds your application.
    ```bash
    docker build -t text-analytics-api .
    ```

2.  **Run the container:**
    This command starts your API. Use the `-e` flag to securely set the `API_KEY` environment variable for the server.
    ```bash
    docker run -d -p 8000:8000 -e API_KEY="YOUR_SECRET_KEY_HERE" --name my-api text-analytics-api
    ```
    * `-d` runs the container in detached mode.
    * `-p 8000:8000` maps your local port 8000 to the container's port 8000.
    * `-e API_KEY="..."` sets the master password for the application.

3.  **Test the API:**
    Your API is now live. Open **[http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)** in your browser to access the interactive (Swagger) documentation.

### Method 2: Run Locally (for Development)

1.  **Create and activate a Python virtual environment:**
    ```bash
    # On Windows
    python -m venv venv
    .\venv\Scripts\activate
    ```

2.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Run the Uvicorn server:**
    The `--reload` flag automatically restarts the server when code is changed.
    ```bash
    uvicorn main:app --reload
    ```

4.  **Test the API:**
    Open **[http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)** in your browser.

---

## Authentication

This API uses a cookie-based authentication system. To use the `/analyze` or `/classify` endpoints, you must first get an authentication cookie.

1.  Navigate to the **`/docs`** page.
2.  Find the **`POST /login`** endpoint and expand it.
3.  Click "Try it out" and enter your `API_KEY` (the one set in the `docker run` command or the default "BASIC_API_KEY") in the request body:
    ```json
    {
      "password": "YOUR_SECRET_KEY_HERE"
    }
    ```
4.  Click "Execute". Your browser will receive and store the `access_token` cookie, which will be automatically included in subsequent requests to the other endpoints.

---

## Example API Usage (`curl`)

Once authenticated, you can call the endpoints. The cookie must be included in the request.

### Analyze Endpoint

```bash
curl -X 'POST' \
  '[http://127.0.0.1:8000/analyze](http://127.0.0.1:8000/analyze)' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -H 'Cookie: access_token=YOUR_SECRET_KEY_HERE' \
  -d '{
  "text": "The CEO, Elon Musk, is launching the Cybertruck from Austin next week."
}'
```

### Example Response:
```json
{
  "sentiment": {
    "label": "POSITIVE",
    "score": 0.9997
  },
  "entities": [
    {
      "text": "Elon Musk",
      "label": "PERSON"
    },
    {
      "text": "Cybertruck",
      "label": "PRODUCT"
    },
    {
      "text": "Austin",
      "label": "GPE"
    },
    {
      "text": "next week",
      "label": "DATE"
    }
  ]
}
```
## Classify Endpoint
```bash
curl -X 'POST' \
  '[http://127.0.0.1:8000/classify](http://127.0.0.1:8000/classify)' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -H 'Cookie: access_token=YOUR_SECRET_KEY_HERE' \
  -d '{
  "text": "This new update broke the login button and now I am locked out!",
  "labels": ["bug report", "feature request", "general question", "positive feedback"]
}'
```
### Example Response
```json
{
  "sequence": "This new update broke the login button and now I am locked out!",
  "scores": [
    {
      "label": "bug report",
      "score": 0.9812
    },
    {
      "label": "feature request",
      "score": 0.0101
    },
    {
      "label": "general question",
      "score": 0.0055
    },
    {
      "label": "positive feedback",
      "score": 0.0032
    }
  ]
}
```
