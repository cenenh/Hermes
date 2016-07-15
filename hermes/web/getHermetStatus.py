import asyncio
import logging
import json
import time
from aiohttp import web, Response, errors
from hermes.mysql import MySQL
from hermes.constant import HTTP_HEADERS


@asyncio.coroutine
def get_hermet_status_handler(request):
    now = int(time.time() / 10) * 10
    mysql = MySQL()
    yield from mysql.connect()
    query = """SELECT card_id, status FROM hermet_status
               where timestamp = %d""" % now
    results = yield from mysql.execute_query(query)
    response = {'code': 200, 'message': 'ok'}
    response['data'] = results
    return web.Response(headers=HTTP_HEADERS,
                        text=json.dumps(response))
