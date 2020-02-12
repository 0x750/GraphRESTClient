import GraphRESTClient as grc

client = grc.GraphRESTClient(
    'example.com', {
        'client_id' : "********-****-****-****-************",
        'scope' : "https://graph.microsoft.com/.default",
        'client_secret' : "***********************",
        'grant_type' : "client_credentials"
    }
)

rep = client.add_route('GET', '/v1.0/users').use({
    'pages' : 1
})

print(rep)
print(client)