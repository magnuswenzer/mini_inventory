import sqlite3

import exceptions


class Database:

    def __init__(self):
        self.db_file_name = 'inventory.db'
        self._create()
        self.unit_columns = []
        self.item_columns = []
        self.category_columns = []

    def _execute(self, sql_command, variables=None, commit=False, fetchall=False):
        """
        Execute the given sql command.
        """
        conn = None
        result = True

        try:
            conn = sqlite3.connect(self.db_file_name)
            conn.execute("PRAGMA foreign_keys = 1")
            c = conn.cursor()

            if variables:
                # print(sql_command)
                # print(variables)
                c.execute(sql_command, variables)
            else:
                c.execute(sql_command)

            if fetchall:
                result = c.fetchall()

            if commit or fetchall or variables:
                conn.commit()

        except sqlite3.IntegrityError as e:
            if 'UNIQUE constraint failed' in str(e):
                raise exceptions.AlreadyInDatabase
            raise

        except sqlite3.Error as error:
            print("Error while execute sqlite query", error)
            raise
        finally:
            if conn:
                conn.close()
                # print("sqlite connection is closed")

        return result

    def add_unit(self, name):
        sql_insert = f"""
                      INSERT INTO Unit (unit_name) 
                      VALUES (?)
                      """
        values = [name.lower()]
        self._execute(sql_insert, variables=values)

    def add_category(self, name):
        sql_insert = f"""
                      INSERT INTO Category (category_name) 
                      VALUES (?)
                      """
        values = [name.lower()]
        self._execute(sql_insert, variables=values)
        
    def add_item(self, **kwargs):
        columns = ['item_name', 'description', 'common', 'quantity', 'amount', 'barcode_nr', 'unit_id', 'category_id']
        sql_insert = f"""
                      INSERT INTO Item (item_name, description, common, quantity, amount, barcode_nr, unit_id, category_id) 
                      VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                      """

        # Check unit_id
        unit_name = kwargs.get('unit', kwargs.get('unit_name', None))
        if not unit_name:
            raise exceptions.MissingUnit
        kwargs['unit_id'] = self._get_unit_id(unit_name)
        category_name = kwargs.get('category', kwargs.get('category_name', None))
        kwargs['category_id'] = self._get_category_id(category_name)
        values = []
        for col in columns:
            value = kwargs.get(col, None)
            if type(value) == str:
                value = value.strip().lower()
                if value == '':
                    value = None
            values.append(value)
        # print(sql_insert)
        # print(values)
        self._execute(sql_insert, variables=values)

    def get_unit_list(self):
        result = self._execute(f"""
                        SELECT unit_name FROM Unit""", fetchall=True)
        if not result:
            return []
        return [item[0] for item in result]

    def get_category_list(self):
        result = self._execute(f"""
                        SELECT category_name FROM Category""", fetchall=True)
        if not result:
            return []
        return [item[0] for item in result]

    def get_item_list(self, unit):
        result = self._execute(f"""
                        SELECT Item.item_name
                        FROM Item
                        INNER JOIN Unit on Item.unit_id = Unit.unit_id
                        WHERE Unit.unit_name = '{unit}'""", fetchall=True)
        if not result:
            return []
        return [item[0] for item in result]

    def get_item_data(self, unit_name=None, category_name=None):
        self._save_columns_in_tables()

        where = [] 
        if unit_name: 
            where.append(f"""Unit.unit_name = '{unit_name}'""")
        if category_name: 
            where.append(f"""Category.category_name = '{category_name}'""")

        query = """
                SELECT *
                FROM Item
                INNER JOIN Unit on Item.unit_id = Unit.unit_id
                LEFT JOIN Category on Item.category_id = Category.category_id
                """
        if where: 
            query = query + ' WHERE ' + ' AND '.join(where)

        # print('QUERY')
        # print(query)

        result = self._execute(query, fetchall=True)

        # result = self._execute(f"""
        #                 SELECT *
        #                 FROM Item
        #                 INNER JOIN Unit on Item.unit_id = Unit.unit_id
        #                 LEFT JOIN Category on Item.category_id = Category.category_id
        #                 WHERE Unit.unit_name = '{unit}'""", fetchall=True)
        lst = []
        columns = self.item_columns + self.unit_columns + self.category_columns
        for item in result:
            lst.append(dict(zip(columns, item)))
            # lst.append(dict(zip(self.item_columns, item)))
        return lst

    def update_item(self, name, **kwargs):
        values = []
        set_list = []
        for key, value in kwargs.items():
            if value is False:
                value = None
            if type(value) == str:
                value = value.strip().lower()
                if value == '':
                    value = None
            if key in ['unit', 'unit_name']:
                value = self._get_unit_id(value)
                key = 'unit_id'
            elif key in ['category', 'category_name']:
                value = self._get_category_id(value)
                key = 'category_id'
                print('UPDATING CATEGORY IN DB:', key, value)
            values.append(value)
            set_list.append(f"""{key} = ?""")
        set_str = f"""SET {', '.join(set_list)}"""
        update_sql = f""" UPDATE Item {set_str} WHERE item_name='{name.lower()}'"""
        self._execute(update_sql, variables=values)

    def delete_unit(self, name):
        sql_delete = f"""
                      DELETE FROM Unit WHERE unit_name='{name.lower()}'
                      """
        return self._execute(sql_delete, commit=True)

    def delete_category(self, name):
        sql_delete = f"""
                      DELETE FROM Category WHERE category_name='{name.lower()}'
                      """
        return self._execute(sql_delete, commit=True)

    def delete_item(self, name):
        sql_delete = f"""
                      DELETE FROM Item WHERE item_name='{name.lower()}'
                      """
        return self._execute(sql_delete, commit=True)

    def _get_unit_id(self, name):
        result = self._execute(f"""
                        SELECT unit_id FROM Unit WHERE unit_name='{name}'""", fetchall=True)
        if not result:
            return None
        return result[0][0]

    def _get_category_id(self, name):
        result = self._execute(f"""
                        SELECT category_id FROM Category WHERE category_name='{name}'""", fetchall=True)
        if not result:
            return None
        return result[0][0]

    def _create(self):
        for query in self._get_create_table_queries():
            self._execute(query)

    def _get_create_table_queries(self):
        qlist = []

        query = '''CREATE TABLE IF NOT EXISTS Unit (
                                                unit_id INTEGER PRIMARY KEY,
                                                unit_name TEXT NOT NULL UNIQUE);'''
        qlist.append(query)

        query = '''CREATE TABLE IF NOT EXISTS Item (
                                                item_id INTEGER PRIMARY KEY,
                                                item_name TEXT NOT NULL UNIQUE, 
                                                description TEXT, 
                                                common INTEGER, 
                                                quantity INTEGER, 
                                                amount INTEGER, 
                                                barcode_nr INTEGER, 
                                                unit_id INTEGER NOT NULL,
                                                category_id INTEGER,
                                                FOREIGN KEY (unit_id) REFERENCES Unit (unit_id), 
                                                FOREIGN KEY (category_id) REFERENCES Category (category_id));'''

        qlist.append(query)

        query = '''CREATE TABLE IF NOT EXISTS Category (
                                                category_id INTEGER PRIMARY KEY,
                                                category_name TEXT NOT NULL UNIQUE);'''

        qlist.append(query)

        return qlist

    def _save_columns_in_tables(self): 
        if not self.unit_columns:
            self.unit_columns = self._get_columns_in_table('Unit')
        if not self.item_columns:
            self.item_columns = self._get_columns_in_table('Item')
        if not self.category_columns:
            self.category_columns = self._get_columns_in_table('Category')

    def _get_columns_in_table(self, table):
        conn = None
        result = False
        try:
            conn = sqlite3.connect(self.db_file_name)
            cursor = conn.execute(f"""SELECT * FROM {table}""")
            result = [des[0] for des in cursor.description]
        except sqlite3.Error as e:
            raise
        finally:
            if conn:
                conn.close()
        return result



if __name__ == '__main__':
    import os
    db = Database()
    if os.path.exists(db.db_file_name):
        os.remove(db.db_file_name)
        db = Database()
    db.add_unit('frys')
    db.add_unit('skap1')
    db.add_unit('skap2')
    db.add_unit('städskrubb')
    db.add_category('pasta')
    db.add_item(item_name='majs', unit='frys')
    db.add_item(item_name='fisk', unit='frys')
    db.add_item(item_name='spagetti', unit='skap1', category='pasta')
    db.add_item(item_name='makaroner', unit='skap1', category='pasta', amount=850, quantity=2)
    db.add_item(item_name='tonfisk', unit='skap1')
    db.add_item(item_name='salt', unit='skap1')
    db.add_item(item_name='rapsolja', unit='skap2')
    db.add_item(item_name='olivolja', unit='skap2')
    db.add_item(item_name='vitlok', unit='skap2')

    db.update_item('fisk', description='tomatfisk')

    print(db.get_unit_list())
