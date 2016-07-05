from aiohttp import web, Response
import asyncio
import json


@asyncio.coroutine
def ping_handler(request):
    response = {
        'statusCode': 200,
        'data': 'pong'
    }
    headers = {'content-type': 'application/json'}
    return web.Response(headers=headers,
                        text=json.dumps(response))
