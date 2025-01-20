import csv
import os
from datetime import timedelta

from sqlalchemy.orm import Session

from alembic import op
from db import StockData


def stock_data_hook(session: Session, stock_data_table) -> None:
    csv_file_path = os.path.join(
        os.path.dirname(__file__), "../bootstrap/snp500prices.csv"
    )

    # Bootstrap table
    # Open and read the CSV file
    with open(csv_file_path, "r") as csvfile:
        reader = csv.DictReader(csvfile)
        # Prepare the data for insertion
        rows = [
            {
                "date": row["Date"],
                "price": float(row["price"]),
                "ticker": row["ticker"],
                "daily_pct_change": float(row["daily_pct_change"]),
            }
            for row in reader
        ]

    # Insert the data into the table
    op.bulk_insert(stock_data_table, rows)

    # Propagate missing prices for all tickers over the whole date range
    session = Session(bind=op.get_bind())
    min_date, max_date = StockData.get_date_range(session)

    for ticker in StockData.get_all_unique_tickers(session):
        ticker_date_and_price_list = StockData.get_ordered_dates_and_prices(
            session, ticker
        )

        first_date, first_price = ticker_date_and_price_list[0]
        new_date = min_date

        while new_date < first_date:
            print(f"Backfilling price for {ticker} on {new_date}")
            session.execute(
                stock_data_table.insert().values(
                    date=new_date, price=first_price, ticker=ticker, daily_pct_change=0
                )
            )
            new_date += timedelta(days=1)

        last_date, last_price = ticker_date_and_price_list[-1]
        new_date = last_date + timedelta(days=1)

        while new_date <= max_date:
            print(f"Adding price for {ticker} on {new_date}")
            session.execute(
                stock_data_table.insert().values(
                    date=new_date, price=last_price, ticker=ticker, daily_pct_change=0
                )
            )
            new_date += timedelta(days=1)

    # Quick sanity check

    for ticker in StockData.get_all_unique_tickers(session):
        ticker_date_and_price_list = StockData.get_ordered_dates_and_prices(
            session, ticker
        )
        first_date, _ = ticker_date_and_price_list[0]
        last_date, _ = ticker_date_and_price_list[-1]

        assert min_date == first_date, f"Ticker {ticker} failed min date"
        assert max_date == last_date, f"Ticker {ticker} failed max date"
