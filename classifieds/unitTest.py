import os
import tempfile
import unittest

import classifieds


class ClassifiedsTestCase(unittest.TestCase):

    # This method is designed to set up a temporary database, such that the tests won't affect the real database
    def setUp(self):
        self.db_fd, classifieds.app.config['DATABASE'] = tempfile.mkstemp()
        self.app = classifieds.app.test_client()

    # All these middle methods are individual tests. unittest will automatically run all of these methods and tell you
    # which tests, if any, failed. If they all pass, then it says "OK"
    def test_header_presence(self):
        rv = self.app.get('/')
        assert b"<h1>Bethel University's Classified Listings</h1>" in rv.data

    def test_search_page(self):
        rv = self.app.get('/search-page')
        assert b'<label for="title">Title contains:</label>' in rv.data

    def test_add_classified(self):
        rv = self.app.get('/add-classified')
        assert b'<form id="classifieds" method="POST" action="/submit-ad">' in rv.data

    def test_post_functions(self):
        # This dict corresponds to the form <form><textarea id="input"> in templates/feedback.html;
        # the keys of the dict correspond to the ids of the input fields, and the values of the dict correspond to the
        # user's answers. This should throw a 500 because it doesn't have a mail client to send the email, but the
        # request is valid.
        rv = self.app.post('/submit-feedback', data=dict(
            input="fooey on youey"
        ), follow_redirects=True)
        print rv
        assert b' ' in rv.data

    # Corresponding to the setUp method, this method unlinks the temporary database so that it can be released from RAM
    def tearDown(self):
        os.close(self.db_fd)
        os.unlink(classifieds.app.config['DATABASE'])

if __name__ == '__main__':
    unittest.main()
