import unittest
import os
from unittest.mock import patch

import functionality

QUIZLET_LINK = os.getenv('QUIZLET_LINK')


class TestFunctionality(unittest.TestCase):
    def test__parse_challenges(self):
        with patch('functionality.requests.get') as mocked_get:
            url = QUIZLET_LINK[:-4]

            mocked_get.return_value.ok = True
            mocked_get.return_value.text = 'Success'
            response = functionality._parse_challenges()
            mocked_get.assert_called_with(
                url,
                headers=functionality.headers
            )
            self.assertEqual(response, 'Success')

            mocked_get.return_value.ok = False
            response = functionality._parse_challenges()
            mocked_get.assert_called_with(
                url,
                headers=functionality.headers
            )
            self.assertEqual(response, f'Failed to access the current website {url}.')

    def test__parse_word(self):
        with patch('functionality.requests.get') as mocked_get:
            word = 'examination'
            url = f'https://dictionary.cambridge.org/dictionary/essential-american-english/{word}'

            mocked_get.return_value.ok = True
            mocked_get.return_value.text = 'Success'
            response = functionality._parse_word(word)
            mocked_get.assert_called_with(
                url,
                headers=functionality.headers
            )
            self.assertEqual(response, 'Success')

            mocked_get.return_value.ok = False
            response = functionality._parse_word(word)
            mocked_get.assert_called_with(
                url,
                headers=functionality.headers
            )
            self.assertEqual(response, f'Failed to access the current website {url}.')


if __name__ == '__main__':
    unittest.main()
