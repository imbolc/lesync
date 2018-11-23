Lesync
======
Http helpers for `django-channels`

Hello world
-----------
```python
from lesync import login_required

@login_required
async def hello(request):
    return {'hello': request.user.username}
```

Install
-------

    pip install lesync

Add `ApiConsumer` into your `routing.py`:

```python
from django.urls import path
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.sessions import SessionMiddlewareStack
from lesync import ApiConsumer

application = ProtocolTypeRouter({
    # ... websockets or something
    'http': SessionMiddlewareStack(
        URLRouter([
            path('/async/<path:path>', ApiConsumer),
            # ... fallback to sync views
        ]),
    ),
})
```

That's it. Now you can add async views which will be served win `/async/` url
prefix.


Request
-------
Subclass of `channels.http.AsgiRequest` with:

- `json` attribute
- `async load_user()` method - which returns standard django user
- `user` attribute - it's available after calling `load_user()` of if you use
    `@login_required` or `@staff_member_required` decorators


Response
--------
In addition to `django.http.HttpResponse`
you can use sugary json responses and streaming:

```python
async def standard(request):
    return HttpResponse('hello, world')

async def json_data(request):
    return {'hello': 'world'}

async def with_status(request):
    return {'bad': 'request'}, 400

async def with_headers(request):
    return {}, 200, {'my': 'header'}

async def streaming(request):
    async def stream():
        for i in range(1, 1000):
            yield f'{i},{i**2}\n'
            await asyncio.sleep(.1)
    return stream(), 200, {'Content-Type': 'text/csv'}
```


Auth
----
Familiar `@login_required` and `@staff_member_required` decorators:

```python
from lesync import staff_member_required

@staff_member_required
async def hello(request):
    return {'admin': request.user.username}
```


Request validation
------------------
You can use `@validate_query` and `@validate_json` decorators
to validate requests data. They're using `trafaret` library to perform
validation, so make sure it's installed.

```python
from lesync.trafaret import validate_json

@validate_json({'ids': [int], 'hello?': str})
async def foo(request):
    return request.json
```


Tests
-----
```bash
    python -m venv .venv
    source .venv/bin/activate
    pip install -Ur requirements-dev.txt
    python -m pytest tests/
```
