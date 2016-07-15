import asyncio
import os
import logging
from aiohttp import web, request
from hermes.web.ping import ping_handler
from hermes.web.user import get_user_handler
from hermes.web.user import add_user_handler
from hermes.web.login import login_handler
from hermes.web.employee import add_employee_handler
from hermes.web.employee import get_employee_handler
from hermes.web.employee import get_employee_by_date_handler
from hermes.web.employee import search_employee_handler
from hermes.arduino.work import working_handler
from hermes.web.getHermetStatus import get_hermet_status_handler
from hermes.web.breakTime import set_break_time_handler
from hermes.web.today import get_on_employee_handler
from hermes.web.today import get_off_employee_handler


@asyncio.coroutine
def hermes_handler(request):
    return web.Response(text='Welcome to HERMES!')


def run():
    logging.debug('run server!')
    loop = asyncio.get_event_loop()
    app = web.Application(loop=loop)
    # add_route
    app.router.add_route('GET', '/', hermes_handler)
    app.router.add_route('GET', '/ping', ping_handler)
    app.router.add_route('GET', '/api/web/test/user', get_user_handler)
    app.router.add_route('POST', '/api/web/test/user', add_user_handler)
    app.router.add_route('POST', '/api/web/login', login_handler)
    app.router.add_route('POST', '/api/web/employee', add_employee_handler)
    app.router.add_route('GET', '/api/web/employeeAll', get_employee_handler)
    app.router.add_route('GET', '/api/web/employee',
                         get_employee_by_date_handler)
    app.router.add_route('GET', '/api/web/hermet/status',
                         get_hermet_status_handler)
    app.router.add_route('POST', '/api/web/setBreakTime',
                         set_break_time_handler)
    app.router.add_route('GET', '/api/web/employee', get_employee_handler)
    app.router.add_route('GET', '/api/web/employee/search',
                         search_employee_handler)
    app.router.add_route('GET', '/api/web/onEmployee',
                         get_on_employee_handler)
    app.router.add_route('GET', '/api/web/offEmployee',
                         get_off_employee_handler)

    app.router.add_route('POST', '/api/arduino/working', working_handler)

    server_handler = app.make_handler(access_log=logging.getLogger())
    server = loop.run_until_complete(loop.create_server(server_handler,
                                                        '0.0.0.0', 8080))

    # Serve requests until CTRL+c is pressed
    logging.debug('Serving on {}'.format(server.sockets[0].getsockname()))

    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass
    finally:
        # Close the server
        loop.run_until_complete(server_handler.finish_connections(1.0))
        server.close()
        loop.run_until_complete(server.wait_closed())
        loop.run_until_complete(app.finish())

    loop.close()
