# Flask Blog Application

A full-stack personal blog platform built with Python and Flask. It provides user registration, login/logout, and an admin interface for creating, editing, and deleting blog posts.\
This project was built as my first full-stack Flask app while learning backend development. It shows basic user accounts, admin features, and data storage.


## Features

Authentication & Security - user login, password hashing, protected routes.

Admin & Blog Management - admin creates, edits, and deletes blog posts.

Database Integrity - SQLAlchemy models with proper relationships and cascades.

### Tech Stack

- Runtime: Python 3.10+ (WSGI) — Flask application server.

- Language: Python.

- Frontend: Jinja2 templates(HTML) + Flask-Bootstrap 5 (CSS), CKEditor (rich-text editor), Flask-Gravatar (avatar rendering).

- Database & Auth: SQLAlchemy ORM, PostgreSQL as the database, Flask-Login for session management; Werkzeug for password hashing.
  
- Migrations: Flask-Migrate (Alembic) for schema migrations.

- Forms & Validation: Flask-WTF (WTForms) + Flask-CKEditor for rich text fields.

- Email / SMTP: smtplib.

- Configuration: python-dotenv.

- CI/CD: GitHub Actions.

- Hosting: Render.

## Quick start with Docker

### Prerequisites
- Docker and Docker Compose must be installed on your machine.

### Installations
#### 1. Clone this repository
 ```
git clone https://github.com/Goncharov-Michael/Blog.git 
cd Blog
 ```

#### 2. Create and configure your environment file:
**Windows:**
```type nul > .env```

**Linux / macOS / Git Bash:**
```touch .env```
```
echo FLASK_KEY=your_flask_password>> .env
echo FLASK_APP=app.main>> .env
echo POSTGRES_USER=username>> .env
echo POSTGRES_PASSWORD=password>> .env
echo POSTGRES_DB=blog>> .env
echo DATABASE_URL=postgresql://username:password@db:5432/blog>> .env
echo EMAIL=your_email>> .env
echo EMAIL_PASSWORD=your_email_app_password>> .env
```

#### 3. Start the services with Docker Compose:
```
cd docker
docker compose up -d
```

## Quick Start locally.

### Prerequisites

- Python 3.10+
- Git
- PostgreSQL

### Installations
#### 1. Clone this repository 
 ```
 git clone https://github.com/Goncharov-Michael/Blog.git 
 cd Blog
 ```

#### 2. Install Dependencies
 ```
 pip install -r requirements.txt
 ```

#### 3. Environment setup 

 Create a .env file in the project root and with your configuration:
 ```
 FLASK_KEY=replace_with_a_secret_key
 DATABASE_URL=postgresql://<username>:<password>@localhost:5432/<database_name>
 EMAIL=your_email@gmail.com
 EMAIL_PASSWORD=your_app_password 
 ```
 
 > **Notes:** The application uses PostgreSQL. DATABASE_URL must point to a PostgreSQL database. 

#### 4. Create the database
 - bash:
 ```
 psql -U postgres -c "CREATE DATABASE <database_name>;"
 ```

#### 5. Create database schema (migrations)

 - Make sure PostgreSQL is running and you created an empty DB.
 
 - From the project root, with your venv active and dependencies installed, run: 
 > Replace "main.py" with the name of your main file if different.

 - bash:
 ```
 python -m flask --app app.main.py db upgrade
 ```

#### 6. Run the App: 
 ```
python -m flask --app app.main run 
 ```

#### Troubleshooting
- **`ModuleNotFoundError` or `ImportError`**: ensure you run commands from the project root and your venv is activated.  
- **`FLASK_APP` points incorrectly**: replace `main.py` with the module name that exposes your `app` (e.g., `app.my`, etc.).  
- **Permission/connection errors to Postgres**: check `DATABASE_URL`, Postgres service running, and user/password/port.

---


## Demo account

### Live demo
Open the deployed site and try the flows directly. 
**Live demo:** https://blog-c4ko.onrender.com ←
- **Admin:** `admin@gmail.com` / `asdf`  
- **User:** `user@gmail.com` / `user123`

> Tip: Sign in as the admin to access **New Post / Edit / Delete** routes.
 
---

**Security notes**
- Demo credentials are for testing only. 
- Never commit real credentials or your `.env` file to the repository.


## Architecture Overview
### Frontend
- Built with Jinja2 templates + Flask-Bootstrap 5
- Uses CKEditor for rich-text blog content
- Gravatar integration for user avatars
- Handles forms and validation via Flask-WTF

### Backend
- Built with Python 3.10+ + Flask
- Handles user authentication (Flask-Login + Werkzeug password hashing)
- CRUD for blog posts (admin only for creating, editing, deleting posts)
- Handles comments for posts
- Handles contact form emails via SMTP

### Blog Tables
| Table           | Purpose                                                                  |
| -------------   | ------------------------------------------------------------------------ |
| `User`          | Stores user accounts and authentication info                             |
| `BlogPost`      | Stores blog posts with title, subtitle, content, author, image, and date |
| `Comment`       | Stores comments linked to users and posts                                |


### Key Routes & Functionality

- `/` – Homepage with all blog posts
- `/register` – Register a new user
- `/login` / `/logout` – User authentication
- `/post/<id>` – View a post and submit comments (login required for comments)
- `/new-post`, `/edit-post/<id>`, `/delete-post/<id>` – Admin-only blog management
- `/contact` – Contact form that sends an email


### Environment Variables

| Variable         | Description                                                                                                 |
|------------------|-------------------------------------------------------------------------------------------------------------|
| FLASK_KEY        | Secret key for Flask sessions and CSRF protection (used locally and in Docker)                               |
| FLASK_APP        | Flask application entry point (used locally and in Docker)                                                 |
| DATABASE_URL     | PostgreSQL connection URL (e.g. postgresql://user:password@host:5432/db) (used locally and in Docker)      |
| EMAIL            | Gmail address used to send contact form messages (used locally and in Docker)                               |
| EMAIL_PASSWORD   | App password for Gmail (required for sending emails) (used locally and in Docker)                            |
| POSTGRES_DB      | Name of the PostgreSQL database created in Docker (used only in Docker)                                     |
| POSTGRES_USER    | Username for the PostgreSQL container (used only in Docker)                                                |
| POSTGRES_PASSWORD| Password for the PostgreSQL container (used only in Docker)                                                |

### License
This project is licensed under the MIT License—see the LICENSE file for details.
