import pytest

from django.urls import path
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.sessions import SessionMiddlewareStack
from django.contrib.auth import get_user_model

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


@pytest.fixture
def user():
    return get_user_model().objects.get_or_create(
        username='user', email='user@gmail.com')[0]


@pytest.fixture
def staff():
    return get_user_model().objects.get_or_create(
        username='staff', email='staff@gmail.com', is_staff=True)[0]


@pytest.mark.asyncio
async def test_dict_response():
    resp = await http.get('/dict')
    assert resp.status == 200
    assert resp.json == {'hello': 'world'}
    assert list(resp.headers) == [('Content-Type', 'application/json')]


@pytest.mark.asyncio
async def test_tuple2_response():
    resp = await http.get('/tuple2')
    assert resp.status == 400
    assert resp.json == {'bad': 'request'}


@pytest.mark.asyncio
async def test_tuple3_response():
    resp = await http.get('/tuple3')
    assert resp.status == 400
    assert resp.json == {'bad': 'request'}
    assert resp.get_header('Cache-Control') == 'no-cache'


@pytest.mark.asyncio
async def test_django_response():
    resp = await http.get('/django-response')
    assert resp.status == 200
    assert resp.text == 'foo'


@pytest.mark.asyncio
async def test_stream_response():
    resp = await http.get('/stream-response')
    assert resp.status == 200
    assert resp.text == '1,foo\n2,bar'
    assert list(resp.headers) == [('Content-Type', 'text/csv')]


@pytest.mark.asyncio
async def test_404():
    resp = await http.get('/404')
    assert resp.status == 404
    assert resp.json == {'error': 'Page not found'}


@pytest.mark.asyncio
async def test_empty_json_request():
    resp = await http.get('/request-json')
    assert resp.status == 400


@pytest.mark.asyncio
async def test_broken_json_request():
    resp = await http.post('/request-json', b'bad json')
    assert resp.status == 400


@pytest.mark.asyncio
async def test_correct_json_request():
    resp = await http.post('/request-json', {'foo': 1})
    assert resp.status == 200
    assert resp.json == {'foo': 1}


@pytest.mark.asyncio
async def test_guest():
    resp = await http.get('/request-user')
    assert resp.status == 200
    assert resp.json == {'user': None}


@pytest.mark.asyncio
async def test_user(user):
    resp = await http.get('/request-user', user=user)
    assert resp.status == 200
    assert resp.json == {'user': 'user'}


@pytest.mark.asyncio
async def test_login_required_guest():
    resp = await http.get('/require-login')
    assert resp.status == 403


@pytest.mark.asyncio
async def test_login_required_user(user):
    resp = await http.get('/require-login', user=user)
    assert resp.status == 200
    assert resp.json == {'user': 'user'}


@pytest.mark.asyncio
async def test_staff_required_guest():
    resp = await http.get('/require-staff')
    assert resp.status == 403


@pytest.mark.asyncio
async def test_staff_required_user(user):
    resp = await http.get('/require-staff', user=user)
    assert resp.status == 403


@pytest.mark.asyncio
async def test_staff_required_staff(staff):
    resp = await http.get('/require-staff', user=staff)
    assert resp.status == 200
    assert resp.json == {'user': 'staff'}
