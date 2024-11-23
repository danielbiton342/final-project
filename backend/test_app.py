import unittest
import json
from bson import ObjectId
from app import app, mongo


class MusicAppTestCase(unittest.TestCase):
    def setUp(self):
        """Set up the test client and initialize the database."""
        self.app = app.test_client()
        self.app.testing = True

        # Clear the database before each test
        mongo.db.singers.delete_many({})

    def tearDown(self):
        """Clean up after each test."""
        mongo.db.singers.delete_many({})

    def _add_singer(self, name="John Doe", songs=None):
        """Helper method to add a singer and return its ID."""
        payload = {"name": name}
        if songs:
            payload["songs"] = songs

        response = self.app.post("/singers", json=payload)
        self.assertEqual(response.status_code, 200)
        return json.loads(response.data)["id"]

    def test_health_check(self):
        """Test the health check endpoint."""
        response = self.app.get("/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.data), {"status": "healthy"})

    def test_add_singer(self):
        """Test adding a new singer."""
        singer_id = self._add_singer(songs=["Song 1", "Song 2"])

        # Verify that the singer was added to the database
        response = self.app.get(f"/singers/{singer_id}")
        self.assertEqual(response.status_code, 200)

        data = json.loads(response.data)
        self.assertEqual(data["name"], "John Doe")
        self.assertEqual(data["songs"], ["Song 1", "Song 2"])

    def test_get_singers(self):
        """Test retrieving all singers."""
        self._add_singer("John Doe", ["Song 1", "Song 2"])

        response = self.app.get("/singers")
        self.assertEqual(response.status_code, 200)

        data = json.loads(response.data)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["name"], "John Doe")

    def test_update_singer_name(self):
        """Test updating a singer's name."""
        singer_id = self._add_singer()

        # Update the singer's name
        response = self.app.put(f"/singers/{singer_id}/name", json={"name": "Jane Doe"})
        self.assertEqual(response.status_code, 200)

        # Verify the update
        response = self.app.get(f"/singers/{singer_id}")
        data = json.loads(response.data)
        self.assertEqual(data["name"], "Jane Doe")

    def test_add_song_to_singer(self):
        """Test adding songs to an existing singer."""
        singer_id = self._add_singer()

        # Add songs to the singer
        response = self.app.put(
            f"/singers/{singer_id}", json={"songs": ["Song 1", "Song 2"]}
        )
        self.assertEqual(response.status_code, 200)

        # Verify songs were added
        response = self.app.get(f"/singers/{singer_id}")
        data = json.loads(response.data)
        self.assertIn("Song 1", data["songs"])
        self.assertIn("Song 2", data["songs"])

    def test_delete_song(self):
        """Test deleting a song from a singer."""
        # Add a singer with songs
        singer_id = self._add_singer(songs=["Song 1", "Song 2"])

        # Delete a song
        response = self.app.delete(f"/singers/{singer_id}/songs/Song 1")
        self.assertEqual(response.status_code, 200)

        # Verify the song was deleted
        response = self.app.get(f"/singers/{singer_id}")
        data = json.loads(response.data)
        self.assertNotIn("Song 1", data["songs"])
        self.assertIn("Song 2", data["songs"])

    def test_delete_singer(self):
        """Test deleting a singer."""
        singer_id = self._add_singer()

        response = self.app.delete(f"/singers/{singer_id}")
        self.assertEqual(response.status_code, 200)

        # Verify the singer was deleted
        response = self.app.get(f"/singers/{singer_id}")
        self.assertEqual(response.status_code, 404)


if __name__ == "__main__":
    unittest.main()
