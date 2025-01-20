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

    @property
    def winner_tickers(self):
        return self.df.loc[self.df["Last Cumulative Return"] > self.avg_last_cum_return, "Tickers"].tolist()

    @property
    def loser_tickers(self):
        return self.df.loc[self.df["Last Cumulative Return"] <= self.avg_last_cum_return, "Tickers"].tolist()

    @property
    def date_range(self):
        return StockData.get_date_range(session)

    @property
    def avg_last_cum_return(self):
        return self.df["Last Cumulative Return"].mean()

    @property
    def percentage_greater_than_avg_last_cum_return(self):
        return (self.df["Last Cumulative Return"] > self.avg_last_cum_return).mean()

    def show_graph(self):
        import plotly.graph_objects as go

        sorted_df = self.df.sort_values(by="Last Cumulative Return", ascending=True)

        tickers = sorted_df["Tickers"]
        cumulative_returns = sorted_df["Last Cumulative Return"]

        # Create the figure
        threshold = self.avg_last_cum_return
        def _colorize(value):
            if value > threshold:
                return "green"
            elif value < 0:
                return "red"
            else:
                return "yellow"

        colors = [_colorize(value) for value in cumulative_returns]

        fig = go.Figure()

        # Add a bar trace
        fig.add_trace(
            go.Bar(
                x=tickers,  # Tickers on the x-axis
                y=cumulative_returns,  # Cumulative returns on the y-axis
                name="Cumulative Returns",
                marker_color=colors  # Use the dynamic color list
            )
        )

        # Format the dates into a human-readable format
        raw_date_range = self.date_range

        formatted_date_range = (
            raw_date_range[0].strftime("%B %d, %Y"),
            raw_date_range[1].strftime("%B %d, %Y"),
        )

        # Customize the layout
        fig.update_layout(
            title=f"Cumulative Returns by Ticker from {formatted_date_range[0]} to {formatted_date_range[1]}",
            xaxis_title="Ticker",
            yaxis_title="Cumulative Return",
            yaxis_tickformat=".0%",  # Format y-axis as percentage
            template="plotly"
        )

        # Show the figure
        fig.show()

def main():
    all_tickers = AllTickers()

    print(f"Date range: {all_tickers.date_range}")
    print(f"Avg Last Cumulative Return: {all_tickers.avg_last_cum_return:.2%}")
    print(
        f"Percentage of Tickers Greater Than Last Cumulative Return: {all_tickers.percentage_greater_than_avg_last_cum_return:.2%}"
    )
    all_tickers.show_graph()

    # import pdb; pdb.set_trace()


if __name__ == "__main__":
    main()
