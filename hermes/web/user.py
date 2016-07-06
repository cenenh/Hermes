from aiohttp import web, Response
from hermes.mysql import mysql
import asyncio
import logging


@asyncio.coroutine
def get_user_handler(request):
    loop = asyncio.get_event_loop()
    user_name = request.match_info.get('name', 'admin')
    db = mysql(loop)
    yield from db.connect()
    results = yield from db.execute_query('select * from test')
    yield from db.close()
    logging.info(results)
    return web.Response(text='hi')
