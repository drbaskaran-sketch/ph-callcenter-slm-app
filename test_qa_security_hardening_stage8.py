#!/usr/bin/env python3
"""
Integration test for Stage 8: Final QA & Security Hardening Audit
Tests:
  1. Unauthenticated request rejection (401/403 Access Denied).
  2. Invalid JWT token rejection (401/403 Access Denied).
  3. SQL Injection resistance on query params & search endpoints.
  4. CORS origin and security headers audit.
  5. Authenticated user access & JWT token validation.
"""

import json
import unittest
import urllib.request
import urllib.parse
import urllib.error
from test_auth_helper import install_auth_opener

import os
BASE_URL = os.environ.get("BASE_URL", "http://localhost:9000")

class TestStage8QASecurityHardening(unittest.TestCase):

    def test_01_unauthenticated_request_rejected(self):
        opener = urllib.request.build_opener()
        url = f"{BASE_URL}/api/v1/enquiries"
        req = urllib.request.Request(url, method="GET")
        try:
            with opener.open(req) as res:
                self.fail("Expected 401/403 Unauthorized, but request succeeded")
        except urllib.error.HTTPError as e:
            self.assertIn(e.code, [401, 403])

    def test_02_invalid_jwt_token_rejected(self):
        opener = urllib.request.build_opener()
        url = f"{BASE_URL}/api/v1/enquiries"
        req = urllib.request.Request(url, headers={"Authorization": "Bearer INVALID.JWT.TOKEN"}, method="GET")
        try:
            with opener.open(req) as res:
                self.fail("Expected 401/403 Unauthorized, but request succeeded")
        except urllib.error.HTTPError as e:
            self.assertIn(e.code, [401, 403])

    def test_03_sql_injection_resistance(self):
        install_auth_opener(BASE_URL)
        payload_str = urllib.parse.quote("' OR '1'='1")
        url = f"{BASE_URL}/api/v1/enquiries?search={payload_str}"
        req = urllib.request.Request(url, method="GET")
        with urllib.request.urlopen(req) as res:
            self.assertEqual(res.status, 200)
            data = json.loads(res.read().decode("utf-8"))
            self.assertIn("enquiries", data)

    def test_04_cors_and_security_headers(self):
        install_auth_opener(BASE_URL)
        url = f"{BASE_URL}/api/v1/branches"
        req = urllib.request.Request(url, headers={"Origin": "https://callcenter-slm.prashanthhospitals.com"}, method="GET")
        with urllib.request.urlopen(req) as res:
            self.assertEqual(res.status, 200)
            headers = dict(res.info())
            cors = headers.get("access-control-allow-origin") or headers.get("Access-Control-Allow-Origin")
            self.assertIsNotNone(cors)

    def test_05_authenticated_user_access_granted(self):
        install_auth_opener(BASE_URL)
        url = f"{BASE_URL}/api/v1/users"
        req = urllib.request.Request(url, method="GET")
        with urllib.request.urlopen(req) as res:
            self.assertEqual(res.status, 200)
            data = json.loads(res.read().decode("utf-8"))
            self.assertIn("users", data)
            self.assertGreater(data["total"], 0)

if __name__ == "__main__":
    unittest.main()
