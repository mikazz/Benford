"""
    Tests
"""

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



    def test_post_job_get_text(self):
        """
            Test Add Job
        """

        # Given
        payload = {
            "page_url": "https://www.google.com/",
            "function": "get_text"
        }

        # When
        response = self.client.post('/job', data=payload)

        # Then
        self.assertEqual("success", response.json['status'])
        self.assertEqual(202, response.status_code)

    def test_post_job_get_images(self):
        """
            Test Add Job
        """

        # Given
        payload = {
            "page_url": "https://www.google.com/",
            "function": "get_images"
        }

        # When
        response = self.client.post('/job', data=payload)

        # Then
        self.assertEqual("success", response.json['status'])
        self.assertEqual(202, response.status_code)

    def test_post_job_with_bad_function(self):
        payload = {
            "page_url": "https://www.google.com/",
            "function": "get_"
        }

        response = self.client.post('/job', data=payload)
        # 400 - Bad request
        self.assertEqual(400, response.status_code)

    def test_post_job_with_no_function(self):
        payload = {
            "page_url": "https://www.google.com/"
        }

        response = self.client.post('/job', data=payload)
        # 400 - Bad request
        self.assertEqual(400, response.status_code)

    def test_post_long_job(self):
        """
            curl -X POST -F "duration=3" http://127.0.0.1:5000/long_job
        """
        payload = {
            "duration": "3"
        }
        response = self.client.post("/long_job", data=payload, follow_redirects=True)
        # 202 - Accepted
        self.assertEqual(202, response.status_code)


if __name__ == "__main__":
    unittest.main()
