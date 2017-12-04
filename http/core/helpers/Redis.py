class Redis:

    __connection = None

    @staticmethod
    def set_connection(connection):
        Redis.__connection = connection

    @staticmethod
    def connection():
        return Redis.__connection

    @staticmethod
    async def get(key):
        return await Redis.connection().execute('get', key)

    @staticmethod
    async def set(key, value):
        result = await Redis.connection().execute('set', key, value)
        return result

    @staticmethod
    async def setbit(key, id, value):
        if value not in [1, 0]:
            raise Exception('Invalid value, please use only 1 or 0.')
        return await Redis.connection().execute('setbit', key, id, value)

    @staticmethod
    async def getbit(keys_group, key):
        result = await Redis.connection().execute('getbit', keys_group, key)
        return result
