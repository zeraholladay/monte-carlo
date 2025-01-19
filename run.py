from datetime import date, datetime, timedelta

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from db import Base, StockData

DATABASE_URL = "postgresql://postgres:localhostonly@localhost:5432/postgres"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
session = SessionLocal()


class Investment:
    def __init__(self, ticker: str):
        """
        Initialize an investment with a ticker symbol and an empty activity log.

        Args:
            ticker (str): The stock ticker symbol.
        """
        self.ticker = ticker
        self.activity = []

    def buy(self, investment_amount: int, date):
        """
        Buy stock units for the given investment amount on a specified date.

        Args:
            investment_amount (int): The amount of money to invest.
            date (Date): The date of the purchase.
        """
        price = StockData.get_price_on_or_after(session, self.ticker, date)

        units = investment_amount / price
        self.activity.append(
            {"date": date, "amount": investment_amount, "units": units}
        )

    def get_total_invested_amount(self):
        """
        Calculate the total amount invested so far.

        Returns:
            int: The total amount invested.
        """
        return sum(entry["amount"] for entry in self.activity)

    def get_value_as_of(self, date):
        """
        Calculate the current value of the investment as of a specified date.

        Args:
            date (Date): The date to calculate the value for.

        Returns:
            float: The total value of the investment as of the specified date.
        """
        total_units = sum(entry["units"] for entry in self.activity)
        price = StockData.get_price_on_or_after(session, self.ticker, date)

        return total_units * price


class Investor:
    def __init__(self, number_of_tickers: int):
        """
        Initialize an investor with a specified number of tickers and create investments for them.

        Args:
            number_of_tickers (int): The number of tickers to invest in.
        """
        self.number_of_tickers = number_of_tickers
        self.investments = [
            Investment(ticker)
            for ticker in StockData.select_random_tickers(session, n=number_of_tickers)
        ]

    def simulate(self, total_amount: int, date_delta):
        """
        Simulate the investment process over a range of dates, distributing investments equally across tickers.

        Args:
            total_amount (int): The total amount of money to invest.
            date_delta (timedelta): The time interval between successive investments.
        """
        min_date, max_date = StockData.get_date_range(session)
        current_date = min_date

        investment_amount_per_ticker = total_amount / self.number_of_tickers

        while current_date < max_date:
            for investment in self.investments:
                investment.buy(investment_amount_per_ticker, current_date)
            current_date += date_delta

    def total_return(self):
        _, max_date = StockData.get_date_range(session)

        total_invested = 0
        total_value = 0

        for investment in self.investments:
            total_invested += investment.get_total_invested_amount()
            total_value += investment.get_value_as_of(max_date)

        return total_value - total_invested


def main():
    time_delta = timedelta(days=14)

    investor = Investor(number_of_tickers=501)
    investor.simulate(100, time_delta)
    print(investor.total_return())
    print(StockData.get_total_return(session))

    # try:
    #     investor = Investor(number_of_tickers=1)
    #     investor.simulate(100, time_delta)
    #     print(investor.total_return())
    #     print(StockData.get_avg_return(session))
    # except Exception as e:
    #     print("An error occurred:", e)
    #     session.rollback()  # Roll back the transaction in case of an error
    # finally:
    #     session.close()  # Always close the session


if __name__ == "__main__":
    main()
