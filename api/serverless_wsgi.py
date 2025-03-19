#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
This module converts an AWS API Gateway proxied request to a WSGI request.
Inspired by: https://github.com/logandk/serverless-wsgi
"""
import base64
import os
from urllib.parse import urlencode
from io import BytesIO

# Response object for the serverless function
class Response:
    def __init__(self):
        self.status = 200
        self.headers = []
        self.body = b""

    def start_response(self, status, response_headers, exc_info=None):
        self.status = int(status.split()[0])
        self.headers = response_headers
        return self.write

    def write(self, body):
        if isinstance(body, str):
            body = body.encode("utf-8")
        self.body += body

def handle_request(app, event, context):
    """Handle a request to a Flask application from Vercel."""
    headers = event.get("headers", {})
    path = event.get("path", "")
    http_method = event.get("method", "GET").upper()
    query_string = event.get("query", {})
    body = event.get("body", "")
    is_base64_encoded = event.get("isBase64Encoded", False)

    # Format query string
    if query_string:
        query_string = urlencode(query_string)

    # Decode base64 body if needed
    if is_base64_encoded:
        body = base64.b64decode(body)
    else:
        if isinstance(body, str):
            body = body.encode("utf-8")

    # Create WSGI environment
    environ = {
        "CONTENT_LENGTH": str(len(body) if body else ""),
        "CONTENT_TYPE": headers.get("content-type", ""),
        "PATH_INFO": path,
        "QUERY_STRING": query_string,
        "REMOTE_ADDR": headers.get("x-forwarded-for", "127.0.0.1"),
        "REQUEST_METHOD": http_method,
        "SCRIPT_NAME": "",
        "SERVER_NAME": headers.get("host", "localhost"),
        "SERVER_PORT": headers.get("x-forwarded-port", "80"),
        "SERVER_PROTOCOL": "HTTP/1.1",
        "wsgi.errors": BytesIO(),
        "wsgi.input": BytesIO(body),
        "wsgi.multiprocess": False,
        "wsgi.multithread": False,
        "wsgi.run_once": False,
        "wsgi.url_scheme": headers.get("x-forwarded-proto", "http"),
        "wsgi.version": (1, 0),
    }

    # Add HTTP headers to environment
    for header_name, header_value in headers.items():
        header_name = header_name.upper().replace("-", "_")
        if header_name not in ("CONTENT_TYPE", "CONTENT_LENGTH"):
            environ[f"HTTP_{header_name}"] = header_value

    # Call the WSGI app
    response = Response()
    result = app(environ, response.start_response)

    # Process the application output
    body = response.body
    for data in result:
        if data:
            if isinstance(data, str):
                data = data.encode("utf-8")
            body += data

    # Format the response for Vercel
    headers_dict = {}
    for key, value in response.headers:
        headers_dict[key] = value

    return {
        "statusCode": response.status,
        "headers": headers_dict,
        "body": body.decode("utf-8"),
        "isBase64Encoded": False
    } 