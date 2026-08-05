"""Shared auth bootstrap for the E2E/integration test scripts.

The API used to have no authentication at all. Now every endpoint except
"/" and "/api/v1/auth/login" requires a JWT bearer token, so every test
script needs to log in once and have that token attached to every request
it makes. install_auth_opener() logs in and installs a urllib opener that
adds the Authorization header globally, so existing urllib.request.urlopen()
call sites in each test script don't need to be touched individually.
"""
import json
import os
import urllib.request

DEFAULT_USERNAME = os.environ.get("PH_TEST_USERNAME", "admin")
DEFAULT_PASSWORD = os.environ.get("PH_TEST_PASSWORD", "dVg9Qw_bDPjAvZii")


def install_auth_opener(base_url="http://localhost:8000", username=None, password=None):
    username = username or DEFAULT_USERNAME
    password = password or DEFAULT_PASSWORD

    login_req = urllib.request.Request(
        f"{base_url}/api/v1/auth/login",
        data=json.dumps({"username": username, "password": password}).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(login_req) as res:
        token = json.loads(res.read().decode("utf-8"))["access_token"]

    class _AuthHandler(urllib.request.BaseHandler):
        def http_request(self, req):
            req.add_header("Authorization", f"Bearer {token}")
            return req
        https_request = http_request

    opener = urllib.request.build_opener(_AuthHandler)
    urllib.request.install_opener(opener)
    return token
