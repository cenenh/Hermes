import asyncio
import logging


ABSOLUTE_PATH = '/home/ubuntu/nginx/Hermes/images/employee/'


@asyncio.coroutine
def save_image(file_name, file_data):
    fd = yield from open_file(''.join([ABSOLUTE_PATH, file_name]))
    result = yield from write_file(fd, file_data)
    yield from close_file(fd)
    return result


@asyncio.coroutine
def open_file(name):
    return open(name, 'wb')


@asyncio.coroutine
def close_file(file):
    file.close()


@asyncio.coroutine
def write_file(fd, data):
    try:
        fd.write(data)
    except Exception as e:
        logging.error(e)
    else:
        return True
    return False
