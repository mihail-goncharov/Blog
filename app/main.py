import datetime
import os
from email.message import EmailMessage
from flask import Flask, render_template, redirect, url_for, request, flash, abort
from flask.typing import ResponseReturnValue
from flask_bootstrap import Bootstrap5
from flask_ckeditor import CKEditor
from flask_gravatar import Gravatar
from flask_migrate import Migrate
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, LoginManager, current_user, logout_user, login_required
from app.forms import NewBlogForm, RegisterForm, LoginForm, CommentForm
from app.models import db, BlogPost, User, Comment
from dotenv import load_dotenv
from smtplib import SMTP, SMTPException
from typing import Callable, TypeVar
import logging

F = TypeVar("F", bound=Callable[..., object])
"""INITIALIZATION"""

# Load environment variables
load_dotenv()
EMAIL = os.getenv("EMAIL")
PASSWORD = os.getenv("EMAIL_PASSWORD")
DB_URI = os.getenv("DATABASE_URL")
if not DB_URI:
    raise RuntimeError("DATABASE_URL is not set")

# Initialize Flask app and extensions
app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("FLASK_KEY")
app.config["SQLALCHEMY_DATABASE_URI"] = DB_URI
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)
migrate = Migrate(app, db)
ckeditor = CKEditor(app)
Bootstrap5(app)
login_manager = LoginManager(app)
gravatar = Gravatar(app, size=100, rating='g', default='retro',
                    force_default=False, force_lower=False, use_ssl=False, base_url=None)


@login_manager.user_loader
def load_user(user_id: str) -> User | None:
    return User.query.get(int(user_id))


"""DECORATOR"""


def admin_only(func: F) -> F:
    """
    Restrict access to a view function to administrators only.
    This decorator ensures that the current user is authenticated and has
    administrative privileges. If the user is not an administrator, a
    403 Forbidden error is raised.
    The decorated function preserves its original signature and return type.
    Args:
        func: The view function to protect.

    Returns:
        The same function, wrapped with an admin access check.

    Raises:
        HTTPException: If the current user is not an administrator.
    """

    @wraps(func)
    @login_required
    def wrapper(*args, **kwargs):
        if current_user.id != 1:
            return abort(403)

        return func(*args, **kwargs)

    return wrapper


"""ROUTES"""


@app.route("/register", methods=["GET", "POST"])
def register() -> ResponseReturnValue:
    """
    Handle user registration.

    This view displays the registration form and processes form submission.
    If the form is submitted with valid data, a new user account is created,
    persisted to the database, and the user is logged in automatically.

    If the provided email address is already registered, the user is
    redirected to the login page with an error message.

    Returns:
        A rendered HTML template or an HTTP redirect response.
    """
    register_form = RegisterForm()

    if register_form.validate_on_submit():
        # Extract form data for registration
        email = register_form.email.data
        password = generate_password_hash(register_form.password.data, method="pbkdf2:sha256", salt_length=8)
        name = register_form.name.data
        user = db.session.execute(db.select(User).where(User.email == email)).scalar()

        # Prevent duplicate registration if email is already in use
        if user:
            flash("You've already signed up with that email, log in instead!", "error")
            return redirect(url_for("login"))

        # Create new user, save to database, log in, and redirect
        new_user = User(email=email, password_hash=password, name=name)
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)
        return redirect(url_for("get_all_posts", current_user=current_user))

    return render_template("register.html", form=register_form)


@app.route("/login", methods=["GET", "POST"])
def login() -> ResponseReturnValue:
    """
    Handle user authentication.

    This view renders the login form and processes login submissions.
    When valid credentials are provided, the user is authenticated and
    logged in, then redirected to the main page. If authentication fails,
    an error message is displayed and the user is redirected back to the
    login page.

    Returns:
        A rendered login page or an HTTP redirect response.
    """
    login_form = LoginForm()
    if login_form.validate_on_submit():
        user = db.session.execute(db.select(User).where(User.email == login_form.email.data)).scalar()
        password = login_form.password.data

        if not user:
            flash("That email does not exist, please try again.", "error")
            return redirect(url_for("login"))

        elif not check_password_hash(user.password_hash, password):
            flash("Password incorrect, please try again.", "error")
            return redirect(url_for("login"))

        else:
            login_user(user)
            return redirect(url_for("get_all_posts", current_user=current_user))

    return render_template("login.html", form=login_form, current_user=current_user)


@app.route("/logout")
def logout() -> ResponseReturnValue:
    """Terminate the current session and redirect to the main page."""
    logout_user()
    return redirect(url_for("get_all_posts", current_user=current_user))


@app.route("/")
def get_all_posts() -> ResponseReturnValue:
    """Query all blog posts and render the main page with the result."""
    posts = db.session.execute(db.select(BlogPost)).scalars().all()[::-1]
    return render_template("index.html", all_posts=posts, current_user=current_user)


@app.route("/post/<int:post_id>", methods=["GET", "POST"])
def show_post(post_id: int) -> ResponseReturnValue:
    """Render a blog post page and process new comments if submitted."""
    post = db.get_or_404(BlogPost, post_id)
    comments = post.comments
    comment_form = CommentForm()

    if comment_form.validate_on_submit():
        if not current_user.is_authenticated:
            flash("You must be logged in to comment.", "error")
            return redirect(url_for("login"))

        new_comment = Comment(text=comment_form.text.data, author_id=current_user.id, post_id=post_id)
        db.session.add(new_comment)
        db.session.commit()

        return redirect(url_for("show_post", post_id=post_id))

    return render_template("post.html", post=post, form=comment_form,
                           comments=comments, gravatar=gravatar)


@app.route("/new-post", methods=["GET", "POST"])
@admin_only
def add_new_post() -> ResponseReturnValue:
    """
    Create a new blog post (admin only).

    Renders the new post form and processes submissions. On valid form
    submission, the post is saved to the database and the user is
    redirected to the main page.
    """
    form = NewBlogForm()
    if form.validate_on_submit():
        new_post = BlogPost(
            title=form.title.data,
            author=current_user,
            subtitle=form.subtitle.data,
            body=form.body.data,
            img_url=form.img_url.data,
        )
        db.session.add(new_post)
        db.session.commit()
        return redirect(url_for('get_all_posts'))

    return render_template("make-post.html", form=form, create=True)


@app.route("/edit-post/<int:post_id>", methods=["GET", "POST"])
@admin_only
def edit_post(post_id: int) -> ResponseReturnValue:
    """
    Edit an existing blog post (admin only).

    Renders the post form pre-filled with the current post data and
    processes updates on submission. On successful update, redirects
    to the post page.
    """
    post = db.get_or_404(BlogPost, post_id)
    form = NewBlogForm(
        title=post.title,
        subtitle=post.subtitle,
        img_url=post.img_url,
        body=post.body
    )

    if form.validate_on_submit():
        # Update the Post
        post.title = form.title.data
        post.subtitle = form.subtitle.data
        post.img_url = form.img_url.data
        post.body = form.body.data
        db.session.commit()

        return redirect(url_for("show_post", post_id=post.id))

    return render_template("make-post.html", form=form, create=False)


@app.route('/delete-post/<int:post_id>')
@admin_only
def delete_post(post_id: int) -> ResponseReturnValue:
    """Delete a specified blog post, remove it from the database and redirect to the main page (admin only)."""
    post = db.get_or_404(BlogPost, post_id)
    db.session.delete(post)
    db.session.commit()
    return redirect(url_for('get_all_posts'))


@app.route("/about")
def about() -> ResponseReturnValue:
    """Render the About page."""
    return render_template("about.html")


@app.route("/contact", methods=["GET", "POST"])
def contact() -> ResponseReturnValue:
    """
    Display the contact form and send user messages.

    Handles GET and POST requests:
      - GET: renders the contact form for the user to fill out.
      - POST: retrieves form data (name, email, phone, message),
        sends the message via `send_message`, and renders the page
        with a confirmation that the message was sent.
    """
    msg_sent = False
    email_error = False
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        phone = request.form.get("phone")
        message = request.form.get("message")

        msg_sent = send_message(name, email, phone, message)
        email_error = not msg_sent

    return render_template("contact.html", error=email_error, msg_sent=msg_sent)


def send_message(name: str, user_email: str, phone: str, message: str) -> bool:
    """
    Send a contact message via email.

    Constructs an email using the provided user information and message
    content, then sends it to the configured recipient using Gmail SMTP.

    Args:
        name: Name of the sender.
        user_email: Email address of the sender.
        phone: Phone number of the sender.
        message: Message content.

    Side effects:
        Sends an email to the configured recipient (EMAIL).
    """
    msg = EmailMessage()
    msg["Subject"] = "New Message"
    msg["From"] = user_email
    msg["To"] = EMAIL
    msg.set_content(f"Name: {name}\n"
                    f"Email: {user_email}\n"
                    f"Phone: {phone}\n"
                    f"Message: {message}")

    # Send message
    try:
        with SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(EMAIL, PASSWORD)
            server.send_message(msg)
            return True
    except SMTPException as exc:
        logging.exception(f"Failed to send contact email: {exc}")
        return False

if __name__ == "__main__":
    app.run(debug=False, port=5002)
