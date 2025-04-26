import os
import asyncio
import requests
from bs4 import BeautifulSoup
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
from contextlib import asynccontextmanager
import uvicorn

# Load environment variables
load_dotenv()

# Configuration
ULTA_URL = os.getenv("PRODUCT_URL_ULTA")
CECRED_ONE_URL = os.getenv("PRODUCT_URL_CECRED_ONE")
CECRED_THREE_URL = os.getenv("PRODUCT_URL_CECRED_THREE")
PUSHOVER_USER_KEY = os.getenv("PUSHOVER_USER_KEY")
PUSHOVER_API_TOKEN = os.getenv("PUSHOVER_API_TOKEN")
CHECK_INTERVAL_SECONDS = 10 * 60  # 10 minutes

def check_stock_ulta() -> bool:
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/122.0.0.0 Safari/537.36"
        )
    }
    try:
        print("Fetching Ulta product page...")
        response = requests.get(ULTA_URL, headers=headers, timeout=10)
        print(f"Response status code: {response.status_code}")
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Error fetching the Ulta product page: {e}")
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
                print("Button is enabled! Product is in stock at Ulta.")
                return True
            else:
                print("Button is disabled. Product still out of stock.")
        else:
            print("AddToBag button not found. Structure might have changed.")
    except Exception as e:
        print(f"Error parsing the page: {e}")

    return False

def check_stock_cecred_one() -> bool:
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/122.0.0.0 Safari/537.36"
        )
    }
    try:
        print("Fetching Cecred 1 product page...")
        response = requests.get(CECRED_ONE_URL, headers=headers, timeout=10)
        print(f"Response status code: {response.status_code}")
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Error fetching the Cecred 1 page: {e}")
        return False

    try:
        soup = BeautifulSoup(response.text, "html.parser")
        button = soup.find("button", class_="product-atc")

        if button:
            print("Found AddToBag button.")
            print("Product is in stock at Cecred.")
            return True
        else:
            print("Product is out of stock at Cecred.")
    except Exception as e:
        print(f"Error parsing the page: {e}")

    return False

def check_stock_cecred_three() -> bool:
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/122.0.0.0 Safari/537.36"
        )
    }
    try:
        print("Fetching Cecred 3 product page...")
        response = requests.get(CECRED_THREE_URL, headers=headers, timeout=10)
        print(f"Response status code: {response.status_code}")
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Error fetching the Cecred 3 page: {e}")
        return False

    try:
        soup = BeautifulSoup(response.text, "html.parser")
        button = soup.find("button", class_="product-atc")

        if button:
            print("Found AddToBag button.")
            print("Product is in stock at Cecred.")
            return True
        else:
            print("Product is out of stock at Cecred.")
    except Exception as e:
        print(f"Error parsing the page: {e}")

    return False

def send_pushover_notification(store: str, product_url: str):
    title = f"🚨 {store} Product is in stock!"
    message = f"Go grab it before it's gone!\n\n{product_url}"
    
    data = {
        "token": PUSHOVER_API_TOKEN,
        "user": PUSHOVER_USER_KEY,
        "title": title,
        "message": message,
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
        if check_stock_ulta():
            send_pushover_notification("Ulta", ULTA_URL)
        elif check_stock_cecred_one():
            send_pushover_notification("Cecred (1)", CECRED_ONE_URL)
        elif check_stock_cecred_three():
            send_pushover_notification("Cecred (3)", CECRED_THREE_URL)
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

@app.api_route("/", methods=["GET", "HEAD"])
async def root():
    return JSONResponse(content={"message": "Stock checker is running."})

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=10000, reload=False)