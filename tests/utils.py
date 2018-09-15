from importlib import import_module
from json import loads, dumps
from types import SimpleNamespace

from django.conf import settings
from channels.testing import HttpCommunicator
from channels.auth import login


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
    def __init__(self, app):
        self.app = app

    async def get(self, path, headers=None, user=None):
        if user:
            headers = await self._login(headers, user)
        communicator = HttpCommunicator(
            self.app, method='GET', path=path, headers=headers)
        r = await communicator.get_response()
        return Response(**r)

    async def post(self, path, body=None, headers=None, user=None):
        if not isinstance(body, bytes):
            data = body or {}
            body = dumps(data).encode('utf-8')
        if user:
            headers = await self._login(headers, user)
        communicator = HttpCommunicator(
            self.app, method='POST', path=path, body=body, headers=headers)
        r = await communicator.get_response()
        return Response(**r)

    async def _login(self, headers, user):
        SessionStore = import_module(settings.SESSION_ENGINE).SessionStore
        session = SessionStore()
        session.create()
        scope = {'session': session}
        await login(scope, user=user)
        session.save()
        cookie = f'{settings.SESSION_COOKIE_NAME}={session.session_key}'
        headers = headers or []
        return headers + [(b'cookie', cookie.encode('utf-8'))]
