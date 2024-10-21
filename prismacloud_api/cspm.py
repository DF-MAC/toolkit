import json
import time
import requests
import threading


class PrismaCloudAPIMixin():
    """ 
    A mixin class for handling API requests and output related to the Prisma Cloud API.
    Contains functions for making authenticated requests, handling pagination, retrying failed requests, and managing API tokens.
    """

    def suppress_warnings_when_verify_false(self):
        """ 
        Disable security warnings when SSL certificate verification is turned off.
        """
        if self.verify is False:
            # Disabling warnings about insecure HTTPS requests
            requests.packages.urllib3.disable_warnings(
                requests.packages.urllib3.exceptions.InsecureRequestWarning)

    def login(self, url=None):
        """
        Perform the login request to the Prisma Cloud API and retrieve the authentication token.
        """
        self.suppress_warnings_when_verify_false()

        if not url:
            url = f'https://{self.api}/login'

        action = 'POST'
        request_headers = {'Content-Type': 'application/json',
                           'User-Agent': self.user_agent}
        body_params_json = json.dumps(
            {'username': self.identity, 'password': self.secret})

        # Use the retry logic wrapper to perform the request
        api_response = self._perform_request_with_retries(
            action, url, headers=request_headers, data=body_params_json)

        if api_response.ok:
            with self.lock:
                api_response_data = json.loads(api_response.content)
                self.token = api_response_data.get('token')
                self.token_expiry = time.time() + self.token_limit
        else:
            self.error_and_exit(api_response.status_code, 'API (%s) responded with an error\n%s' % (
                url, api_response.text))

        if self.debug:
            print('New API Token:', self.token)

    def extend_login(self):
        """
        Extend the existing login session by requesting a new authentication token.
        """
        self.suppress_warnings_when_verify_false()

        url = f'https://{self.api}/auth_token/extend'
        action = 'GET'
        request_headers = {'Content-Type': 'application/json',
                           'User-Agent': self.user_agent, 'x-redlock-auth': self.token}

        # Use the retry logic wrapper to perform the request
        api_response = self._perform_request_with_retries(
            action, url, headers=request_headers)

        if api_response.ok:
            with self.lock:
                api_response_data = json.loads(api_response.content)
                self.token = api_response_data.get('token')
                self.token_expiry = time.time() + self.token_limit
        else:
            self.error_and_exit(api_response.status_code, 'API (%s) responded with an error\n%s' % (
                url, api_response.text))

        if self.debug:
            print('Extending API Token')

    def execute(self, action, endpoint, query_params=None, body_params=None, request_headers=None, force=False, paginated=False):
        """
        Execute a general API request with support for retries, token renewal, and pagination.
        """
        self.suppress_warnings_when_verify_false()

        with self.lock:
            if not self.token or self.is_token_expired():
                self.login()

        results = []
        more = True

        while more:
            if self.is_token_expired():
                self.extend_login()

            url = f'https://{self.api}/{endpoint}'

            if not request_headers:
                request_headers = {'Content-Type': 'application/json',
                                   'User-Agent': self.user_agent, 'x-redlock-auth': self.token}

            body_params_json = json.dumps(body_params) if body_params else None

            # Use the retry logic wrapper to perform the request
            api_response = self._perform_request_with_retries(
                action, url, headers=request_headers, params=query_params, data=body_params_json)

            if api_response.ok:
                if not api_response.content:
                    return None
                if api_response.headers.get('Content-Type') == 'application/x-gzip':
                    return api_response.content
                if api_response.headers.get('Content-Type') == 'text/csv':
                    return api_response.content.decode('utf-8')

                try:
                    result = json.loads(api_response.content)
                except ValueError:
                    self.logger.error('JSON parsing error.')
                    if force:
                        return results
                    self.error_and_exit(
                        api_response.status_code, 'Error parsing response')

                if paginated:
                    results.extend(result['items'])
                    more = 'nextPageToken' in result and result['nextPageToken']
                    if more:
                        body_params = {'pageToken': result['nextPageToken']}
                else:
                    return result
            else:
                self.logger.error('API error response.')

        return results

    def _perform_request_with_retries(self, action, url, headers, params=None, data=None):
        """
        Wrapper to perform requests with retry logic and exponential backoff.
        """
        for attempt, wait_time in enumerate(self.retry_waits, start=1):
            try:
                response = requests.request(
                    action, url, headers=headers, params=params, data=data, verify=self.verify, timeout=self.timeout)
                if response.ok:
                    return response
            except requests.exceptions.RequestException as e:
                self.logger.error(
                    f'Request exception during attempt {attempt}: {e}')
            time.sleep(wait_time)

        # Final attempt without retries
        return requests.request(action, url, headers=headers, params=params, data=data, verify=self.verify, timeout=self.timeout)

    def is_token_expired(self):
        """ Thread-safe check if the token is expired """
        with self.lock:
            return time.time() >= self.token_expiry if self.token_expiry else True

    @classmethod
    def error_and_exit(cls, error_code, error_message='', system_message=''):
        raise SystemExit(f'\n\nStatus Code: {error_code}\n{
                         error_message}\n{system_message}\n')

    def error_report(self):
        if self.logger.error.counter > 0:
            print(f'API responded with {self.logger.error.counter} error(s)')

    @classmethod
    def progress(cls, txt=None):
        if txt:
            print(txt)
