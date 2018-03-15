from pymongo import MongoClient
import json


class MongoDB:

    def __init__(self, host, port_id):
        self.conn = MongoClient(host, port_id)
        self.db = self.conn.nba

    def close_conn(self):
        self.conn.close()

    def add_rows_to_table(self, table, head, content):
        target_table = self.db.get_collection(str(table))
        for row in content:
            document = "{"
            for index in range(0, len(head)):
                if '.' in head[index]:
                    head[index] = head[index].replace('.', '')
                # '.' can't be written to MongoDB
                document += ('\"' + head[index] + '\":\"' + row[index] + '\"')
                if index < len(head) - 1:
                    document += ','
            document += '}'
            json_doc = json.loads(document)
            target_table.insert(json_doc)
        # print(table + ' added to DB (' + str(len(content)) + ' rows)')