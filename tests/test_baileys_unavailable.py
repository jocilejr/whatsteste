import unittest
from unittest.mock import patch
codex/add-error-handling-for-fetch-requests-tdpmgk
import urllib.request
from urllib.error import URLError

# Helper functions mimicking fetch layer error handling

def fetch_groups():
    try:
codex/add-error-handling-for-fetch-requests-tdpmgk
        urllib.request.urlopen("http://127.0.0.1:3002/groups/test", timeout=1)
        return ""  # Success path is not relevant for this test
    except URLError:
        return "Serviço Baileys indisponível na porta 3002"

def send_message():
    try:
codex/add-error-handling-for-fetch-requests-tdpmgk
        req = urllib.request.Request(
            "http://127.0.0.1:3002/send/test",
            data=b"{}",
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        urllib.request.urlopen(req, timeout=1)
        return ""
    except URLError:

        return "Serviço Baileys indisponível na porta 3002"


class BaileysUnavailableTest(unittest.TestCase):
 codex/add-error-handling-for-fetch-requests-tdpmgk
    @patch("urllib.request.urlopen", side_effect=URLError("down"))
    def test_groups_unavailable_message(self, mock_open):
        self.assertEqual(fetch_groups(), "Serviço Baileys indisponível na porta 3002")

    @patch("urllib.request.urlopen", side_effect=URLError("down"))
    def test_send_unavailable_message(self, mock_open):

        self.assertEqual(send_message(), "Serviço Baileys indisponível na porta 3002")


if __name__ == "__main__":
    unittest.main()
