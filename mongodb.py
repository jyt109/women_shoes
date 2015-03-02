import pymongo


class MongoDB(object):
    def __init__(self, db_name, table_name):
        self.db_name = db_name
        self.table_name = table_name
        client = pymongo.MongoClient()
        self.db = client[self.db_name]
        self.table = self.db[self.table_name]
        self.table.remove()

    def get_table(self):
        return self.table

    def insertion(self, fields, tup_lst):
        for tup in tup_lst:
            if len(fields) != len(tup):
                raise Exception('Fields must have the same length as values')
            json = dict(zip(fields, tup))
            self.table.insert(json)
