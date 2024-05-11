# streamlit deps
import streamlit as st
from streamlit_server_state import server_state, server_state_lock
import secrets
import os

from screens import scores

from sqlalchemy.sql import text
from sqlalchemy import Engine

def username_exists(engine, username) -> bool:
    """Check if a username exists in the database.

    Args:
        engine (Engine): SQLAlchemy engine
        username (str): The username to check

    Returns:
        bool: True if the username exists, False otherwise
    """

    with engine.connect() as conn:
        result = conn.execute(
            text("SELECT COUNT(*) FROM users WHERE user_id = :name"), {"name": username}
        ).scalar()
        return result > 0


def insert_user(engine, username, token) -> None:
    """Insert a user into the database.

    Args:
        engine (Engine): SQLAlchemy engine
        username (str): The username to insert
        token (str): The user token to insert
    """

    with engine.connect() as conn:
        conn.execute(
            text("INSERT INTO users (user_id, token) VALUES (:name, :token)"),
            {"name": username, "token": token},
        )
        conn.commit()


def set_user_token(token) -> None:
    with server_state_lock["user_token"]:
        server_state.user_token = token

def set_user_id(user_id) -> None:
    with server_state_lock["user_id"]:
        server_state.user_id = user_id


def _create_name(engine: Engine) -> None | str:
    """Create a name for the user.

    Args:
        engine (Engine): SQLAlchemy engine

    Returns:
        bool: True if the user was created, False otherwise
    """

    # title
    st.title("Eurovision 2024")

    # input field
    name = st.text_input("Name")
    submit = st.button("Submit")

    # user submits
    if submit and name:

        # check if name already exists
        if username_exists(engine, name):
            st.error("Name already exists")
            return None

        else:
            # generate token
            token = secrets.token_urlsafe()

            # add user to db
            insert_user(engine, name, token)
            set_user_token(token)
            set_user_id(name)

            return name

    else:
        return None


def show(engine: Engine) -> None:
    """Show the landing page.

    Args:
        engine (Engine): SQLAlchemy engine
    """
    # current wd
    cwd = os.getcwd()
    path = os.path.join(cwd, 'visuals', 'eurovision-2024-visual.jpg')
    st.image(path, use_column_width=True)

    # check for user token
    if not server_state.get("user_token", None):

        # prompt user to create name
        user_id = _create_name(engine)

        # if registered, show scores page
        if user_id:
            scores.show(engine=engine, user_id=user_id)

    # jump to scores page if already registered
    else:
        scores.show(engine, user_id = server_state.user_id)
