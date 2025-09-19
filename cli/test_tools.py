import unittest
from unittest.mock import patch, MagicMock
import ai.tools as tools

class TestTools(unittest.TestCase):

    def setUp(self):
        self.user = "user_shreya"
        self.event = {
            "id": 1,
            "title": "Test Event",
            "date": "2025-01-01",
            "start_time": "10:00",
            "end_time": "11:00"
        }

    @patch("database.add_event")
    def test_add_event_tool(self, mock_add):
        mock_add.return_value = self.event
        result = tools.add_event_tool("Test Event", "2025-01-01", "10:00", "11:00", self.user)
        self.assertTrue(result["success"])
        self.assertIn("Event added", result["message"])

    @patch("database.list_events_on_date")
    def test_list_events_on_date_tool(self, mock_list):
        mock_list.return_value = [self.event]
        result = tools.list_events_on_date_tool("2025-01-01", self.user)
        self.assertTrue(result["success"])
        self.assertIn("Test Event", result["message"])

    @patch("database.list_events_by_title")
    def test_list_events_by_title_tool(self, mock_list):
        mock_list.return_value = [self.event]
        result = tools.list_events_by_title_tool("Test Event", self.user)
        self.assertTrue(result["success"])
        self.assertIn("Test Event", result["message"])

    @patch("database.list_events_next_n_days")
    def test_list_events_next_n_days_tool(self, mock_list):
        mock_list.return_value = [self.event]
        result = tools.list_events_next_n_days_tool(7, self.user)
        self.assertTrue(result["success"])
        self.assertEqual(len(result["events"]), 1)

    @patch("database.update_event")
    def test_update_event_tool(self, mock_update):
        mock_update.return_value = True
        result = tools.update_event_tool(1, title="Updated Event", user=self.user)
        self.assertTrue(result["success"])
        self.assertIn("updated successfully", result["message"])

    @patch("database.delete_event")
    def test_delete_event_tool(self, mock_delete):
        mock_delete.return_value = True
        result = tools.delete_event_tool(1, self.user)
        self.assertTrue(result["success"])
        self.assertIn("deleted successfully", result["message"])

    @patch("database.delete_event_by_title")
    def test_delete_event_by_title_tool(self, mock_delete):
        mock_delete.return_value = True
        result = tools.delete_event_by_title_tool("Test Event", self.user)
        self.assertTrue(result["success"])
        self.assertIn("deleted", result["message"])


if __name__ == "__main__":
    unittest.main()
