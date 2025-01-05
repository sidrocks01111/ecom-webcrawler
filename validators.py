import ssl
from urllib.parse import urljoin, urlparse
from urllib.robotparser import RobotFileParser
import urllib.request



class Validator:

    @staticmethod
    def validate_url(url):
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except ValueError:
            return False
        