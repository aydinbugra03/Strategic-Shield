# Strategic Shield

## Project Setup Guide

1. **Clone the repository**
   ```bash
   git clone <repo-url>
   cd strategic-shield
   ```
2. **Create Python virtual environment**
   ```bash
   python -m venv env
   source env/bin/activate
   pip install --upgrade pip
   pip install -r backend/requirements.txt
   ```
3. **Install Node dependencies**
   ```bash
   cd frontend
   npm install
   ```
4. **Database configuration**
   - Use PostgreSQL 14 or MySQL 8.
   - Update connection settings in the backend configuration files.

## Repository Structure

- `db/` – database scripts
- `etl/` – data loading routines
- `optim/` – Gurobi optimization scripts
- `backend/` – API and server code
- `frontend/` – React application
- `docs/` – project documentation
- `tests/` – unit tests
