GET = 'GET'
POST = 'POST'


def dict_to_querystring(params):
    if params not in [None, {}]:
        return '&'.join([f'{k}={v}' for k, v in params.items()])
    else:
        return ''


def make_request(session, url, timeout=10, headers=None, params=None, data=None, request_type=GET):
    if request_type == GET:
        response = session.get(url, params=params, data=data, headers=headers, timeout=timeout)
    elif request_type == POST:
        response = session.post(url, params=params, data=data, headers=headers, timeout=timeout)
    else:
        raise Exception(f'Request type not supported: {request_type}')
    return response
