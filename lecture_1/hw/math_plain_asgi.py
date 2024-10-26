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
                status_code = 422
            except Exception:
                response_data = json.dumps({"error": "No valid n value provided"})
                status_code = 422
        else:
            response_data = json.dumps({"error": "No n parameter given"})
            status_code = 422

    elif path.startswith("/fibonacci") and method == "GET":
        try:
            split_path = path.split("/")
            n = int(split_path[-1])

            if n >= 0:
                result = fibonacci(n)
                response_data = json.dumps({"result": result})
                status_code = 200
            else:
                raise ValueError("n must be a non-negative integer")
        except ValueError:
            response_data = json.dumps({"error": "Invalid Fibonacci number"})
            status_code = 422
        except IndexError:
            response_data = json.dumps({"error": "No number provided for Fibonacci"})
            status_code = 404

    # Handling mean query
    elif path == "/mean" and method == "GET":
        body = await read_body(receive)
        try:
            data = json.loads(body)  # We expect the body to contain a JSON list
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


def fibonacci(n):
    if n == 0:
        return 0
    elif n == 1:
        return 1
    else:
        a, b = 0, 1
        for _ in range(2, n + 1):
            a, b = b, a + b
        return b


# Function to read the entire request body, expected for `/mean`
async def read_body(receive):
    body = b""
    more_body = True

    while more_body:
        message = await receive()
        body += message.get("body", b"")
        more_body = message.get("more_body", False)

    return body.decode("utf-8")


async def send_response(send, data, status=200):
    await send(
        {
            "type": "http.response.start",
            "status": status,
            "headers": [(b"content-type", b"application/json")],
        }
    )
    await send(
        {
            "type": "http.response.body",
            "body": data.encode("utf-8"),
        }
    )
