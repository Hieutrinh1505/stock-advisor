import requests
from dotenv import load_dotenv
import os

load_dotenv()

BASE_URL = "https://api.polygon.io"

res = requests.get(
    url=f"{BASE_URL}/v3/reference/tickers",
    params={"apiKey": os.getenv("POLYGON_API_KEY")},
)

print(res.json())
