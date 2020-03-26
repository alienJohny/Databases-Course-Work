import sqlite3
from abc import ABC, abstractmethod


class StorageInterface(ABC):
    @abstractmethod
    def create(self):
        pass


    @abstractmethod
    def read(self):
        pass


    @abstractmethod
    def update(self, userid, vendor, size):
        pass


    @abstractmethod
    def delete(self, userid):
        pass


class SQLiteStorage(StorageInterface):
    def __init__(self):
        self.__connection__ = Connection().getInstance()

    

class Connection:
    def __init__(self):
        self.__instance__ = None
        self.config_name = "./db.conf"
        self.DB_PATH = self.readConfig()
    
    def readConfig(self):
        with open(self.config_name, "r") as database_config:
            config = database_config.readline()

        return config

    def getInstance(self):
        try:
            self.__instance__ = sqlite3.connect(self.DB_PATH)
            
            return self.__instance__
        except IOError:
            print('An error occurred trying to connect to database.')


with open("./db.conf", "r") as database_config:
    DB_PATH = database_config.readline()

def insert_into_cart(userid, vendor, size):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    sql_query = 'insert into cart (userid, vendor, size) values '
    sql_query += '(\'{}\',{},{});'.format(userid, vendor, size)

    print(sql_query)

    c.execute(sql_query)
    conn.commit()

    goods_amount = c.execute("select count(userid) from cart where userid = '{}';".format(userid))
    goods_amount = [i for i in goods_amount][0][0]

    conn.close()

    return goods_amount


def get_items_amount(userid):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    goods_amount = c.execute("select count(userid) from cart where userid = '{}';".format(userid))
    goods_amount = [i for i in goods_amount][0][0]

    conn.close()

    return goods_amount


def get_data(request):
    url_args = list(request.args.keys())
    if all(i in url_args for i in ['sort', 'gender', 'cats']):
        sort_by = request.args.get('sort')
        gender = request.args.get('gender')
        categories = request.args.getlist('cats')
    else:
        sort_by = 'Sort by'
        gender = 'forall'
        categories = 'None'

    data = make_sql_query(gender, sort_by, categories)

    return data


def make_sql_query(gender, sort_by, cats):

    # Create database for catalog of clothing
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    sql_query = 'select * from goods'
    if gender != 'forall':
        sql_query += ' where gender = \'{}\''.format(gender)

    if cats != 'None' and cats != ['None']:
        if gender == 'forall':
            sql_query += (' where (' + " or ".join(['category = \'{}\''.format(cat) for cat in cats]) + ')')
        else:
            sql_query += (' and (' + " or ".join(['category = \'{}\''.format(cat) for cat in cats]) + ')')

    sql_query += ' order by '
    if sort_by == 'By popularity' or sort_by == 'Sort by':
        sql_query += 'rating desc'
    if sort_by == 'Ascending prices':
        sql_query += 'price'
    if sort_by == 'Descending prices':
        sql_query += 'price desc'

    print(sql_query)
    data = [i for i in c.execute(sql_query)]

    conn.close()

    return data


def select_cart(userid):
    sql_query = """
    select *, count(*) as amount from (
        select g.description,
            g.category,
            g.gender,
            c.size,
            g.color,
            g.price * (1 - g.discount) as price,
            c.vendor
        from cart c
        join goods g
        on c.vendor = g.vendor
        where userid = '{0}'
    ) as items
    group by vendor, size
    having count(*) >= 1
    """.format(userid)

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    data = [i for i in c.execute(sql_query)]
    conn.close()

    return data
    
