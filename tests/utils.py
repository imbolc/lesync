from json import loads, dumps
from types import SimpleNamespace

from channels.testing import HttpCommunicator


class Response(SimpleNamespace):
    @property
    def json(self):
        return loads(self.body)

    @property
    def text(self):
        return self.body.decode('utf-8')

    def get_header(self, name):
        return dict(self.headers).get(name)


class HttpRequest:
    def __init__(self, consumer):
        self.consumer = consumer

    async def get(self, path):
        communicator = HttpCommunicator(self.consumer, method='GET', path=path)
        r = await communicator.get_response()
        return Response(**r)

    async def post(self, path, body=None):
        if not isinstance(body, bytes):
            data = body or {}
            body = dumps(data).encode('utf-8')
        communicator = HttpCommunicator(
            self.consumer, method='POST', path=path, body=body)
        r = await communicator.get_response()
        return Response(**r)
