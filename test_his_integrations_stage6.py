#!/usr/bin/env python3
"""
Integration test for Stage 6: HIS Integrations (OPD Slot Booking, Surgery Pre-booking & Patient Registry Search)
Tests:
  1. GET /api/v1/his/slots - get available OPD consultation slots.
  2. POST /api/v1/his/book-appointment - book OPD consultation slot in HIS and link to enquiry.
  3. POST /api/v1/his/prebook-surgery - pre-book OT surgery procedure slot in HIS.
  4. GET /api/v1/his/patient-search - search patient EMR/UHID registry.
"""

import json
import unittest
import urllib.request
from test_auth_helper import install_auth_opener

BASE_URL = "http://localhost:8000"

class TestStage6HISIntegrations(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        install_auth_opener(BASE_URL)
        cls.test_enquiry_id = "ENQ-2026-8801"

    def test_01_get_his_slots(self):
        url = f"{BASE_URL}/api/v1/his/slots?doctorName=Dr.%20S.%20Prashanth"
        req = urllib.request.Request(url, method="GET")
        with urllib.request.urlopen(req) as res:
            self.assertEqual(res.status, 200)
            data = json.loads(res.read().decode("utf-8"))
            self.assertIn("slots", data)
            self.assertGreater(data["total"], 0)

    def test_02_book_opd_appointment(self):
        url = f"{BASE_URL}/api/v1/his/book-appointment"
        payload = {
            "enquiryId": self.test_enquiry_id,
            "doctorName": "Dr. S. Prashanth, Sr. Cardiologist",
            "appointmentDate": "2026-08-10",
            "slotTime": "10:30 AM",
            "remarks": "Stage 6 HIS OPD Slot Booking"
        }
        req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), headers={"Content-Type": "application/json"}, method="POST")
        with urllib.request.urlopen(req) as res:
            self.assertEqual(res.status, 200)
            data = json.loads(res.read().decode("utf-8"))
            self.assertIn("hisBookingId", data)
            self.assertIn("patientUhid", data)
            self.assertEqual(data["enquiry"]["status"], "APPOINTMENT_CONFIRMED")
            self.assertEqual(data["enquiry"]["hisSyncStatus"], "SYNCED")

    def test_03_prebook_surgery(self):
        url = f"{BASE_URL}/api/v1/his/prebook-surgery"
        payload = {
            "enquiryId": self.test_enquiry_id,
            "doctorName": "Dr. S. Prashanth, Sr. Cardiologist",
            "procedureName": "Coronary Angiogram & Stenting",
            "proposedSurgeryDate": "2026-08-12",
            "otRoom": "OT-2 (Cardio Suite)",
            "remarks": "Stage 6 HIS OT Prebooking"
        }
        req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), headers={"Content-Type": "application/json"}, method="POST")
        with urllib.request.urlopen(req) as res:
            self.assertEqual(res.status, 200)
            data = json.loads(res.read().decode("utf-8"))
            self.assertIn("hisBookingId", data)
            self.assertEqual(data["enquiry"]["status"], "SURGERY_FIXED")
            self.assertEqual(data["enquiry"]["hisSyncStatus"], "SYNCED")

    def test_04_his_patient_search(self):
        url = f"{BASE_URL}/api/v1/his/patient-search?search=Karthik"
        req = urllib.request.Request(url, method="GET")
        with urllib.request.urlopen(req) as res:
            self.assertEqual(res.status, 200)
            data = json.loads(res.read().decode("utf-8"))
            self.assertIn("results", data)
            self.assertGreater(data["total"], 0)
            self.assertEqual(data["results"][0]["patientName"], "Karthik Raja")

if __name__ == "__main__":
    unittest.main()
