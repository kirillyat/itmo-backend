from typing import List, Dict
from urllib.parse import parse_qs
import math
import json


async def app(scope, receive, send):
    assert scope["type"] == "http"

    path = scope["path"]
    method = scope["method"]
    query_string = scope["query_string"].decode("utf-8")
    queries = parse_qs(query_string)

    if path == "/factorial" and method == "GET":
        response_data, status_code = await factorial(queries)
    elif path == "/fibonacci" and method == "GET":
        response_data, status_code = await fibonacci(queries)
    elif path == "/mean" and method == "GET":
        response_data, status_code = await mean(queries)
    else:
        response_data, status_code = json.dumps({"error": "Not Found"}), 404

    await send_response(send, response_data, status=status_code)


async def factorial(queries: Dict[str, List[str]]):
    try:
        n = int(queries.get("n", [None])[0])
        if n is None or n < 0:
            raise ValueError("n must be a non-negative integer")
        result = math.factorial(n)
        return json.dumps({"result": result}), 200
    except (ValueError, TypeError):
        return json.dumps({"error": "Invalid input"}), 400


async def fibonacci(queries: Dict[str, List[str]]):
    try:
        n = int(queries.get("n", [None])[0])
        if n is None or n < 0:
            raise ValueError("n must be a non-negative integer")

        def _fibonacci(num):
            a, b = 0, 1
            for _ in range(num):
                a, b = b, a + b
            return a

        result = _fibonacci(n)
        return json.dumps({"result": result}), 200
    except (ValueError, TypeError):
        return json.dumps({"error": "Invalid input"}), 400


async def mean(queries: Dict[str, List[str]]):
    try:
        data = queries.get("data", [])
        if not data:
            raise ValueError("data must be a non-empty list")

        numbers = list(map(float, data))

        if not numbers:
            return json.dumps({"result": 0}), 200
            
        mean_value = sum(numbers) / len(numbers)
        return json.dumps({"result": mean_value}), 200
    except (ValueError, TypeError):
        return json.dumps({"error": "Invalid input"}), 400


async def send_response(send, data, status=200):
    headers = {
        "type": "http.response.start",
        "status": status,
        "headers": [(b"content-type", b"application/json; charset=utf-8")],
    }
    body = {"type": "http.response.body", "body": data.encode()}
    await send(headers)
    await send(body)