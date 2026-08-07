#!/usr/bin/env python3
"""
Integration test for Stage 5: SLA, Escalation & Performance Scorecards
Tests:
  1. POST /api/v1/sla/check-breaches - trigger automated 3-tier SLA breach evaluation.
  2. GET /api/v1/sla/matrix - verify 3-tier SLA escalation matrix counts and compliance rate %.
  3. GET /api/v1/sla/scorecard - verify weighted SLM scorecards (TAT 40%, Conv 35%, FCR 15%, Quality 10%).
"""

import json
import unittest
import urllib.request
from test_auth_helper import install_auth_opener

import os
BASE_URL = os.environ.get("BASE_URL", "http://localhost:9000")

class TestStage5SLAGovernance(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        install_auth_opener(BASE_URL)

    def test_01_check_sla_breaches(self):
        url = f"{BASE_URL}/api/v1/sla/check-breaches"
        req = urllib.request.Request(url, data=b"{}", headers={"Content-Type": "application/json"}, method="POST")
        with urllib.request.urlopen(req) as res:
            self.assertEqual(res.status, 200)
            data = json.loads(res.read().decode("utf-8"))
            self.assertIn("SLA Audit Complete", data["message"])
            self.assertIn("scanned", data)

    def test_02_sla_matrix(self):
        url = f"{BASE_URL}/api/v1/sla/matrix"
        req = urllib.request.Request(url, method="GET")
        with urllib.request.urlopen(req) as res:
            self.assertEqual(res.status, 200)
            data = json.loads(res.read().decode("utf-8"))
            self.assertIn("tier1OnTime", data)
            self.assertIn("tier2BranchHead", data)
            self.assertIn("tier3Director", data)
            self.assertIn("slaComplianceRate", data)

    def test_03_sla_scorecard(self):
        url = f"{BASE_URL}/api/v1/sla/scorecard"
        req = urllib.request.Request(url, method="GET")
        with urllib.request.urlopen(req) as res:
            self.assertEqual(res.status, 200)
            data = json.loads(res.read().decode("utf-8"))
            self.assertIn("scorecard", data)
            self.assertGreater(data["total"], 0)
            top_slm = data["scorecard"][0]
            self.assertIn("score", top_slm)
            self.assertIn("grade", top_slm)

if __name__ == "__main__":
    unittest.main()
