import streamlit as st
from sqlalchemy import text
import pandas as pd
import plotly.express as px
from sqlalchemy import Engine
from screens.config import COUNTRIES
import matplotlib.pyplot as plt
import os


def show(engine: Engine, user_id: str):
    cwd = os.getcwd()
    path = os.path.join(cwd, 'visuals', 'eurovision-2024-visual.jpg')
    st.image(path, use_column_width=True)
    user_id = user_id
    st.write(f"Welcome {user_id}!")
    st.title("Leaderboard")
    display_leaderboard(engine)
    interactive_score_entry_and_chart(engine, user_id)


def display_leaderboard(engine: Engine):
    union_query = " UNION ALL ".join(
        f"SELECT '{country}' AS country" for country in COUNTRIES
    )

    query = f"""
    SELECT c.country, COALESCE(SUM(s.total_score), 0) as total_score
    FROM ({union_query}) c
    LEFT JOIN scores s ON c.country = s.country
    GROUP BY c.country
    ORDER BY total_score DESC
    """
    df = pd.read_sql(query, engine)
    st.dataframe(
        data=df, use_container_width=True
    )  # Display the DataFrame using Streamlit


def refresh_and_display_scores(engine, selected_country):
    import pandas as pd
    import plotly.express as px
    import streamlit as st

    # Query to get user names who have scores for the selected country
    users_query = """
    SELECT DISTINCT user_id
    FROM scores
    WHERE country = :country
    """
    users_df = pd.read_sql(users_query, engine, params={"country": selected_country})

    # Create a dropdown for user selection
    user_list = users_df["user_id"].tolist()
    selected_user = st.selectbox("Filter scores by user:", ["All"] + user_list)

    # Fetch total scores
    total_scores_query = """
    SELECT SUM(song) as Song, SUM(vocal) as Vocals, 
    SUM(staging) as Staging, SUM(CAMP) as CAMP
    FROM scores
    WHERE country = :country
    """

    # Query and DataFrame handling based on user selection
    if selected_user != "All":
        # Fetch user-specific scores
        user_scores_query = """
        SELECT SUM(song) as Song, SUM(vocal) as Vocals, 
        SUM(staging) as Staging, SUM(CAMP) as CAMP
        FROM scores
        WHERE country = :country AND user_id = :user_id
        """
        user_scores_df = pd.read_sql(user_scores_query, engine, params={"country": selected_country, "user_id": selected_user}) # type: ignore

        total_scores_df = pd.read_sql(total_scores_query, engine, params={"country": selected_country})

        # Calculate differences
        difference_df = total_scores_df - user_scores_df
        difference_df.columns = ["Song", "Vocals", "Staging", "CAMP"]

        # Data preparation for plotting
        user_scores_df = user_scores_df.T.reset_index()
        user_scores_df.columns = ["index", "user_score"]
        difference_df = difference_df.T.reset_index()
        difference_df.columns = ["index", "difference_score"]

        # Create a bar chart using Plotly Express
        fig = px.bar(
            user_scores_df, x="index", y="user_score", title=f"Score Breakdown for {selected_country}", color_discrete_sequence=["#FF7075"]
        )

        # add bar colour


        # Add the difference as another bar on top
        fig.add_trace(
            px.bar(difference_df, x="index", y="difference_score", color_discrete_sequence=["rgba(255, 112, 117, 0.7)"]).data[0]
        )

    elif selected_user == "All":
        total_df = pd.read_sql(total_scores_query, engine, params={"country": selected_country})
        total_df = total_df.T.reset_index()
        total_df.columns = ["index", "score"]
        fig = px.bar(
            total_df, x="index", y="score", title=f"Score Breakdown for {selected_country}", color_discrete_sequence=['#FF7075']
        )

    # Modify layout to remove gridlines and axis titles, and to adjust bar appearance
    fig.update_layout(
        xaxis=dict(showgrid=False, title_text=''),  # Remove x-axis gridlines and title
        yaxis=dict(showgrid=False, title_text=''),  # Remove y-axis gridlines and title
        bargap=0.2  # Adjust gap between bars to help rounding effect
    )

    # Use Streamlit to display the chart
    config = {"staticPlot": True}
    st.plotly_chart(figure_or_data=fig, use_container_width=True, config=config)




def submit_scores(engine: Engine, user_id, country, category_scores):
    with engine.connect() as conn:
        total_score = sum(category_scores.values())
        result = conn.execute(
            text(
                "SELECT 1 FROM scores WHERE user_id = :user_id AND country = :country"
            ),
            {"user_id": user_id, "country": country},
        ).fetchone()

        try:
            if result:
                update_query = text(
                    """
                    UPDATE scores 
                    SET song = :song, vocal = :vocal, staging = :staging, CAMP = :CAMP, total_score = :total_score
                    WHERE user_id = :user_id AND country = :country
                """
                )
                conn.execute(
                    update_query,
                    {
                        **category_scores,
                        "total_score": total_score,
                        "user_id": user_id,
                        "country": country,
                    },
                )
            else:
                insert_query = text(
                    """
                    INSERT INTO scores (user_id, country, song, vocal, staging, CAMP, total_score)
                    VALUES (:user_id, :country, :song, :vocal, :staging, :CAMP, :total_score)
                """
                )
                conn.execute(
                    insert_query,
                    {
                        **category_scores,
                        "total_score": total_score,
                        "user_id": user_id,
                        "country": country,
                    },
                )
            conn.commit()
        except Exception as e:
            st.error("Failed to update database: " + str(e))


def get_user_scores_for_country(engine: Engine, user_id, country):
    """Retrieve user scores for a selected country from the database."""
    with engine.connect() as conn:
        query = text(
            """
            SELECT song, vocal, staging, CAMP
            FROM scores
            WHERE user_id = :user_id AND country = :country
        """
        )
        result = conn.execute(
            query, {"user_id": user_id, "country": country}
        ).fetchone()

        # If no result, return default values
        if result is None:
            return {"song": 0, "vocal": 0, "staging": 0, "CAMP": 0}

        # Create a dictionary by explicitly accessing each column
        return {
            "song": result[0],
            "vocal": result[1],
            "staging": result[2],
            "CAMP": result[3],
        }


def interactive_score_entry_and_chart(engine: Engine, user_id):
    selected_country = st.selectbox("Select a country:", COUNTRIES)
    if selected_country:

        state = get_user_scores_for_country(engine, user_id, selected_country)

        categories = ["song", "vocal", "staging", "CAMP"]
        category_scores = {
            category: st.slider(
                f"{category}",
                value=state.get(category, 0),
                min_value=0,
                max_value=12,
                key=f"{category}_{selected_country}",
            )
            for category in categories
        }

        if st.button("Submit Score"):
            submit_scores(engine, user_id, selected_country, category_scores)
            # Update the session state after submitting scores
            st.session_state[selected_country] = category_scores.copy()
            st.experimental_rerun()  # Refresh to show updated data

        # Optionally refresh and display the updated scores
        refresh_and_display_scores(engine, selected_country)
