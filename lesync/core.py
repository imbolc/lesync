from functools import wraps
from json import loads, JSONDecodeError
from types import AsyncGeneratorType

from channels.generic.http import AsyncHttpConsumer
from channels.auth import get_user
from channels.http import AsgiRequest
from channels.exceptions import RequestAborted, RequestTimeout

from django import http, urls
from django.http import HttpResponse, JsonResponse, HttpResponseForbidden
from django.utils.functional import cached_property

from .utils import encoded_headers


class RaisedResponse(Exception):
    def __init__(self, response):
        self.response = response


class Request(AsgiRequest):
    @cached_property
    def json(self):
        try:
            return loads(self._body)
        except JSONDecodeError:
            raise RaisedResponse(http.HttpResponseBadRequest('Broken json'))

    async def load_user(self):
        if not hasattr(self, 'user'):
            self.user = await get_user(self.scope)
        return self.user


class StreamResponse(dict):
    def __init__(self, stream, status_code=200, headers=None):
        assert isinstance(stream, AsyncGeneratorType)
        self.stream = stream
        self.status_code = status_code
        headers = headers or [('content-type', 'text/html')]
        self.update(dict(headers))


class ApiConsumer(AsyncHttpConsumer):
    async def handle(self, body):
        try:
            request = Request(self.scope, body)
        except UnicodeDecodeError:
            response = http.HttpResponseBadRequest()
        except RequestTimeout:
            response = HttpResponse('408 Request Timeout (upload too slow)',
                                    status=408)
        except RequestAborted:
            # Client closed connection on us mid request. Abort!
            return
        else:
            try:
                response = await self.get_response(request)
            except RaisedResponse as e:
                response = e.response
        if isinstance(response, StreamResponse):
            await self.send_headers(headers=encoded_headers(response))
            async for chunk in response.stream:
                if isinstance(chunk, str):
                    chunk = chunk.encode('utf-8')
                    await self.send_body(chunk, more_body=True)
            await self.send_body(b'')
        else:
            await self.send_response(response.status_code, response.content,
                                     headers=encoded_headers(response))

    async def get_response(self, request):
        try:
            func, args, kwargs = urls.resolve(request.path)
        except urls.Resolver404:
            data = {'error': 'Page not found'}, 404
        else:
            data = await func(request, *args, **kwargs)
            if isinstance(data, (HttpResponse, StreamResponse)):
                return data
        return self._to_response(data)

    def _to_response(self, data):
        payload, status, headers = self._normalize_response_tuple(data)
        if isinstance(payload, AsyncGeneratorType):
            return StreamResponse(payload, status, headers)
        response = JsonResponse(payload, status=status)
        for k, v in dict(headers).items():
            response[k] = v
        return response

    def _normalize_response_tuple(self, data):
        assert isinstance(data, (dict, AsyncGeneratorType, tuple))
        if isinstance(data, (dict, AsyncGeneratorType)):
            data = data, 200, []
        if len(data) == 2:
            data += ([], )
        assert len(data) == 3
        return data


def login_required(f):
    @wraps(f)
    async def wrapper(request, *args, **kwargs):
        user = await request.load_user()
        if not user.is_authenticated:
            return HttpResponseForbidden('You have to log in')
        return await f(request, *args, **kwargs)
    return wrapper


def staff_member_required(f):
    @wraps(f)
    @login_required
    async def wrapper(request, *args, **kwargs):
        if not request.user.is_staff:
            return HttpResponseForbidden('Access denied')
        return await f(request, *args, **kwargs)
    return wrapper
