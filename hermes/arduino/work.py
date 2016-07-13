# coding=utf-8
import asyncio
import logging
import json
import time
from aiohttp import web, request
from hermes.util.time import getCurrentTime
from hermes.util.time import getToday
from hermes.util.time import getTimeDiff
from hermes.mysql import MySQL


@asyncio.coroutine
def working_handler(request):
    data = yield from request.json()
    card_id = data['card_id']
    hermet_status = int(data['hermet_status'])

    mysql = MySQL()
    yield from mysql.connect()

    args = (data['card_id'], getToday())
    query = """SELECT card_id, date, go_work_time, off_work_time from works
               WHERE card_id = '%s' and date = '%s'""" % args
    result = yield from mysql.execute_query(query)

    if hermet_status == 1 and not result:
        # 오늘에 대한 출근 정보가 없는데 hermetStatus가 1이면 출근
        args = (data['card_id'], getToday(), getCurrentTime())
        query = """INSERT INTO works(card_id, date, go_work_time)
                   VALUES('%s', '%s', '%s')""" % args

    elif hermet_status == 0 and result:
        # 오늘에 대한 출근 정보가 있는데 hermetStatus가 0이면 퇴근
        if result[0]['off_work_time'] == 'NULL':
            logging.debug('go off')
            now = getCurrentTime()
            today = getToday()
            working_time = getTimeDiff(start_time=result[0]['go_work_time'],
                                       end_time=now)
            args = (now, working_time, data['card_id'], today)
            query = """UPDATE works SET off_work_time = '%s',
                    working_time = '%s' where card_id = '%s'
                    and date = '%s'""" % args

    elif hermet_status == 1 and result:
        # 오늘에 대한 출근 정보가 있는데 hermetStatus가 0이면 퇴근 정보 삭제.
        args = ('NULL', 'NULL', data['card_id'], getToday())
        query = """UPDATE works SET off_work_time = '%s', working_time = '%s'
                   where card_id = '%s' and date = '%s'""" % args
    else:
        query = None

    if query:
        yield from mysql.execute_query(query)

    now = int(time.time() / 10) * 10
    args = (card_id, now, hermet_status)
    query = """INSERT INTO hermet_status(card_id, timestamp, status)
               VALUES('%s', %d, %i)""" % args
    ERROR = None
    try:
        yield from mysql.execute_query(query)
    except Exception as e:
        # duplicate timestamp일 확률이 높음.
        ERROR = e
        logging.error(e)
    finally:
        log = 'card_id = {}, timestamp = {}, status = {} is inserted'
        if ERROR:
            log = 'card_id = {}, timestamp = {}, status = {} skipped'
        logging.debug(log.format(card_id, now, hermet_status))

    query = """SELECT * FROM break_time WHERE id = 'hermes'"""
    results = yield from mysql.execute_query(query)
    yield from mysql.close()
    response = {
        'code': 200,
        'message': 'ok',
        'break_time': results[0]['is_break_time']
    }
    return web.Response(headers={'content-type': 'application/json'},
                        text=json.dumps(response))
