# TruthLens AI - Deployment Guide

## Prerequisites
- Docker & Docker Compose
- Python 3.12+ (for local development)
- Node.js 18+ (for local frontend development)

## Running via Docker Compose

```bash
# Clone and enter workspace
git clone https://github.com/truthlens/truthlens-ai.git
cd truthlens-ai

# Start containerized services (PostgreSQL, Backend, Frontend)
docker-compose up --build -d
```

Frontend will be available at: `http://localhost:3000`
Backend OpenAPI documentation at: `http://localhost:8000/api/docs`

## Running Locally for Development

### 1. Backend Setup
```bash
cd backend
python -m venv venv
# On Windows:
venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate

pip install -r requirements.txt

# Start backend server
uvicorn app.main:app --reload --port 8000
```

### 2. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

### 3. Run Benchmark Suite
```bash
$env:PYTHONPATH='backend'; python evaluation/evaluate.py
```
