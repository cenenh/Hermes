# coding=utf-8
import asyncio
import logging
import json
from aiohttp import web, Response, errors
from hermes.mysql import MySQL
from hermes.util.time import getToday, getCurrentTime
from hermes.constant import HTTP_HEADERS


@asyncio.coroutine
def set_break_time_handler(request):
    data = yield from request.json()
    mysql = MySQL()
    yield from mysql.connect()
    now = getCurrentTime()
    today = getToday()
    # 0이면 휴식시간 끝, 1이면 휴식시간 시작
    args = (data['is_break_time'], today, now)
    query = """UPDATE break_time SET is_break_time = '%d',
               set_date = '%s', set_time = '%s' where id ='hermes'""" % args
    yield from mysql.execute_query(query)
    yield from mysql.close()
    response = {
        'code': 200,
        'message': 'ok',
        'current_is_break_tiem': data['is_break_time'],
        'set_date': getToday(),
        'set_time': now,
    }
    message = 'setBreakTimeHandler Response = {}'
    logging.debug(message.format(response))
    return web.Response(headers=HTTP_HEADERS,
                        text=json.dumps(response))
