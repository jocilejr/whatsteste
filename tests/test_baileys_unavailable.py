import unittest
from unittest.mock import patch
import requests

# Helper functions mimicking fetch layer error handling

def fetch_groups():
    try:
        requests.get("http://127.0.0.1:3002/groups/test", timeout=1)
        return ""  # Success path is not relevant for this test
    except requests.exceptions.RequestException:
        return "Serviço Baileys indisponível na porta 3002"

def send_message():
    try:
        requests.post("http://127.0.0.1:3002/send/test", json={}, timeout=1)
        return ""
    except requests.exceptions.RequestException:
        return "Serviço Baileys indisponível na porta 3002"


class BaileysUnavailableTest(unittest.TestCase):
    @patch("requests.get", side_effect=requests.exceptions.ConnectionError)
    def test_groups_unavailable_message(self, mock_get):
        self.assertEqual(fetch_groups(), "Serviço Baileys indisponível na porta 3002")

    @patch("requests.post", side_effect=requests.exceptions.ConnectionError)
    def test_send_unavailable_message(self, mock_post):
        self.assertEqual(send_message(), "Serviço Baileys indisponível na porta 3002")


if __name__ == "__main__":
    unittest.main()
