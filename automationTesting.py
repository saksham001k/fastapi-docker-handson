import os
import unittest
from urllib.error import HTTPError
from urllib.request import Request, urlopen
import json

BASE_URL = os.getenv("BASE_URL", "http://127.0.0.1:8000").rstrip("/")


def call(path, method="GET", payload=None):
    body = json.dumps(payload).encode() if payload is not None else None
    request = Request(BASE_URL + path, data=body, method=method)
    if body is not None:
        request.add_header("Content-Type", "application/json")
    try:
        response = urlopen(request, timeout=5)
    except HTTPError as error:
        response = error
    with response:
        data = response.read()
        return response.status, json.loads(data) if data else None


class ApiTests(unittest.TestCase):
    def test_root(self):
        status, data = call("/")
        self.assertEqual(status, 200)
        self.assertEqual(data["sap_id"], "590015169")
        self.assertEqual(data["location"], "Dehradun")
        self.assertEqual(data["demo"], "unit4-combined-task3")

    def test_health(self):
        self.assertEqual(call("/health"), (200, {"status": "healthy"}))

    def test_list_and_filter(self):
        status, data = call("/students")
        self.assertEqual(status, 200)
        self.assertTrue(data)
        status, data = call("/students?branch=cse")
        self.assertEqual(status, 200)
        self.assertIn(1, [student["id"] for student in data])
        self.assertTrue(all(student["branch"].upper() == "CSE" for student in data))

    def test_get_and_missing_student(self):
        self.assertEqual(call("/students/1"), (200, {"id": 1, "name": "Aarav", "branch": "CSE"}))
        self.assertEqual(call("/students/999999")[0], 404)

    def test_invalid_create(self):
        self.assertEqual(call("/students", "POST", {"name": "Test"})[0], 422)

    def test_create_update_delete(self):
        student = {"name": "Test Student", "branch": "IT"}
        status, created = call("/students", "POST", student)
        self.assertEqual(status, 201)
        student_id = created["id"]
        path = f"/students/{student_id}"
        try:
            self.assertEqual(call(path), (200, {"id": student_id, **student}))
            updated = {"name": "Updated Student", "branch": "CSE"}
            self.assertEqual(call(path, "PUT", updated), (200, {"id": student_id, **updated}))
            self.assertEqual(call(path), (200, {"id": student_id, **updated}))
            self.assertEqual(call(path, "DELETE"), (204, None))
            self.assertEqual(call(path)[0], 404)
        finally:
            call(path, "DELETE")


if __name__ == "__main__":
    unittest.main(verbosity=2)
