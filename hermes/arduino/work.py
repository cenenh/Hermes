import asyncio
import logging
import json
from aiohttp import web, request
from hermes.util.time import getCurrentTime
from hermes.util.time import getToday
from hermes.util.time import getTimeDiff
from hermes.mysql import MySQL


@asyncio.coroutine
def go_work_handler(request):
    response = {'code': 200, 'message': 'ok'}
    data = yield from request.post()
    mysql = MySQL()
    yield from mysql.connect()
    args = (data['card_id'], getToday(), getCurrentTime())
    query = """INSERT INTO works(card_id, date, go_work_time)
               VALUES('%s', '%s', '%s')""" % args
    try:
        yield from mysql.execute_query(query)
    except Exception as e:
        logging.error(e)
        response = {'code': 400, 'message': 'fail'}
    finally:
        yield from mysql.close()

    logging.info('go work handler Response = {}\n'.format(response))

    headers = {'content-type': 'application/json'}
    return web.Response(headers=headers,
                        text=json.dumps(response))


@asyncio.coroutine
def off_work_handler(request):
    today = getToday()
    response = {'code': 200, 'message': 'ok'}
    data = yield from request.post()
    mysql = MySQL()
    yield from mysql.connect()
    query = """SELECT go_work_time FROM works
               WHERE card_id = '%s' and date = '%s'""" % (data['card_id'],
                                                          today)
    try:
        rows = yield from mysql.execute_query(query)
    except Exception as e:
        logging.error(e)
        response = {'code': 400, 'message': 'fail'}
    else:
        now = getCurrentTime()
        working_time = getTimeDiff(start_time=rows[0]['go_work_time'],
                                   end_time=now)
        args = (now, working_time, data['card_id'], today)
        query = """UPDATE works SET off_work_time = '%s', working_time = '%s'
                   where card_id = '%s' and date = '%s'""" % args
        yield from mysql.execute_query(query)
    finally:
        yield from mysql.close()

    logging.info('off work handler Response = {}\n'.format(response))

    headers = {'content-type': 'application/json'}
    return web.Response(headers=headers,
                        text=json.dumps(response))
