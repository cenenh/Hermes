# coding=utf-8
import asyncio
import logging
import json
from aiohttp import web, Response, errors
from hermes.mysql import MySQL
from hermes.util.time import getToday
from hermes.util.file import open_file, write_file, close_file, save_image
from hermes.constant import DUTY, SERVER_URL


@asyncio.coroutine
def add_employee_handler(request):
    data = yield from request.post()
    file_name = '.'.join([data['card_id'], 'jpg'])
    save_result = yield from save_image(file_name, data['photo'].file.read())

    if not save_result:
        response = {
            'code': 400,
            'message': 'fail'
        }
        headers = {'content-type': 'application/json'}
        return web.Response(headers=headers,
                            text=json.dumps(response))
    try:
        employee_duty = DUTY[data['duty']]
    except KeyError as e:
        logging.error(e)
        employee_duty = '일용근무자'

    args = (data['card_id'],
            data['employee_name'],
            data['enterprise'],
            data['duty'],
            data['workspace'],
            data['phone_number'],
            data['registration_number'],
            data['email'],
            SERVER_URL+file_name,
            DUTY[employee_duty]
            )

    mysql = MySQL()
    yield from mysql.connect()
    query = """INSERT INTO employee (card_id, employee_name, enterprise,
               duty, workspace, phone_number, registration_number,
               email, photo_url, unit_price)
               VALUES('%s', '%s', '%s', '%s', '%s',
               '%s', '%s', '%s', '%s', %d)""" % args

    try:
        yield from mysql.execute_query(query)
    except Exception as e:
        logging.error(e)
    else:
        response = {'code': 200, 'message': 'ok'}
    finally:
        yield from mysql.close()

    logging.info('add employee handler Response = {}'.format(response))

    headers = {'content-type': 'application/json'}
    return web.Response(headers=headers,
                        text=json.dumps(response))


@asyncio.coroutine
def search_employee_handler(request):
    req = request.GET
    employee_name = req.get('name', None)
    if employee_name is None:
        error = 'Error!, employee_name = {}'
        logging.error(error.format(employee_name))
        raise errors.HttpBadRequest('ERROR')
    mysql = MySQL()
    yield from mysql.connect()
    query = """SELECT * FROM employee
               WHERE employee_name = '%s'""" % employee_name
    rows = yield from mysql.execute_query(query)
    yield from mysql.close()
    response = {
        'size': len(rows),
        'employees': []
    }
    for row in rows:
        response['employees'].append({
            'card_id': row['card_id'],
            'employee_name': row['employee_name'],
            'phone_number': row['phone_number'],
            'email': row['email'],
            'duty': row['duty'],
            'workspace': row['workspace'],
            'photo_url': row['photo_url'],
            'registration_number': row['registration_number'],
            'unit_price': row['unit_price'],
            'pay': row['unit_price'] * 20,
        })
    logging.info('get employee handler Response = {}\n'.format(response))
    headers = {'content-type': 'application/json'}
    return web.Response(headers=headers,
                        text=json.dumps(response))


@asyncio.coroutine
def get_employee_by_date_handler(request):
    data = request.GET
    card_id = data.get('card_id', None)
    date = data.get('date', None)
    if not date:
        date = getToday()
    query = """SELECT * FROM employee natural join works
               where date ='%s'""" % date
    if card_id:
        query = """SELECT * FROM employee natural join works
                where card_id = '%s' and date ='%s'""" % (card_id, date)

    mysql = MySQL()
    yield from mysql.connect()
    rows = yield from mysql.execute_query(query)
    yield from mysql.close()
    response = {}
    response['size'] = len(rows)
    response['employees'] = []
    for row in rows:
        response['employees'].append({
            'date': date,
            'card_id': row['card_id'],
            'employee_name': row['employee_name'],
            'phone_number': row['phone_number'],
            'email': row['email'],
            'duty': row['duty'],
            'workspace': row['workspace'],
            'photo_url': row['photo_url'],
            'go_work_time': row['go_work_time'],
            'off_work_time': row['off_work_time'],
            'registration_number': row['registration_number'],
            'unit_price': row['unit_price'],
            'pay': row['unit_price'] * 20,
        })

    log = 'get_employee_by_date_handler Response = {}\n'
    logging.info(log.format(response))
    headers = {'content-type': 'application/json'}
    return web.Response(headers=headers,
                        text=json.dumps(response))


@asyncio.coroutine
def get_employee_handler(request):
    mysql = MySQL()
    yield from mysql.connect()
    rows = yield from mysql.execute_query("""SELECT * from employee""")
    yield from mysql.close()
    response = {}
    response['size'] = len(rows)
    response['employees'] = []
    for row in rows:
        response['employees'].append({
            'date': getToday(),
            'card_id': row['card_id'],
            'employee_name': row['employee_name'],
            'enterprise': row['enterprise'],
            'duty': row['duty'],
            'workspace': row['workspace'],
            'phone_number': row['phone_number'],
            'email': row['email'],
            'photo_url': row['photo_url'],
            'registration_number': row['registration_number'],
            'unit_price': row['unit_price'],
            'pay': row['unit_price'] * 20,
        })

    logging.info('get employee handler Response = {}\n'.format(response))
    headers = {'content-type': 'application/json'}
    return web.Response(headers=headers,
                        text=json.dumps(response))
