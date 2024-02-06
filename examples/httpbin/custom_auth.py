def hit_custom_auth(request, variables):
    request.headers.update({
        'CB-ACCESS-SIGN': "sign",
        'CB-ACCESS-TIMESTAMP': "timestamp",
        'CB-ACCESS-KEY': "key",
    })
    return request
