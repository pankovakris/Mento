import unittest
from unittest.mock import patch, Mock
import app.parser.linkedin_parser as linkedin_parser


class TestLinkedInParser(unittest.TestCase):

    def setUp(self):
        self.linkedin_url = "https://www.linkedin.com/company/testcompany"
        self.mock_html = """
        <html>
        <body>
            <h1 class="top-card-layout__title">Test Company (YC S25)</h1>
            <span class="line-clamp-2">We build cool things</span>
            <p class="break-words">YC S25 startup in stealth</p>
        </body>
        </html>
        """

    @patch("app.parser.linkedin_parser.requests.get")
    def test_linkedin_check_yc_mention_positive(self, mock_get):
        mock_resp = Mock()
        mock_resp.status_code = 200
        mock_resp.text = self.mock_html
        mock_get.return_value = mock_resp

        matched, match_info = linkedin_parser.linkedin_check_yc_mention(
            self.linkedin_url
        )

        self.assertTrue(matched)
        self.assertIn("location", match_info)
        self.assertIn("snippet", match_info)
        self.assertEqual(match_info["location"], "name")

    @patch("app.parser.linkedin_parser.requests.get")
    def test_linkedin_check_yc_mention_no_match(self, mock_get):
        mock_resp = Mock()
        mock_resp.status_code = 200
        mock_resp.text = "<html><body><h1>Random Company</h1></body></html>"
        mock_get.return_value = mock_resp

        matched, match_info = linkedin_parser.linkedin_check_yc_mention(
            self.linkedin_url
        )

        self.assertFalse(matched)
        self.assertIsNone(match_info)

    def test_load_existing_companies_file_not_exist(self):
        companies = linkedin_parser.load_existing_companies("nonexistent_file.json")
        self.assertEqual(companies, [])


if __name__ == "__main__":
    unittest.main()
