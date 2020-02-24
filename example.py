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

print(client)
print(rep)