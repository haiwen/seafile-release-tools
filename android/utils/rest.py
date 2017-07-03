import json
from urllib.parse import urljoin

import requests


class RestClient(requests.Session):

    def __init__(self, base_url, auth=None):
        super(RestClient, self).__init__()
        self.base_url = base_url
        self.auth = auth
        self.headers['Content-Type'] = 'application/json'
        self.headers['Accept'] = 'application/json'

    def request(self, method, url, *a, **kw):
        if url.startswith('http://') or url.startswith('https://'):
            pass
        else:
            url = urljoin(self.base_url, url.lstrip('/'))
        if 'data' in kw and isinstance(kw['data'], dict):
            kw['data'] = json.dumps(kw['data'])
        if self.auth:
            # otherwise requrests library would try to pick auth from ~/.netrc
            kw.setdefault('auth', self.auth)
        return super(RestClient, self).request(method, url, *a, **kw)
