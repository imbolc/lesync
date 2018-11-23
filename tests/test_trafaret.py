import pytest

from django.urls import path
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.sessions import SessionMiddlewareStack

from lesync import ApiConsumer
from utils import HttpRequest


application = ProtocolTypeRouter({
    'http': SessionMiddlewareStack(
        URLRouter([
            path('<path:path>', ApiConsumer),
        ]),
    ),
})


http = HttpRequest(application)


@pytest.mark.asyncio
async def test_query_validation():
    resp = await http.get('/query-validation')
    assert resp.status == 400
    assert resp.json == {'errors': {'id': 'is required'}}
    resp = await http.get('/query-validation?id=foo')
    assert resp.status == 400
    resp = await http.get('/query-validation?id=1&foo=bar')
    assert resp.status == 400
    assert resp.json == {'errors': {'foo': 'foo is not allowed key'}}
    resp = await http.get('/query-validation?id=1')
    assert resp.status == 200
    assert resp.json == {'id': 1}


@pytest.mark.asyncio
async def test_json_validation():
    resp = await http.post('/json-validation')
    assert resp.status == 400
    assert resp.json == {'errors': {'id': 'is required'}}
    resp = await http.post('/json-validation', {'id': 'foo'})
    assert resp.status == 400
    resp = await http.post('/json-validation', {'id': 1, 'foo': 'bar'})
    assert resp.status == 400
    assert resp.json == {'errors': {'foo': 'foo is not allowed key'}}
    resp = await http.post('/json-validation', {'id': 1})
    assert resp.status == 200
    assert resp.json == {'id': 1}
