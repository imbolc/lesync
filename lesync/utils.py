def encoded(s):
    return s if isinstance(s, bytes) else s.encode('utf-8')


def encoded_headers(headers):
    return [(encoded(k), encoded(v)) for k, v in headers.items()]

