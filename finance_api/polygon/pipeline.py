import requests
from dotenv import load_dotenv
import os
from typing import List, Dict, Optional
import time
from datetime import datetime
import pandas as pd

load_dotenv()

class PolygonPipeline:
    """Pipeline for fetching stock data from Polygon.io API."""

    def __init__(self, api_key: Optional[str] = None, data_path: str = "data"):
        """Initialize the pipeline with API credentials and configuration."""
        self.base_url = "https://api.polygon.io"
        self.api_key = api_key or os.getenv("POLYGON_API_KEY")
        self.data_path = data_path
        self.limit = 50000
        self.time_start = None

    def get_stock(self, tickers: List[str], start_date: str = "2023-10-16", end_date: str = "2025-10-15"):
        """Fetch daily stock data from Polygon API and save to parquet files."""
        api_call = 0 
        for ticker in tickers:
            # Initialize rate limit timer
            if self.time_start is None:
                self.time_start = time.time()
            try:
                # Request daily aggregates
                res = requests.get(
                    url=f"{self.base_url}/v2/aggs/ticker/{ticker}/range/1/day/{start_date}/{end_date}",
                    params={"apiKey": self.api_key, "limit": self.limit},
                )
                api_call += 1
                json_data = res.json()["results"]
                df = pd.DataFrame(json_data)
                df["ticker"] = ticker
                print(f"Exporting data to {self.data_path}/{ticker}.parquet\n\n")
                df.to_parquet(f"{self.data_path}/{ticker}.parquet", index=False)

                # Rate limiting: pause after 50 seconds of requests
                time_end = time.time()
                if time_end - self.time_start >= 50 or api_call == 5:
                    print("Sleep for 1 min")
                    time.sleep(60)
                    self.time_start = None
                    api_call = 0

            except Exception as e:
                print(f"Error fetching {ticker}: {e}")


if __name__ == "__main__":
    # Top 20 tickers for stock advisory portfolio
    tickers = [
        # Large Cap Tech & Growth
        "AAPL", "MSFT", "GOOGL", "NVDA", "META", "TSLA",
        # Financial Services
        "JPM", "V", "MA",
        # Healthcare
        "UNH", "JNJ", "LLY",
        # Consumer & Retail
        "AMZN", "WMT", "COST",
        # Diversified Blue Chips
        "BRK.B", "XOM", "PG",
        # Market Indices
        "SPY", "QQQ"
    ]

    # Initialize pipeline and fetch stock data
    pipeline = PolygonPipeline()
    pipeline.get_stock(tickers)
