import asyncio
import logging
import json
from aiohttp import web, Response, errors
from hermes.mysql import MySQL
from hermes.constant import HTTP_HEADERS


@asyncio.coroutine
def login_handler(request):
    data = yield from request.post()
    mysql = MySQL()
    yield from mysql.connect()
    query = """SELECT * FROM administrator
            WHERE id = '%s' and
            password = '%s'""" % (data['id'], data['password'])
    results = yield from mysql.execute_query(query)
    yield from mysql.close()
    response = {
        'code': 200,
        'message': 'login success'
    }
    if not results:
        response = {
            'code': 400,
            'message': 'Password Incorrect or No Such User'
        }

    logging.info('add login handler Response = {}'.format(response))
    return web.Response(headers=HTTP_HEADERS,
                        text=json.dumps(response))
