import json

import pymysql
import pymysql.cursors

class MySqlClient:
    def __init__(self, config):
        cfg = json.load(open(config))
        self.connection = pymysql.connect(
                host=cfg['host'],
                user=cfg['user'],
                password=cfg['password'],
                database=cfg['database'],
                charset='utf8mb4',
                cursorclass=pymysql.cursors.DictCursor
        )

    def update_funding(self, exchange, symbol, time, rate, span):
        with self.connection:
            with self.connection.cursor() as cursor:
                sql = "REPLACE INTO funding (exchange, symbol, time, rate, span) VALUES (%s, %s, %s, %s, %s)"
                cursor.execute(sql, (exchange, symbol, time, rate, span))
            self.connection.commit()

    def get_funding(self, exchange, symbol, start_time, end_time):
        with self.connection:
            with self.connection.cursor() as cursor:
                cursor.execute("SELECT * FROM funding
                                WHERE exchange = %s
                                AND symbol = %s
                                AND start_time >= %s
                                AND end_time < %s",
                               (exchange, symbol, start_time, end_time))
                return cursor.fetchall()

