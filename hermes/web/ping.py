from aiohttp import web, Response
import asyncio
import json
from hermes.constant import HTTP_HEADERS


@asyncio.coroutine
def ping_handler(request):
    response = {
        'code': 200,
        'data': 'pong'
    }
    return web.Response(headers=HTTP_HEADERS,
                        text=json.dumps(response))
