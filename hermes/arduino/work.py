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
        args = (data['card_id'], getToday(), getCurrentTime(), 'NULL', 'NULL')
        query = """INSERT INTO works(card_id, date, go_work_time,
                   off_work_time, working_time)
                   VALUES('%s', '%s', '%s', '%s', '%s')""" % args

    elif hermet_status == 2 and result:
        # 오늘에 대한 출근 정보가 있고, hermetStatus가 2이면 일단 퇴근으로 저장.
        now = getCurrentTime()
        working_time = getTimeDiff(start_time=result[0]['go_work_time'],
                                   end_time=now)
        args = (now, working_time, data['card_id'], getToday())
        query = """UPDATE works SET off_work_time = '%s', working_time = '%s'
                   where card_id = '%s' and date = '%s'""" % args

    elif hermet_status == 1 and result:
        # 오늘에 대한 출근 정보가 있는데 hermetStatus가 1이면 퇴근 정보 삭제.
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

    # 부저는 1이면 안울리고, 0이면 울린다.
    # 쉬는 시간이면 1, 쉬는 시간이 아니면 0
    response = results[0]['is_break_time']
    message = "is_break_time? : {}, Working Handler Response = {}"
    logging.debug(message.format(results[0]['is_break_time'], response))
    return web.Response(text='VAL'+str(response))
