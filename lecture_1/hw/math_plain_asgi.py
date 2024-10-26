from typing import List, Dict
from urllib.parse import parse_qs
import math
import json
from urllib.parse import parse_qs


async def app(scope, receive, send):
    assert scope["type"] == "http"

    path = scope["path"]
    method = scope["method"]

    if path == "/factorial" and method == "GET":
        query_string = scope["query_string"].decode("utf-8")
        queries = dict(
            elem.split("=") for elem in query_string.split("&") if "=" in elem
        )

        if "n" in queries:
            try:
                n = int(queries["n"])
                if n >= 0:
                    response_data = json.dumps({"result": math.factorial(n)})
                    status_code = 200
                else:
                    raise ValueError("n must be a non-negative integer")
            except ValueError:
                response_data = json.dumps({"error": "Invalid n value"})
                status_code = 400
            except Exception:
                response_data = json.dumps({"error": "No valid n value provided"})
                status_code = 422
        else:
            response_data = json.dumps({"error": "No n parameter given"})
            status_code = 422

    # Handling fibonacci query
    elif path.startswith("/fibonacci") and method == "GET":
        try:
            split_path = path.split("/")
            n = int(split_path[-1])  # Extract n from path like /fibonacci/5

            if n >= 0:
                result = fibonacci(n)
                response_data = json.dumps({"result": result})
                status_code = 200
            else:
                raise ValueError("n must be non-negative")
        except (ValueError, IndexError):
            response_data = json.dumps({"error": "Invalid Fibonacci sequence number"})
            status_code = 422

    # Handling mean query
    elif path == "/mean" and method == "GET":
        body = await read_body(receive)
        try:
            data = json.loads(body)  # Expecting body in JSON format
            if not isinstance(data, list) or not all(
                isinstance(item, (int, float)) for item in data
            ):
                response_data = json.dumps(
                    {"error": "The given data must be a list of numbers"}
                )
                status_code = 422
            elif not data:
                response_data = json.dumps({"error": "The given data is empty"})
                status_code = 400
            else:
                mean_value = sum(data) / len(data)
                response_data = json.dumps({"result": mean_value})
                status_code = 200
        except json.JSONDecodeError:
            response_data = json.dumps({"error": "Invalid JSON format"})
            status_code = 422

    else:
        response_data = json.dumps({"error": "Not Found"})
        status_code = 404

    await send_response(send, response_data, status=status_code)


# Fibonacci function
def fibonacci(n):
    if n <= 1:
        return n
    else:
        a, b = 0, 1
        for _ in range(2, n + 1):
            a, b = b, a + b
        return b


async def read_body(receive):
    body = b""
    while True:
        message = await receive()
        body += message.get("body", b"")
        if not message.get("more_body"):
            break
    return body.decode("utf-8")


async def send_response(send, data, status=200):
    await send(
        {
            "type": "http.response.start",
            "status": status,
            "headers": [(b"content-type", b"application/json; charset=utf-8")],
        }
    )
    await send(
        {
            "type": "http.response.body",
            "body": data.encode("utf-8"),
        }
    )
