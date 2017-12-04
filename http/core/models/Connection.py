import abc
import psycopg2

from orator import DatabaseManager, Model


class Connection(metaclass=abc.ABCMeta):
    __db = None
    __Model = None

    @staticmethod
    def init(db_config, alternative=False):
        if alternative is False:
            if Connection.__db is None:
                Connection.__db = DatabaseManager(db_config)
            if Connection.__Model is None:
                Model.set_connection_resolver(Connection.__db)
                Connection.__Model = Model
        else:
            conn = psycopg2.connect("host='{0}' dbname='{1}' user='{2}' password='{3}'".format(db_config['host'], db_config['database'], db_config['user'], db_config['password']))
            Connection.__db = conn.cursor()

    @staticmethod
    def close_connection():
        Connection.__db = None

    @staticmethod
    def get_db():
        return Connection.__db

    @staticmethod
    def get_model():
        return Connection.__Model
