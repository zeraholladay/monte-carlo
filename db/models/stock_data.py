from sqlalchemy import Column, Date, Float, String, Integer

from .base import Base

class StockData(Base):
    """
    SQLAlchemy model for storing stock data.
    """
    __tablename__ = 'stock_data'

    # Fields of the table
    id = Column(Integer, primary_key=True, autoincrement=True)  # Unique ID for each record
    date = Column(Date, nullable=False, index=True)  # Date of the record
    price = Column(Float, nullable=False)  # Stock price
    ticker = Column(String(10), nullable=False)  # Ticker symbol of the stock
    daily_pct_change = Column(Float, nullable=False)  # Daily percentage change in stock price

    def __repr__(self):
        return f"<StockData(id={self.id}, date={self.date}, ticker={self.ticker}, price={self.price}, daily_pct_change={self.daily_pct_change})>"
