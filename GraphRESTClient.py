import http.client, urllib.parse
import datetime
import json

class GraphRESTClient:

    class GraphRESTRoute:

        def __init__(self, route, client):
            self.route = route
            self.options = {
                'query_options' : {},
                'pages' : 1
            }
            self._client = client

        def _make_closure(self, route, method, client):
            # Add query options to route
            if(self.options['query_options']):
                route = route + "?" + '&'.join([
                        k + "=" + urllib.parse.quote(str(i))
                        for k, i in self.options['query_options'].items()
                ])

            # Check if token is still valid
            if not client.is_token_still_valid():
                # if Token is not valid, get a new one
                client._renew_auth_token()

            def _closure(options):
                #Multiple pages management
                _pages = options['pages']
                _current_page = 0
                _next_link_exists = True
                _route = route

                data = []
                URI = "graph.microsoft.com"

                while _next_link_exists and _current_page < _pages:
                    _current_page += 1
                    headers = {
                        "Authorization": client._session_token['token_type'] + " " + client._session_token['access_token']
                    }
                    conn = http.client.HTTPSConnection(URI)
                    conn.request(method, _route, headers=headers)
                    res = conn.getresponse()
                    if res.status != 200:
                        raise Exception("Error " + str(res.status) + " : " + res.read().decode('utf-8'))
                        conn.close()
                        exit
                    else:
                        _data = json.loads(res.read().decode('utf-8'))
                        data.append(_data['value'])
                        if _current_page < _pages:
                            try:
                                _route = _data['@odata.nextLink'][len("https://graph.microsoft.com"):]
                            except:
                                _next_link_exists = False
                        conn.close()

                return [a for s in data for a in s]
            return _closure

        def get(self):
            return self._make_closure(self.route, 'GET', self._client)(self.options)

        def top(self, top_value):
            if top_value > 0:
                self.options['query_options']['$top'] = top_value
            else:
                self.options['query_options']['$top'] = 1
            return self

        def select(self, select_value):
            if isinstance(select_value, str):
                self.options['query_options']['$select'] = select_value
            elif isinstance(select_value, list):
                self.options['query_options']['$select'] = ",".join(select_value)
            else:
                raise Exception(".select() params must be str or list(str)")
            return self

        def pages(self, pages_value):
            if pages_value > 0:
                self.options['pages'] = pages_value
            else:
                self.options['pages'] = 1
            return self

        def __str__(self):
            return self.route + "\n\t" + "Pages : " + str(self.options['pages'])

    def __init__(self, domain, application):
        self._OAuthcreds = application
        self._domain = domain
        self._session_token = self._get_session_token(self._OAuthcreds)
        self._token_expiration = self._get_token_expiration()
        
    def _get_session_token(self, cred, silent=False):
        URI = "login.microsoftonline.com"
        headers = {
            'Content-Type': "application/x-www-form-urlencoded"
        }
        form = urllib.parse.urlencode(cred)
        conn = http.client.HTTPSConnection(URI)
        conn.request('POST', '/' + self._domain + '/oauth2/v2.0/token', body=form, headers=headers)
        res = conn.getresponse()
        if res.status != 200:
            conn.close()
            if not silent:
                raise Exception("Error " + str(res.status) + " : Can't get access token")
        else:
            data = res.read().decode('utf-8')
            conn.close()
            return json.loads(data)

    def _get_token_expiration(self):
        return datetime.datetime.now() + datetime.timedelta(seconds=3600)

    def get_remaining_token_validity_seconds(self, asStr=False):
        if asStr:
            return str((self._token_expiration - datetime.datetime.now()).total_seconds())
        else:
            return (self._token_expiration - datetime.datetime.now()).total_seconds()

    def is_token_still_valid(self):
        if self.get_remaining_token_validity_seconds() > 10:
            return True
        else:
            return False

    def _renew_auth_token(self):
        self._session_token = self._get_session_token(self._OAuthcreds, silent=True)
        self._token_expiration = self._get_token_expiration()

    def api(self, route):
        return self.GraphRESTRoute(route, self)

    def __str__(self):
        return """\
Graph REST Client
Tenant URL : """ + self._domain + """
Session Token : """ + self._session_token['token_type'] + " " + self._session_token['access_token'][:40] + "..." + """
Token still valid for """ + self.get_remaining_token_validity_seconds(True) + " seconds"
