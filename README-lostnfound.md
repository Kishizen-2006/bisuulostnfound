# BISU Lost & Found Render Deploy

Upload these files to your GitHub repo:

- `lostnfound.py`
- `requirements.txt`
- `.gitignore`
- `README.md`
- `bisu_logo.png`

Use these exact contents for the support files:

## requirements.txt

```txt
Flask>=3.0,<4.0
gunicorn>=23.0,<24.0
Werkzeug>=3.0,<4.0
Jinja2>=3.1,<4.0
```

## .gitignore

```gitignore
__pycache__/
instance/
uploads/
*.db
*.db-journal
.env
.venv/
venv/
*.pyc
```

## README.md

```md
# BISU Lost & Found Render Deploy

Files in this repo:

- `lostnfound.py`
- `requirements.txt`
- `.gitignore`
- `README.md`
- `bisu_logo.png`

## Render Web Service settings

- Build Command: `pip install -r requirements.txt`
- Start Command: `gunicorn lostnfound:app`

## Environment variables

Set this in Render:

- `SECRET_KEY`

## Notes

This app currently uses SQLite.
Do not upload local database files like `bisu_lostnfound.db`.
The app also serves `bisu_logo.png`, so include that file in the repo root.
If you want to use a Render PostgreSQL database, the code must be updated to use `DATABASE_URL`.
```
