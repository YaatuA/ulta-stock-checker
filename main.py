import os
import asyncio
import requests
from bs4 import BeautifulSoup
from fastapi import FastAPI
from dotenv import load_dotenv
from contextlib import asynccontextmanager
import uvicorn

# Load environment variables
load_dotenv()

# Config
URL = os.getenv("PRODUCT_URL")
PUSHOVER_USER_KEY = os.getenv("PUSHOVER_USER_KEY")
PUSHOVER_API_TOKEN = os.getenv("PUSHOVER_API_TOKEN")
CHECK_INTERVAL_SECONDS = 15 * 60  # 15 minutes

def check_stock() -> bool:
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/122.0.0.0 Safari/537.36"
        )
    }
    try:
        print("Fetching product page...")
        response = requests.get(URL, headers=headers, timeout=10)
        print(f"Response status code: {response.status_code}")
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Error fetching the page: {e}")
        return False

    try:
        soup = BeautifulSoup(response.text, "html.parser")
        button = soup.find("button", class_="AddToBagButton__AddToBag")

        if button:
            print("Found AddToBag button.")
            classes = button.get("class", [])
            print(f"Button classes: {classes}")
            disabled_attr = button.has_attr("disabled")
            print(f"Disabled attribute present: {disabled_attr}")

            if "pal-c-Button--disabled" not in classes and not disabled_attr:
                print("Button is enabled! Product is in stock.")
                return True
            else:
                print("Button is disabled. Product still out of stock.")
        else:
            print("AddToBag button not found. Structure might have changed.")
    except Exception as e:
        print(f"Error parsing the page: {e}")

    return False

def send_pushover_notification():
    message = f"🚨 Ulta product is now in stock!\n\n{URL}"
    data = {
        "token": PUSHOVER_API_TOKEN,
        "user": PUSHOVER_USER_KEY,
        "message": message,
        "title": "Ulta Restock Alert",
        "priority": 1,
    }
    try:
        response = requests.post("https://api.pushover.net/1/messages.json", data=data, timeout=10)
        if response.status_code == 200:
            print("Pushover notification sent successfully.")
        else:
            print(f"Error sending notification: {response.text}")
    except requests.RequestException as e:
        print(f"Error sending Pushover notification: {e}")

async def background_checker():
    while True:
        print("Checking stock...")
        if check_stock():
            send_pushover_notification()
        else:
            print("Not in stock yet.")
        await asyncio.sleep(CHECK_INTERVAL_SECONDS)

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Starting background stock checker...")
    asyncio.create_task(background_checker())
    yield
    print("Shutting down...")

# Create FastAPI app with lifespan
app = FastAPI(lifespan=lifespan)

@app.get("/")
async def root():
    return {"message": "Ulta stock checker is running."}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=10000, reload=False)