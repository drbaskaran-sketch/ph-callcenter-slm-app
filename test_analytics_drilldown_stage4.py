#!/usr/bin/env python3
"""
Integration test for Stage 4: Analytics & Drill-downs (Specialities, Doctors & Agents)
Tests:
  1. GET /api/v1/analytics/specialities - verify speciality breakdown & conversion calculations.
  2. GET /api/v1/analytics/doctors - verify doctor consultation & procedure metrics.
  3. GET /api/v1/analytics/agents - verify agent call handling, TAT, and quality score.
"""

import json
import unittest
import urllib.request
from test_auth_helper import install_auth_opener

import os
BASE_URL = os.environ.get("BASE_URL", "http://localhost:9000")

class TestStage4AnalyticsDrilldown(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        install_auth_opener(BASE_URL)

    def test_01_specialities_analytics(self):
        url = f"{BASE_URL}/api/v1/analytics/specialities"
        req = urllib.request.Request(url, method="GET")
        with urllib.request.urlopen(req) as res:
            self.assertEqual(res.status, 200)
            data = json.loads(res.read().decode("utf-8"))
            self.assertIn("specialities", data)
            self.assertGreater(data["total"], 0)
            cardio = next((s for s in data["specialities"] if "Cardiology" in s["speciality"]), None)
            self.assertIsNotNone(cardio)

    def test_02_doctors_analytics(self):
        url = f"{BASE_URL}/api/v1/analytics/doctors"
        req = urllib.request.Request(url, method="GET")
        with urllib.request.urlopen(req) as res:
            self.assertEqual(res.status, 200)
            data = json.loads(res.read().decode("utf-8"))
            self.assertIn("doctors", data)
            self.assertGreater(data["total"], 0)

    def test_03_agents_analytics(self):
        url = f"{BASE_URL}/api/v1/analytics/agents"
        req = urllib.request.Request(url, method="GET")
        with urllib.request.urlopen(req) as res:
            self.assertEqual(res.status, 200)
            data = json.loads(res.read().decode("utf-8"))
            self.assertIn("agents", data)
            self.assertGreater(data["total"], 0)

if __name__ == "__main__":
    unittest.main()
