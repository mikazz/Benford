from flask_testing import TestCase
import unittest
from webapp.app.app import app


class BaseTestCase(TestCase):
    def create_app(self):
        return app

    def setUp(self):
        self.app = app.test_client()

    def tearDown(self):
        pass


class TestMainBlueprint(BaseTestCase):
    def test_index(self):
        # Ensure Flask is setup # Ensure Connection to Redis is established.
        # When
        response = self.client.get("/", follow_redirects=True)
        # Then
        self.assertEqual(response.status_code, 200)

    def test_dashboard_index(self):
        # When
        response = self.client.get("/rq", follow_redirects=True)
        # Then
        self.assertEqual(response.status_code, 200)

    def test_get_jobs(self):
        # When
        response = self.client.get("/jobs", follow_redirects=True)
        # Then
        self.assertEqual(response.status_code, 200)


if __name__ == "__main__":
    unittest.main()
