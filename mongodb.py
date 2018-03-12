from pymongo import MongoClient
import json


class MongoDB:

    def __init__(self, host, port_id):
        self.conn = MongoClient(host, port_id)
        self.db = self.conn.nba

    def close_conn(self):
        self.conn.close()

    def write_per_game_data(self, name, table_head, table_content):
        for row in table_content:
            document = '{\"name\":\"' + name + '\",'
            for index in range(0,len(table_head)):
                document += ('\"' + table_head[index] + '\":\"' + row[index] + '\"')
                if index < len(table_head) - 1:
                    document += ','
            document += '}'
            value = json.loads(document)
            self.db.per_game.insert(value)
        print(name + '\'s Per Game data added to DB (' + str(len(table_head)) + 'rows)')