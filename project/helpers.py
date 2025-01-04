import csv
import datetime
import pytz
import requests
import urllib
import uuid

from flask import redirect, render_template, request, session
from functools import wraps


def apology(message, code=400):
    """Render message as an apology to user."""

    def escape(s):
        """
        Escape special characters.

        https://github.com/jacebrowning/memegen#special-characters
        """
        for old, new in [
            ("-", "--"),
            (" ", "-"),
            ("_", "__"),
            ("?", "~q"),
            ("%", "~p"),
            ("#", "~h"),
            ("/", "~s"),
            ('"', "''"),
        ]:
            s = s.replace(old, new)
        return s

    return render_template("apology.html", top=code, bottom=escape(message)), code


def login_required(f):
    """
    Decorate routes to require login.

    https://flask.palletsprojects.com/en/latest/patterns/viewdecorators/
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)

    return decorated_function

allowed_tags = [
    'nav', 'b', 'i', 'u', 'strong', 'em', 'a', 'p', 'div', 'span',
    'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'img', 'ul', 'li',
    'br', 'hr', 'blockquote', 'code', 'pre',
    'table', 'thead', 'tbody', 'tr', 'th', 'td', 'caption', 'canvas',
    'iframe', 'video', 'audio', 'source', 'script', 'style', 'link'
]

allowed_attrs = {
    '*': ['style', 'class', 'id', 'title', 'onclick', 'Lightbox'],
    'img': ['src', 'alt', 'width', 'height'],
    'table': ['style', 'class'],
    'tr': ['style', 'class'],
    'th': ['style', 'class'],
    'td': ['style', 'class'],
}

# Optional: Add allowed styles (e.g., CSS properties)
allowed_styles = [
    'color', 'font-size', 'background-color', 'text-align',
    'margin', 'padding', 'border', 'width', 'height',
    'display', 'position', 'float', 'clear', 'overflow',
    'font-family', 'line-height', 'font-weight', 'text-decoration',
    'list-style-type', 'vertical-align', 'text-transform',
    'opacity', 'z-index', 'box-shadow', 'border-radius'
]
