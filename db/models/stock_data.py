from datetime import timedelta

from sqlalchemy import Column, Date, Float, Integer, String, UniqueConstraint
from sqlalchemy.orm import Session
from sqlalchemy.sql.expression import func

from .base import Base


class StockData(Base):
    """
    SQLAlchemy model for storing stock data.
    """

    __tablename__ = "stock_data"

    # Fields of the table
    id = Column(
        Integer, primary_key=True, autoincrement=True, index=True
    )  # Unique ID for each record
    date = Column(Date, index=True)  # Date of the record
    price = Column(Float)  # Stock price
    ticker = Column(String(10), index=True)  # Ticker symbol of the stock
    daily_pct_change = Column(Float)  # Daily percentage change in stock price

    # Define unique constraint on ticker and date
    __table_args__ = (
        UniqueConstraint('ticker', 'date', name='uq_ticker_date'),
    )

    def __repr__(self):
        return f"<StockData(id={self.id}, date={self.date}, ticker={self.ticker}, price={self.price}, daily_pct_change={self.daily_pct_change})>"

    @staticmethod
    def get_total_return(session):
        min_date, max_date = StockData.get_date_range(session)

        total = 0
        count = 0

        for ticker in StockData.get_all_unique_tickers(session):
            first_price = StockData.get_price_on_or_after(session, ticker, min_date)
            last_price = StockData.get_price_on_or_after(session, ticker, max_date)

            date = max_date

            date -= timedelta(days=1)
            last_price = StockData.get_price_on_or_after(session, ticker, date)

            total += last_price - first_price
            count += 1

        return total / count

    @staticmethod
    def get_all_unique_tickers(session):
        """
        Retrieve all unique tickers from the StockData table.

        Args:
            session (Session): The SQLAlchemy session to use for the query.

        Returns:
            list[str]: A list of unique ticker symbols.
        """
        unique_tickers = session.query(StockData.ticker).distinct().all()
        return [ticker[0] for ticker in unique_tickers]

    @staticmethod
    def select_random_tickers(session: Session, n: int = 1):
        """
        Selects n non-repeating random tickers from the StockData table.

        Args:
            session (Session): The SQLAlchemy session to use for the query.
            n (int): The number of random tickers to select.

        Returns:
            list[str]: A list of n random ticker symbols, or fewer if not enough exist.
        """
        random_tickers = (
            session.query(StockData.ticker)
            .group_by(StockData.ticker)
            .order_by(func.random())
            .limit(n)
            .all()
        )
        return [ticker[0] for ticker in random_tickers]

    @staticmethod
    def get_ordered_dates_and_prices(session: Session, ticker: str):
        """
        Returns an ordered list of dates and prices for a given ticker.

        Args:
            session (Session): The SQLAlchemy session to use for the query.
            ticker (str): The ticker symbol to filter by.

        Returns:
            list[tuple]: A list of tuples, each containing a date and a price, ordered by date.
        """
        results = (
            session.query(StockData.date, StockData.price)
            .filter(StockData.ticker == ticker)
            .order_by(StockData.date)
            .all()
        )
        return results

    @staticmethod
    def get_price_on_or_after(session: Session, ticker: str, target_date: Date):
        """
        Returns the price of a given ticker on the target date or the next available date.

        Args:
            session (Session): The SQLAlchemy session to use for the query.
            ticker (str): The ticker symbol to filter by.
            target_date (Date): The target date to look for.

        Returns:
            float: The price of the ticker on or after the target date, or None if no data is available.
        """
        result = (
            session.query(StockData.price)
            .filter(StockData.ticker == ticker, StockData.date >= target_date)
            .order_by(StockData.date)
            .first()
        )
        return result[0] if result else None

    @staticmethod
    def get_date_range(session: Session):
        """
        Returns the lowest and highest date in the StockData table.

        Args:
            session (Session): The SQLAlchemy session to use for the query.

        Returns:
            tuple[Date, Date]: A tuple containing the lowest and highest date
        """
        result = session.query(
            func.min(StockData.date), func.max(StockData.date)
        ).first()
        return result
