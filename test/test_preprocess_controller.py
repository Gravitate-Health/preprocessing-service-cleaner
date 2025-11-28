import unittest

from flask import json

from preprocessor.test import BaseTestCase


class TestPreprocessController(BaseTestCase):
    """PreprocessController integration test stubs"""

    def test_preprocess_post(self):
        """Test case for preprocess_post

        
        """
        body = None
        headers = { 
            'Accept': 'application/json',
            'Content-Type': 'application/json',
        }
        response = self.client.open(
            '/preprocess',
            method='POST',
            headers=headers,
            data=json.dumps(body),
            content_type='application/json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))


if __name__ == '__main__':
    unittest.main()
