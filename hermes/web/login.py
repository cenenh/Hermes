from aiohttp import web, Response, errors
from hermes.mysql import MySQL
import asyncio
import logging
import json


@asyncio.coroutine
def login_handler(request):
    loop = asyncio.get_event_loop()
    data = yield from request.json()
    db = MySQL(loop)
    yield from db.connect()
    query = """SELECT * FROM admin_user
            WHERE id = '%s' and
            password = '%s'""" % (data['id'], data['password'])
    results = yield from db.execute_query(query)
    yield from db.close()
    response = {
        'code': 200,
        'message': 'login success'
    }
    if not results:
        response = {
            'code': 400,
            'message': 'Password Incorrect or No Such User'
        }
    headers = {'content-type': 'application/json'}
    return web.Response(headers=headers,
                        text=json.dumps(response))
