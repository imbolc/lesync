from asyncio import sleep
from django.http import HttpResponse
from lesync import login_required, staff_member_required

from lesync.trafaret import validate_query, validate_json


async def dict_response(request):
    return {'hello': 'world'}


async def tuple2_response(request):
    return {'bad': 'request'}, 400


async def tuple3_response(request):
    return {'bad': 'request'}, 400, {'Cache-Control': 'no-cache'}


async def django_response(request):
    return HttpResponse('foo')


async def stream_response(request):
    async def stream():
        yield '1,foo\n'
        await sleep(.01)
        yield '2,bar'
    return stream(), 200, {'Content-Type': 'text/csv'}


async def request_json(request):
    return request.json


async def request_user(request):
    user = await request.load_user()
    user = user.username if user.is_authenticated else None
    return {'user': user}


@login_required
async def require_login(request):
    return {'user': request.user.username}


@staff_member_required
async def require_staff(request):
    return {'user': request.user.username}


@validate_query({'id': int})
async def query_validation(request):
    return dict(request.GET)


@validate_json({'id': int})
async def json_validation(request):
    return request.json
