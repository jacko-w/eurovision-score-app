# streamlit deps
import streamlit as st
from streamlit_server_state import server_state

# modules
from screens import landing, scores
from db.database import db_connect

def check_user_token() -> bool:
    """Checks for the existence of a user token.

    Returns:
        bool: True if the user token exists, False otherwise.
    """
    return server_state.get("user_token", None) is not None


def main() -> None:
    """Main function for the app."""

    st.write(st.secrets["INSTANCE_CONNECTION_NAME"])

    # connect to database
    engine = db_connect()

    # check for user token and set page selection
    if check_user_token():
        scores.show(engine=engine, user_id=server_state.user_id)

    else:
        # no token, show landing page
        landing.show(engine)


if __name__ == "__main__":
    main()
