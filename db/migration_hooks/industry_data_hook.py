import csv
import os
from datetime import timedelta

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from alembic import op

from ..models.stock_data import StockData


def industry_data_hook(session: Session, industry_data_table) -> None:
    csv_file_path = os.path.join(
        os.path.dirname(__file__), "../bootstrap/industries.csv"
    )

    # Open and read the CSV file
    with open(csv_file_path, "r") as csvfile:
        reader = csv.DictReader(csvfile)

        # Prepare the data for insertion
        rows = [
            {
                "symbol": row["Symbol"],
                "name": row["Name"],
                # "last_sale": row["LastSale"],
                # "market_cap": row["MarketCap"],
                # "ipo_year": row["IPOyear"],
                "sector": row["Sector"],
                "industry": row["industry"],
                "summary_quote": row["Summary Quote"],
            }
            for row in reader
        ]

        # Insert the data into the table

    # Insert the data into the table
    op.bulk_insert(industry_data_table, rows)
