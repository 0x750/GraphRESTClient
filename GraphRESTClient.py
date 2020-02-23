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

            def _closure(options=dict()):
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
                        print("Error " + str(res.status) + " : " + res.read().decode('utf-8'))
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
            self.options['query_options']['$top'] = top_value
            return self

        def select(self, select_value):
            self.options['query_options']['$select'] = select_value
            return self

        def pages(self, pages_value):
            self.options['pages'] = pages_value
            return self

        def __str__(self):
            return "  " + '\t' + self.route

    def __init__(self, domain, application):
        self._OAuthcreds = application
        self._domain = domain
        self._session_token = self._get_session_token(self._OAuthcreds)
        
    def _get_session_token(self, cred):
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
            raise Exception("Error " + str(res.status) + " : Can't get access token")
        else:
            data = res.read().decode('utf-8')
            conn.close()
            return json.loads(data)

    def api(self, route):
        return self.GraphRESTRoute(route, self)

    def __str__(self):
        return """\
Graph REST Client
Tenant URL : """ + self._domain + """
Session Token : """ + self._session_token['token_type'] + " " + self._session_token['access_token'][:40] + "..."
