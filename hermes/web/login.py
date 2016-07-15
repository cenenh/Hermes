from aiohttp import web, Response, errors
from hermes.mysql import MySQL
import asyncio
import logging
import json


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

    headers = {'content-type': 'application/json'}
    return web.Response(headers=headers,
                        text=json.dumps(response))
