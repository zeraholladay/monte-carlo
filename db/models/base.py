import pandas as pd
from sqlalchemy.orm import Session, declarative_base
from sqlalchemy.sql import text

# Define the declarative base
Base = declarative_base()


# Add shared functionality through a mixin
class BaseMixin:
    @staticmethod
    def get_df_from_sql(session: Session, query: str) -> pd.DataFrame:
        """
        Executes a SQL query using the provided SQLAlchemy session and
        returns the result as a Pandas DataFrame.

        Args:
            session (Session): An active SQLAlchemy session connected to the database.
            query (str): The SQL query to execute.

        Returns:
            pd.DataFrame: A DataFrame containing the query results.

        Example:
            session = Session(bind=engine)
            query = "SELECT * FROM my_table"
            df = BaseMixin.get_df_from_sql(session, query)
        """
        # Execute the query
        result = session.execute(text(query))

        # Extract column names
        columns = result.keys()

        # Fetch all rows
        data = result.fetchall()

        # Create a Pandas DataFrame
        df = pd.DataFrame(data, columns=columns)

        return df


# Combine the declarative base with the mixin
class ModelBase(BaseMixin, Base):
    __abstract__ = True  # Ensure this is not mapped to a table
