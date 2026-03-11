# Incident Timeline Reconstructor

A full-stack tool to parse raw logs, identify silent periods (gaps), and categorize root causes during incidents.

## Features
- **POST /parse-logs**: Extract timestamps and severity.
- **POST /reconstruct**: Detect timeline gaps (>5 mins) and guess root causes.
- **Frontend**: Paste raw logs, visualize in a color-coded table, and export as an HTML report.
- **Deploy-ready**: Includes Dockerfile and `render.yaml`.

## Local Setup (Python)

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Run the server:
   ```bash
   uvicorn app.main:app --reload
   ```

3. Open `http://localhost:8000` in your browser.

## Local Setup (Docker)

1. Build the image:
   ```bash
   docker build -t incident-timeline .
   ```

2. Run the container:
   ```bash
   docker run -p 8000:8000 incident-timeline
   ```

3. Open `http://localhost:8000` in your browser.

## Tech Stack
- **Backend**: FastAPI (Python 3.11)
- **Frontend**: HTML5, Tailwind CSS (CDN), JavaScript
- **Infrastructure**: Docker, Render
