from aiohttp import web, Response, errors
from hermes.mysql import MySQL
import asyncio
import logging
import json
from hermes.util.file import open_file, write_file, close_file, save_image


SERVER_URL = 'http://52.78.10.38:8000/images/employees/'


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

    args = (data['card_id'],
            data['employee_name'],
            data['enterprise'],
            data['duty'],
            data['workspace'],
            data['phone_number'],
            data['registration_number'],
            data['email'], SERVER_URL+file_name)

    mysql = MySQL()
    yield from mysql.connect()
    query = """INSERT INTO employee (card_id, employee_name, enterprise,
               duty, workspace, phone_number, registration_number,
               email, photo_url) VALUES('%s', '%s', '%s', '%s', '%s',
               '%s', '%s', '%s', '%s')""" % args
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
