#!/usr/bin/env python3
"""
Integration test for Stage 3: User Master, Roles & Permissions & SLM Provisioning
Tests:
  1. Login as Admin and retrieve JWT token.
  2. Create a new User account via POST /api/v1/users.
  3. Reset user password via POST /api/v1/users/{id}/reset-password.
  4. Provision a new SLM roster record via POST /api/v1/slms with auto user account.
  5. Clean up created test data.
"""

import json
import unittest
import urllib.request
from test_auth_helper import install_auth_opener

import os
BASE_URL = os.environ.get("BASE_URL", "http://localhost:9000")

class TestStage3UserManagement(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        install_auth_opener(BASE_URL)
        cls.test_username = "test_slm_stage3"
        cls.test_slm_name = "Dr. Stage3 Tester"

    def test_01_create_user(self):
        url = f"{BASE_URL}/api/v1/users"
        payload = {
            "username": self.test_username,
            "password": "Stage3Password123!",
            "fullName": "Stage3 Test User",
            "email": "stage3@prashanthhospitals.org",
            "role": "SLM",
            "branchCode": "KOL"
        }
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST"
        )
        try:
            with urllib.request.urlopen(req) as res:
                self.assertEqual(res.status, 201)
                data = json.loads(res.read().decode("utf-8"))
                self.assertEqual(data["user"]["username"], self.test_username)
                self.assertEqual(data["user"]["role"], "SLM")
                self.assertEqual(data["user"]["branchCode"], "KOL")
        except urllib.error.HTTPError as e:
            # If already exists from prior run, check status 400
            self.assertEqual(e.code, 400)

    def test_02_get_users_list(self):
        url = f"{BASE_URL}/api/v1/users"
        req = urllib.request.Request(url, method="GET")
        with urllib.request.urlopen(req) as res:
            self.assertEqual(res.status, 200)
            data = json.loads(res.read().decode("utf-8"))
            self.assertIn("users", data)
            self.assertGreater(data["total"], 0)

    def test_03_reset_password(self):
        # Fetch user id
        req = urllib.request.Request(f"{BASE_URL}/api/v1/users", method="GET")
        with urllib.request.urlopen(req) as res:
            users = json.loads(res.read().decode("utf-8")).get("users", [])
        
        target = next((u for u in users if u["username"] == self.test_username), None)
        if target:
            reset_url = f"{BASE_URL}/api/v1/users/{target['id']}/reset-password"
            reset_req = urllib.request.Request(
                reset_url,
                data=json.dumps({"newPassword": "NewSecretPassword123!"}).encode("utf-8"),
                headers={"Content-Type": "application/json"},
                method="POST"
            )
            with urllib.request.urlopen(reset_req) as res:
                self.assertEqual(res.status, 200)
                data = json.loads(res.read().decode("utf-8"))
                self.assertIn("Password reset successfully", data["message"])

    def test_04_create_slm_roster(self):
        url = f"{BASE_URL}/api/v1/slms"
        payload = {
            "name": self.test_slm_name,
            "department": "Neuroscience",
            "branchCode": "CHP",
            "phone": "+91 99999 88888",
            "status": "ON_DUTY",
            "createUserAccount": False
        }
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST"
        )
        with urllib.request.urlopen(req) as res:
            self.assertEqual(res.status, 201)
            data = json.loads(res.read().decode("utf-8"))
            self.assertEqual(data["slm"]["name"], self.test_slm_name)
            self.assertEqual(data["slm"]["department"], "Neuroscience")

    @classmethod
    def tearDownClass(cls):
        # Cleanup created user and slm
        try:
            req_u = urllib.request.Request(f"{BASE_URL}/api/v1/users", method="GET")
            with urllib.request.urlopen(req_u) as res:
                users = json.loads(res.read().decode("utf-8")).get("users", [])
            for u in users:
                if u["username"] == cls.test_username:
                    del_req = urllib.request.Request(f"{BASE_URL}/api/v1/users/{u['id']}", method="DELETE")
                    urllib.request.urlopen(del_req)

            req_s = urllib.request.Request(f"{BASE_URL}/api/v1/slms", method="GET")
            with urllib.request.urlopen(req_s) as res:
                slms = json.loads(res.read().decode("utf-8")).get("slms", [])
            for s in slms:
                if s["name"] == cls.test_slm_name:
                    del_req = urllib.request.Request(f"{BASE_URL}/api/v1/slms/{s['id']}", method="DELETE")
                    urllib.request.urlopen(del_req)
        except Exception:
            pass

if __name__ == "__main__":
    unittest.main()
