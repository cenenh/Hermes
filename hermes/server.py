import asyncio
import os
import logging
from aiohttp import log, web, request
from hermes.web.ping import ping_handler


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
