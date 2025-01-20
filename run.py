from datetime import date, datetime, timedelta

import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from db import StockData

DATABASE_URL = "postgresql://postgres:localhostonly@localhost:5432/postgres"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
session = SessionLocal()


class Ticker:
    def __init__(self, ticker: str):
        """
        Initialize an investment with a ticker symbol.

        Args:
            ticker (str): The stock ticker symbol.
        """
        self.ticker = ticker
        self._calc_returns()

    def _get_stock_data(self):
        return StockData.get_ordered_dates_and_prices(session, self.ticker)

    @property
    def avg_return(self):
        return self.df["Return"].mean()

    @property
    def last_cum_return(self):
        return self.df["Cumulative Return"].iloc[-1]

    def _calc_returns(self):
        stock_data = self._get_stock_data()

        data = {
            "Date": [date for date, _ in stock_data],
            "Price": [price for _, price in stock_data],
        }
        self.df = pd.DataFrame(data)
        self.df["Date"] = pd.to_datetime(self.df["Date"])

        # Calculate daily returns (percentage change)
        self.df["Return"] = self.df["Price"].pct_change()

        # Calculate cumulative return
        self.df["Cumulative Return"] = (1 + self.df["Return"]).cumprod() - 1


class AllTickers:
    def __init__(self):
        data = {}
        data["Tickers"] = StockData.get_all_unique_tickers(session)
        data["Last Cumulative Return"] = [
            Ticker(n).last_cum_return for n in data["Tickers"]
        ]
        self.df = pd.DataFrame(data)

    # all_tickers.df.loc[all_tickers.df["Last Cumulative Return"] > all_tickers.avg_last_cum_return, "Tickers"]

    @property
    def date_range(self):
        return StockData.get_date_range(session)

    @property
    def avg_last_cum_return(self):
        return self.df["Last Cumulative Return"].mean()

    @property
    def percentage_greater_than_avg_last_cum_return(self):
        return (self.df["Last Cumulative Return"] > self.avg_last_cum_return).mean()


def main():
    all_tickers = AllTickers()

    print(f"Date range: {all_tickers.date_range}")
    print(f"Avg Last Cumulative Return: {all_tickers.avg_last_cum_return:.2%}")
    print(
        f"Percentage of Tickers Greater Than Last Cumulative Return: {all_tickers.percentage_greater_than_avg_last_cum_return:.2%}"
    )

    # import pdb; pdb.set_trace()


if __name__ == "__main__":
    main()
