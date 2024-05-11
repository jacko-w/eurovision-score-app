# from sqlalchemy import create_engine, Engine
# from sqlalchemy.ext.declarative import declarative_base
# from sqlalchemy import Column, String
# from sqlalchemy import Column, String, Integer, Float
# import os
# from sqlalchemy.engine import reflection

# # Set up the database connection
# # def db_connect() -> Engine:
# #     # Replace the following URL with your actual database URL
# #     DATABASE_URL = "postgresql://username:password@localhost/dbname"
# #     engine = create_engine(DATABASE_URL)
# #     return engine

# Base = declarative_base()


# class User(Base):
#     __tablename__ = "users"
#     user_id = Column(String, primary_key=True)
#     token = Column(String, unique=True)

# # Define the Score class based on your requirements
# class Score(Base):
#     __tablename__ = 'scores'
#     user_id = Column(String, primary_key=True)
#     country = Column(String, primary_key=True)
#     total_score = Column(Integer)
#     song = Column(Integer)
#     vocal = Column(Integer)
#     staging = Column(Integer)
#     CAMP = Column(Integer)

# def db_connect() -> Engine:
#     base_dir = os.path.dirname(os.path.abspath(__file__))  # Absolute directory of this script
#     database_path = os.path.join(base_dir, "eurovision2024.db")
#     print("Database path:", database_path)
#     DATABASE_URL = f"sqlite:///{database_path}"
#     engine = create_engine(DATABASE_URL, echo=True)
#     return engine

# def list_tables(engine: Engine):
#     inspector = reflection.Inspector.from_engine(engine)
#     tables = inspector.get_table_names()
#     print("Existing tables:", tables)
#     return tables


# def create_tables(engine: Engine):
#     Base.metadata.create_all(engine)


# if __name__ == "__main__":
#     print("Creating database and tables...")
#     engine = db_connect()
#     create_tables(engine)
#     list_tables(engine)
#     print("Database setup complete.")

from sqlalchemy import Engine, create_engine
import streamlit as st
from google.cloud.sql.connector import Connector


INSTANCE_CONNECTION_NAME = st.secrets["INSTANCE_CONNECTION_NAME"]
DB_USER = st.secrets["DB_USER"]
DB_PASS = st.secrets["DB_PASS"]
DB_NAME = st.secrets["DB_NAME"]

# initialise connector
connector = Connector()

def get_conn():
    conn = connector.connect(
        INSTANCE_CONNECTION_NAME,
        "pymysql",
        user="DB_USER",
        password="DB_PASS",
        db="DB_NAME",
    )
    return conn

def db_connect() -> Engine:
    engine = create_engine("mysql+pymysql://", creator=get_conn,)
    return engine