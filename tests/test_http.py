import unittest
from src.webserver.http import parse_request, HTTPParseError

class TestHTTPParsing(unittest.TestCase):
    def test_basic_get(self):
        raw = b"GET /index.html HTTP/1.1\r\nHost: localhost\r\nConnection: close\r\n\r\n"
        req = parse_request(raw, 4096)
        self.assertEqual(req.method, 'GET')
        self.assertEqual(req.path, '/index.html')
        self.assertTrue(req.version, 'HTTP/1.1')
        self.assertFalse(req.keep_alive)

    def test_missing_host(self):
        raw = b"GET / HTTP/1.1\r\nConnection: keep-alive\r\n\r\n"
        with self.assertRaises(HTTPParseError):
            parse_request(raw, 4096)

    def test_unsupported_method(self):
        raw = b"POST / HTTP/1.1\r\nHost: a\r\n\r\n"
        with self.assertRaises(HTTPParseError):
            parse_request(raw, 4096)

    def test_malformed_header_line(self):
        raw = b"GET / HTTP/1.1\r\nHost localhost\r\n\r\n"
        with self.assertRaises(HTTPParseError):
            parse_request(raw, 4096)

if __name__ == '__main__':
    unittest.main()
