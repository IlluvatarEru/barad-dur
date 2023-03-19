GET = 'GET'
POST = 'POST'


def make_request(session, url, timeout=10, headers=None, data=None, request_type=GET):
    if request_type == GET:
        response = session.get(url, data=data, headers=headers, timeout=timeout)
    elif request_type == POST:
        response = session.post(url, data=data, headers=headers, timeout=timeout)
    else:
        raise Exception(f'Request type not supported: {request_type}')
    return response
