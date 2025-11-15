# Quick Setup Guide

## Quick Start

1. **Activate your virtual environment** (if not already activated):
   ```bash
   # Windows
   bims-venv\Scripts\activate
   
   # macOS/Linux
   source bims-venv/bin/activate
   ```

2. **Install dependencies**:
   
   **For Python 3.14 users (REQUIRED)**:
   ```bash
   python setup_sqlalchemy.py
   ```
   This will install the development version of SQLAlchemy required for Python 3.14.
   
   **For Python 3.11/3.12 users**:
   ```bash
   pip install -r requirements.txt
   ```
   
   **Manual SQLAlchemy fix (if needed)**:
   ```bash
   pip install --upgrade --force-reinstall git+https://github.com/sqlalchemy/sqlalchemy.git
   ```

3. **Create environment file** (optional, defaults are set):
   ```bash
   # Copy the example (if .env.example exists)
   # Or create .env manually with your settings
   ```

4. **Run the server** (database will be created automatically):
   ```bash
   python run.py
   ```
   Or:
   ```bash
   uvicorn app.main:app --reload
   ```

6. **Access the API**:
   - API: http://localhost:8000
   - Interactive Docs: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc

## First Steps

1. **Register a Brand User**:
   ```bash
   POST /api/v1/auth/register
   {
     "email": "brand@example.com",
     "username": "branduser",
     "password": "password123",
     "role": "brand"
   }
   ```

2. **Register an Influencer User**:
   ```bash
   POST /api/v1/auth/register
   {
     "email": "influencer@example.com",
     "username": "influenceruser",
     "password": "password123",
     "role": "influencer"
   }
   ```

3. **Login**:
   ```bash
   POST /api/v1/auth/login
   # Use form data: username=email, password=password
   ```

4. **Create Profiles**:
   - Brand: `POST /api/v1/brands`
   - Influencer: `POST /api/v1/influencers`

## Development Notes

- Database file: `brandfluence.db` (SQLite)
- All models are in `app/models/`
- All schemas are in `app/schemas/`
- API endpoints are in `app/api/v1/endpoints/`
- Configuration is in `app/core/config.py`

## 🗄️ Database Migration to PostgreSQL

When ready to migrate to PostgreSQL:

1. Update `DATABASE_URL` in `.env`:
   ```
   DATABASE_URL=postgresql://user:password@localhost:5432/brandfluence
   ```

2. Install PostgreSQL adapter (if needed):
   ```bash
   pip install psycopg2-binary
   ```

3. The SQLAlchemy setup is already compatible - just change the URL!

