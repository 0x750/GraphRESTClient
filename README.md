# Python Graph REST Client

> A Python client to use the Microsoft Graph API as an [application](https://docs.microsoft.com/en-us/graph/auth-v2-service).

### Exemple : 

```python
import GraphRESTClient as grc

client = grc.GraphRESTClient(
    'example.com', {
        'client_id' : "********-****-****-****-************",
        'scope' : "https://graph.microsoft.com/.default",
        'client_secret' : "***********************",
        'grant_type' : "client_credentials"
    }
)

rep = client.api(
        '/v1.0/users'
    ).select(
        ['displayName', 'mail']
    ).top(1).pages(2).get()
```

This request will return the display name and mail for the first user of the 2 first pages.

### TODO
- [x] More standard API
- [ ] POST, PATCH, DELETE methods
- [x] Auth Token management
    - [x] Renew Token
    - [x] Auto check and renew token