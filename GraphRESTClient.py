import http.client, urllib.parse
import datetime
import json

class GraphRESTClient:

    class GraphRESTRoute:

        def __init__(self, method, route, client):
            self.route = route
            if method in ['GET', 'POST']:
                self.method = method
            else:
                raise ValueError(method + ' : This method is not yet supported')
            self._closure = self._make_closure(self.route, self.method, client)

        def _make_closure(self, route, method, client):
            def _closure(options=dict()):
                #Multiple pages management
                _pages = options.get('pages', 1)
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

        def use(self, options=None):
            return self._closure(options)

        def __str__(self):
            return "  " + self.method + '\t' + self.route

    def __init__(self, domain, application):
        self._OAuthcreds = application
        self._domain = domain
        self._session_token = self._get_session_token(self._OAuthcreds)
        self.routes = []

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

    def add_route(self, route, method):
        self.routes.append(self.GraphRESTRoute(route, method, self))
        return self.routes[len(self.routes) - 1]

    def get_route(self, route, method):
        for _route in self.routes:
            if hash(_route.route + _route.method) == hash(route + method):
                return _route
        return self.add_route(route, method)

    def __str__(self):
        return """\
Graph REST Client
Tenant URL : """ + self._domain + """
Session Token : """ + self._session_token['token_type'] + " " + self._session_token['access_token'][:40] + """...
Routes :\n""" + '\n'.join(["  " + str(self.routes.index(route)) + str(route)
    for route in self.routes])
