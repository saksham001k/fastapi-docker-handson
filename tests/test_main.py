import unittest

from fastapi.testclient import TestClient
from main import app


class StudentApiTests(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_home(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["sap_id"], "590015169")
        self.assertEqual(response.json()["location"], "Dehradun")

    def test_health(self):
        self.assertEqual(self.client.get("/health").json(), {"status": "healthy"})

    def test_students(self):
        response = self.client.get("/students")
        self.assertEqual(response.status_code, 200)
        self.assertEqual([student["id"] for student in response.json()], [1, 2, 3])

    def test_unknown_route(self):
        self.assertEqual(self.client.get("/missing").status_code, 404)

    def test_request_logging(self):
        with self.assertLogs("student-api", level="INFO") as logs:
            self.client.get("/health?token=not-a-real-secret")
        message = " ".join(logs.output)
        self.assertIn("GET /health status=200 duration_ms=", message)
        self.assertNotIn("token=", message)


if __name__ == "__main__":
    unittest.main()
