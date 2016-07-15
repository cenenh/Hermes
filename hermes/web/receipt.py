# coding=utf-8
import asyncio
import logging
import json
from hermes.mysql import MySQL
from aiohttp import web, Response, errors
from hermes.constant import HTTP_HEADERS


@asyncio.coroutine
def get_receipt_handler(request):
    req = request.GET
    mysql = MySQL()
    yield from mysql.connect()
    query = """SELECT card_id, employee_name, unit_price, date,
               working_time FROM employee natural join works
               where card_id = '%s'""" % req['card_id']
    rows = yield from mysql.execute_query(query)
    yield from mysql.close()

    response = {
        'pay': 0,
        'card_id': req['card_id'],
        'working_data': []
    }
    for row in rows:
        response['pay'] += row['unit_price']
        response['working_data'].append({
            'date': row['date'],
            'unit_price': row['unit_price'],
        })

    return web.Response(headers=HTTP_HEADERS,
                        text=json.dumps(response))
