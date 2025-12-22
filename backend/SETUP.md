# Backend Setup Guide

## Prerequisites

- Python 3.10 or higher
- PostgreSQL 14 or higher
- pip (Python package manager)

## Installation Steps

### 1. Create Virtual Environment

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Set Up Environment Variables

Copy `.env.example` to `.env` and update with your settings:

```bash
cp .env.example .env
```

Edit `.env` with your database credentials and secret key.

### 4. Set Up Database

Create a PostgreSQL database:

```sql
CREATE DATABASE financial_analyzer;
```

Update `DATABASE_URL` in `.env`:

```
DATABASE_URL=postgresql://username:password@localhost:5432/financial_analyzer
```

### 5. Run Database Migrations

```bash
# Initialize Alembic (if not already done)
alembic init alembic

# Create initial migration
alembic revision --autogenerate -m "Initial migration"

# Apply migrations
alembic upgrade head
```

### 6. Create Upload Directory

```bash
mkdir -p uploads
```

### 7. Run the Application

```bash
# Option 1: Using run.py
python run.py

# Option 2: Using uvicorn directly
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

API documentation (Swagger UI) will be available at `http://localhost:8000/docs`

## Testing

Run tests with pytest:

```bash
pytest
```

## Development

### Code Formatting

```bash
black src/
flake8 src/
mypy src/
```

## API Endpoints

Once running, you can access:

- API Docs: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- Health Check: http://localhost:8000/health

