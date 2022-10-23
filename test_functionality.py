import unittest
from unittest.mock import patch
import functionality


class TestFunctionality(unittest.TestCase):
    def test__parse_challenges(self):
        with patch('functionality.requests.get') as mocked_get:
            mocked_get.return_value.ok = True
            mocked_get.return_value.text = 'Success'
            response = functionality._parse_challenges()
            mocked_get.assert_called_with(
                'https://quizlet.com/ru/632318229/flash-cards/',
                headers=functionality.headers
            )
            self.assertEqual(response, 'Success')

            mocked_get.return_value.ok = False
            response = functionality._parse_challenges()
            mocked_get.assert_called_with(
                'https://quizlet.com/ru/632318229/flash-cards/',
                headers=functionality.headers
            )
            self.assertEqual(response, 'Failed to access the current website.')

    def test__parse_word(self):
        with patch('functionality.requests.get') as mocked_get:
            mocked_get.return_value.ok = True
            mocked_get.return_value.text = 'Success'
            response = functionality._parse_challenges()
            mocked_get.assert_called_with(
                'https://quizlet.com/ru/632318229/flash-cards/',
                headers=functionality.headers
            )
            self.assertEqual(response, 'Success')

            mocked_get.return_value.ok = False
            response = functionality._parse_challenges()
            mocked_get.assert_called_with(
                'https://quizlet.com/ru/632318229/flash-cards/',
                headers=functionality.headers
            )
            self.assertEqual(response, 'Failed to access the current website.')


if __name__ == '__main__':
    unittest.main()
