import logging
import threading
from datetime import datetime, timedelta

from .cspm import PrismaCloudAPICSPM
from .cwpp import PrismaCloudAPICWPP
from .pccs import PrismaCloudAPIPCCS
from .pc_lib_utility import PrismaCloudUtility
from .version import version  # Import version from your version.py


class CallCounter:
    """ Decorator to determine number of calls for a method """

    def __init__(self, method):
        self.method = method
        self.counter = 0

    def __call__(self, *args, **kwargs):
        self.counter += 1
        return self.method(*args, **kwargs)


class PrismaCloudAPI(PrismaCloudAPICSPM, PrismaCloudAPICWPP, PrismaCloudAPIPCCS):
    """ Prisma Cloud API Class with thread safety improvements """

    def __init__(self):
        self.name = ''
        self.api = ''
        self.api_compute = ''
        self.identity = None
        self.secret = None
        self.verify = True
        self.debug = False
        self.timeout = None  # timeout=(16, 300)
        self.token = None
        self.token_expiry = None  # Use datetime for token expiry
        self.retry_status_codes = [425, 429, 500, 502, 503, 504]
        self.retry_waits = [1, 2, 4, 8, 16, 32]
        self.max_workers = 8
        self.lock = threading.Lock()  # Threading lock for shared resources
        self.logger = self._initialize_logger()
        # Set User-Agent
        self.user_agent = f"PrismaCloudAPI/{version}"

    def _initialize_logger(self):
        """ Initialize logger with a default configuration """
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.DEBUG)
        formatter = logging.Formatter(
            fmt='%(asctime)s: %(levelname)s: %(message)s', datefmt='%Y-%m-%d %I:%M:%S %p')
        file_handler = logging.FileHandler('error.log', delay=True)
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        logger.error = CallCounter(logger.error)  # Track error counts
        return logger

    def configure(self, settings, use_meta_info=True):
        """ Configures the API settings """
        with self.lock:  # Acquire lock to prevent race conditions during configuration
            self.name = settings.get('name', '')
            self.identity = settings.get('identity')
            self.secret = settings.get('secret')
            self.verify = settings.get('verify', True)
            self.debug = settings.get('debug', False)
            self.user_agent = settings.get('user_agent', self.user_agent)

            url = PrismaCloudUtility.normalize_url(settings.get('url', ''))
            if url:
                if url.endswith('.prismacloud.io') or url.endswith('.prismacloud.cn'):
                    self.api = url
                    if use_meta_info:
                        meta_info = self.meta_info()
                        if meta_info and 'twistlockUrl' in meta_info:
                            self.api_compute = PrismaCloudUtility.normalize_url(
                                meta_info['twistlockUrl'])
                else:
                    self.api_compute = PrismaCloudUtility.normalize_url(url)

    def is_token_expired(self):
        """ Check if the token is expired in a thread-safe manner """
        with self.lock:  # Ensure thread-safe read of token expiry
            return datetime.now() >= self.token_expiry if self.token_expiry else True

    def update_token(self, new_token, expiry_duration_seconds=590):
        """ Update token and set expiration time in a thread-safe manner """
        with self.lock:
            self.token = new_token
            self.token_expiry = datetime.now() + timedelta(seconds=expiry_duration_seconds)

    def get_token(self):
        """ Thread-safe access to get the current token """
        with self.lock:
            return self.token

    def debug_print(self, message):
        if self.debug:
            print(message)

    def make_api_call(self, endpoint, payload):
        """ Example API call method that checks token validity and uses retry logic """
        if self.is_token_expired():
            self.refresh_token()  # Hypothetical method to refresh the token

        with self.lock:  # Acquire lock before using shared resources
            headers = {
                "Authorization": f"Bearer {self.token}",
                "User-Agent": self.user_agent
            }

        # Placeholder for the actual API call logic
        # This should include proper error handling, retries, etc.
        response = None
        try:
            # Simulate an API call
            response = self._simulate_api_call(endpoint, payload, headers)
        except Exception as e:
            self.logger.error(f"API call failed: {e}")

        return response

    def _simulate_api_call(self, endpoint, payload, headers):
        """ Simulated API call - replace with actual HTTP request logic """
        # This would be where you'd use `requests` or another HTTP library
        # Ensure that retry logic is implemented here
        return {"status": "success"}

    def refresh_token(self):
        """ Simulated token refresh logic """
        # Acquire a new token and update in a thread-safe manner
        new_token = "new_generated_token"  # Hypothetically generate a new token
        self.update_token(new_token)
