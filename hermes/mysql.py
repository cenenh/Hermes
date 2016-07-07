import asyncio
import aiomysql


class MySQL():

    def __init__(self, loop):
        self.host = '127.0.0.1'
        self.port = 3306
        self.user = 'root'
        self.password = '1q2w3e4r'
        self.db = 'hermes'
        self.loop = loop
        self.connection = None
        self.cursor = None

    @asyncio.coroutine
    def connect(self):
        self.connection = yield from aiomysql.connect(host=self.host,
                                                      port=self.port,
                                                      user=self.user,
                                                      password=self.password,
                                                      db=self.db,
                                                      loop=self.loop)
        self.cursor = yield from self.connection.cursor(aiomysql.DictCursor)
        return self.cursor

    @asyncio.coroutine
    def execute_query(self, query):
        yield from self.cursor.execute(query)
        results = yield from self.cursor.fetchall()
        return results

    @asyncio.coroutine
    def close(self):
        yield from self.cursor.close()
        self.connection.close()
