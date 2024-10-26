import requests
import time

URLS = [
    "http://localhost:8000/item",
    "http://localhost:8000/item",
    "http://localhost:8000/cart",
]


def generate_traffic():
    while True:
        for url in URLS:
            try:
                requests.get(url)
            except requests.RequestException as e:
                print(f"Error: {e}")
        time.sleep(1)


if __name__ == "__main__":
    generate_traffic()
