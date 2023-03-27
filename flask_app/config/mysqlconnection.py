import pymysql.cursors

class mySQLConnection:
    def __init__(self, db):
        self.connection = pymysql.connect(host = 'localhost',
                                         user = 'root',
                                         password = 'root',
                                         db = db,
                                         charset = 'utf8',
                                         cursorclass = pymysql.cursors.DictCursor,
                                         autocommit = True)
        
        
    

    def query_db(self, query, data=None):
        with self.connection.cursor() as cursor:
            try:
                query = cursor.mogrify(query, data)
                cursor.execute(query, data)
                if query.lower().find("insert") >= 0:
                    self.connection.commit()
                    return cursor.lastrowid
                elif query.lower().find('select') >= 0:
                    result = cursor.fetchall()
                    return result
                elif query.lower().find('show') >= 0:
                    result = cursor.fetchall()
                    return result
                elif query.lower().find('describe') >= 0:
                    result = cursor.fetchall()
                    return result
                else:
                    self.connection.commit()
            except Exception as e:
                print("something went wrong", e)
                exit(1)

def ConnectToMySQL(db):
    return mySQLConnection(db)