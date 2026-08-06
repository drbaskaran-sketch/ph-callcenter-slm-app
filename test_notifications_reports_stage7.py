#!/usr/bin/env python3
"""
Integration test for Stage 7: Notifications & Reports Engine
Tests:
  1. GET /api/v1/notifications/templates - fetch verified WhatsApp/SMS templates.
  2. POST /api/v1/notifications/send - test outbound WhatsApp / SMS dispatch gateway.
  3. GET /api/v1/reports/export/csv - download operational CSV report.
  4. GET /api/v1/reports/export/summary - fetch executive summary snapshot.
"""

import json
import unittest
import urllib.request
from test_auth_helper import install_auth_opener

BASE_URL = "http://localhost:8000"

class TestStage7NotificationsReports(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        install_auth_opener(BASE_URL)
        cls.test_enquiry_id = "ENQ-2026-8801"

    def test_01_get_notification_templates(self):
        url = f"{BASE_URL}/api/v1/notifications/templates"
        req = urllib.request.Request(url, method="GET")
        with urllib.request.urlopen(req) as res:
            self.assertEqual(res.status, 200)
            data = json.loads(res.read().decode("utf-8"))
            self.assertIn("templates", data)
            self.assertGreater(len(data["templates"]), 0)

    def test_02_send_whatsapp_notification(self):
        url = f"{BASE_URL}/api/v1/notifications/send"
        payload = {
            "enquiryId": self.test_enquiry_id,
            "channel": "WHATSAPP",
            "templateType": "APPOINTMENT_CONFIRMATION",
            "recipientPhone": "+91 98401 54321"
        }
        req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), headers={"Content-Type": "application/json"}, method="POST")
        with urllib.request.urlopen(req) as res:
            self.assertEqual(res.status, 200)
            data = json.loads(res.read().decode("utf-8"))
            self.assertIn("dispatchId", data)
            self.assertEqual(data["channel"], "WHATSAPP")
            self.assertIn("Prashanth Hospitals", data["renderedBody"])

    def test_03_export_csv_report(self):
        url = f"{BASE_URL}/api/v1/reports/export/csv"
        req = urllib.request.Request(url, method="GET")
        with urllib.request.urlopen(req) as res:
            self.assertEqual(res.status, 200)
            headers = dict(res.info())
            content_type = headers.get("Content-Type") or headers.get("content-type")
            self.assertIn("text/csv", content_type)
            csv_content = res.read().decode("utf-8")
            self.assertIn("Enquiry ID", csv_content)
            self.assertIn("Patient Name", csv_content)

    def test_04_export_summary_report(self):
        url = f"{BASE_URL}/api/v1/reports/export/summary"
        req = urllib.request.Request(url, method="GET")
        with urllib.request.urlopen(req) as res:
            self.assertEqual(res.status, 200)
            data = json.loads(res.read().decode("utf-8"))
            self.assertIn("totalEnquiriesCaptured", data)
            self.assertIn("activeBranches", data)

if __name__ == "__main__":
    unittest.main()
