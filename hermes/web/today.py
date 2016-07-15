# coding=utf=8
import asyncio
import logging
import json
from aiohttp import web, Response, errors
from hermes.mysql import MySQL
from hermes.util.time import getToday


headers = {'content-type': 'application/json'}


response = {
    'code': 200,
    'message': 'ok',
    'count': 0
}


@asyncio.coroutine
def get_on_employee_handler(request):
    count = yield from get_employees_count()
    response['count'] = count
    message = 'on_employee_response = {}\n'.format(response)
    logging.info(message)
    return web.Response(headers=headers,
                        text=json.dumps(response))


@asyncio.coroutine
def get_off_employee_handler(request):
    count = yield from get_employees_count('off')
    response['count'] = count
    message = 'off_employee_response = {}\n'.format(response)
    logging.info(message)
    return web.Response(headers=headers,
                        text=json.dumps(response))


@asyncio.coroutine
def get_employees_count(status='on'):
    args = ('NULL', getToday())
    query = """SELECT * FROM employee natural join works
               WHERE off_work_time = '%s' and date = '%s'""" % args

    if status == 'off':
        query = """SELECT * FROM employee natural join works
                   WHERE off_work_time != '%s' and date = '%s'""" % args

    mysql = MySQL()
    yield from mysql.connect()
    rows = yield from mysql.execute_query(query)
    logging.info('get count of {}_employee request'.format(status))
    yield from mysql.close()
    return len(rows)
