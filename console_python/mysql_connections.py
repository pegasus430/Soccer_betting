import mysql.connector
import mysql.connector.pooling


dbconfig = {
    "host": "localhost",
    "port": "3306",
    "user": "root",
    "password": "P@ssw0rd2021",
    "database": "soccer",
    "auth_plugin": 'mysql_native_password'
}


mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    passwd="P@ssw0rd2021",
    database="soccer"
)
mycursor = mydb.cursor()

class MySQLPool(object):
    def __init__(self, config=None):
        if config is None:
            config = dbconfig
        res = {}
        self._host = config["host"]
        self._port = config["port"]
        self._user = config["user"]
        self._password = config["password"]
        self._database = config["database"]
        self._auth_plugin = 'mysql_native_password'
        pool_name = "mypool"
        pool_size = 3
        auth_plugin = "mysql_native_password"

        res["host"] = self._host
        res["port"] = self._port
        res["user"] = self._user
        res["password"] = self._password
        res["database"] = self._database
        res['auth_plugin'] = 'mysql_native_password'
        self.dbconfig = res
        self.pool = self.create_pool(pool_name=pool_name, pool_size=pool_size)

    def create_pool(self, pool_name="mypool", pool_size=5):
        pool = mysql.connector.pooling.MySQLConnectionPool(
            pool_name=pool_name,
            pool_size=pool_size,
            pool_reset_session=True,
            **self.dbconfig)
        return pool

    def close(self, conn, cursor):
        """
        A method used to close connection of mysql.
        :param conn:
        :param cursor:
        :return:
        """
        cursor.close()
        conn.close()

    def execute(self, sql, args=None, commit=False):
        """
        Execute a sql, it could be with args and with out args. The usage is
        similar with execute() function in module pymysql.
        :param sql: sql clause
        :param args: args need by sql clause
        :param commit: whether to commit
        :return: if commit, return None, else, return result
        """
        # get connection form connection pool instead of create one.
        conn = self.pool.get_connection()
        cursor = conn.cursor()
        if args:
            cursor.execute(sql, args)
        else:
            cursor.execute(sql)
        if commit is True:
            conn.commit()
            self.close(conn, cursor)
            return "Success"
        else:
            res = cursor.fetchall()
            self.close(conn, cursor)
            return res

    def executemany(self, sql, args, commit=False):
        """
        Execute with many args. Similar with executemany() function in pymysql.
        args should be a sequence.
        :param sql: sql clause
        :param args: args
        :param commit: commit or not.
        :return: if commit, return None, else, return result
        """
        # get connection form connection pool instead of create one.
        conn = self.pool.get_connection()
        cursor = conn.cursor()
        cursor.executemany(sql, args)
        if commit is True:
            conn.commit()
            self.close(conn, cursor)
            return None
        else:
            res = cursor.fetchall()
            self.close(conn, cursor)
            return res
