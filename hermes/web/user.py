from aiohttp import web, Response
from hermes.mysql import MySQL
import asyncio
import logging
import json


@asyncio.coroutine
def add_user_handler(request):
    data = yield from request.json()
    try:
        name = data['name']
    except KeyError as e:
        logging.error(e)
        response = {'code': 400, 'message': "'name' is omitted"}
    else:
        mysql = MySQL()
        yield from mysql.connect()
        query = """INSERT INTO test_user(name) VALUES('%s')""" % name
        yield from mysql.execute_query(query)
        yield from mysql.close()
        response = {'code': 200, 'message': 'ok'}
    finally:
        return web.Response(headers={'content-type': 'application/json'},
                            text=json.dumps(response))


@asyncio.coroutine
def get_user_handler(request):
    mysql = MySQL()
    yield from mysql.connect()
    results = yield from mysql.execute_query('select * from test_user')
    yield from mysql.close()
    return web.Response(headers={'content-type': 'application/json'},
                        text=json.dumps(results))
