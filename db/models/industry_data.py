from sqlalchemy import Column, String, Float, Text, Integer
from sqlalchemy.ext.declarative import declarative_base

from .base import ModelBase

class Industry(ModelBase):
    __tablename__ = "industry_data"

    id = Column(
        Integer, primary_key=True, autoincrement=True, index=True
    )  # Unique ID for each record
    symbol = Column(String(10), nullable=False) # Stock ticker symbol
    name = Column(String(255), nullable=False)                    # Company name
    last_sale = Column(String(10), nullable=True)                 # Last sale price
    market_cap = Column(String(10), nullable=True)                # Market capitalization
    ipo_year = Column(String(10), nullable=True)                  # IPO year
    sector = Column(String(100), nullable=True)                   # Sector
    industry = Column(String(150), nullable=True)                 # Industry
    summary_quote = Column(Text, nullable=True)                   # Summary quote or URL

    def __repr__(self):
        return (
            f"<Industries(symbol={self.symbol}, name={self.name}, last_sale={self.last_sale}, "
            f"market_cap={self.market_cap}, ipo_year={self.ipo_year}, sector={self.sector}, "
            f"industry={self.industry}, summary_quote={self.summary_quote})>"
        )
