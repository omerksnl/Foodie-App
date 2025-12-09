# Foodie App

A Flask + MySQL prototype for a food ordering platform. Customers can browse restaurants, search menus, manage carts/checkout, and leave ratings. Managers can update menus and view orders/sales.

## Stack
- Python 3.12+, Flask, Jinja2
- MySQL (schema and seed data in `DDL.sql` and `DML.sql`)
- MySQL Connector/Python

## Setup
1) Create and activate a virtual environment (Windows PowerShell):
```
python -m venv .venv
.venv\Scripts\activate
```
2) Install dependencies:
```
pip install -r requirements.txt
```
3) Configure database credentials (create `.env` from `env.example`):
```
DB_HOST=localhost
DB_USER=your_mysql_user
DB_PASSWORD=your_mysql_password
DB_NAME=theapp
```

4) Create and seed the database (adjust credentials as needed):
```
mysql -u root -p < DDL.sql
mysql -u root -p < DML.sql   # optional sample data
```
5) Run the app:
```
set FLASK_APP=app.py
flask run
```
The server defaults to `http://127.0.0.1:5000`.

## Sample logins (from `DML.sql`)
- Manager: `oliviachef` / `SecurePass123!`
- Customer: `emmafoodie` / `TastyMeals321!`

## Project structure
- `app.py` — Flask routes for customers and managers
- `db.py` — MySQL connection helper
- `templates/` — Jinja2 templates for pages
- `static/` — CSS/JS assets
- `DDL.sql` — schema creation + view/trigger
- `DML.sql` — seed data and reset script

## Upload to GitHub (quick guide)
1) Create a new empty repo on GitHub (no README).
2) In this folder, initialize git and commit:
```
git init
git add .
git commit -m "Initial commit"
```
3) Point to GitHub and push:
```
git branch -M main
git remote add origin https://github.com/<your-username>/<repo-name>.git
git push -u origin main
```
If a `venv/` folder exists locally, it is ignored by `.gitignore` and will not be pushed.

## Notes
- Set DB credentials via environment variables (`DB_HOST`, `DB_USER`, `DB_PASSWORD`, `DB_NAME`). Do not commit real secrets.
- Enable MySQL and ensure the `theapp` database exists before running the server.

