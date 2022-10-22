"""
SQlite database CRUD operations
usage: db = Database('my_data.db')
The database will be created if necessary.
Derived from Traversy tkinter video: https://www.youtube.com/watch?v=ELkaEpN29PU
5-1-2020; modified 07-2020
Modified 08-08-2020: add Row factory and PARSE_DECLTYPES |  sqlite3.PARSE_COLNAMES
"""
import sqlite3

class Database:
    def __init__(self, db):
        """
        Return a Database object
        :param db: filename to SQLite3 db file or ':memory:' for an in memory database.
        """
        self.conn = sqlite3.connect(db, detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)
        self.conn.row_factory = sqlite3.Row
        self.cur = self.conn.cursor()
        
    def vacuum(self):
        """
        Vacuum the database to optimize performace and disk usage.
        """        
        self.cur.execute("VACUUM;")

    def backup_db(self, backup_db):
        """
        Backup a SQLite3 database to the specified location.
        Note: the backup database will be created, if necessary.
        :param backup_db: Full directory to a database file
        :return: None
        """

        def progress(status, remaining, total):
            """
             Prints progress during db backup. See Python docs.
             :param status: used by the process - see docs
             :param remaining:
             :param total:
             :return:
             """
            print(f'Copied {total - remaining} of {total} pages...')

        backup = sqlite3.connect(backup_db)
        with backup:
            self.conn.backup(backup, pages=0, progress=progress)

    def get_total_changes(self):
        """
        Returns the total number of database rows that have been modified, inserted, or deleted since the database
         connection was opened.
        :return: int
        """
        return self.conn.total_changes

    def run_script(self, script):
        """
        Run multiple SQL statements contained sequentially.
        :param script: a string of SQL commands. This can be the output of a file.read() method
        or a triple quoted string.
        :return: None
        """
        self.conn.executescript(script)
        self.conn.commit()

    def insert_many(self, query, values):
        """
        Insert iterable of values using executemany() method.
        :param query: SQL query string
        - single value example: "INSERT INTO integers VALUES (?);"
        :param values: an iterable of values to insert
        Note: Values should be tuples or lists.
        - [(x,) for x in gen_function()]
        - [(x,) for x in range(10)]
        - [[x] for x in range(10)]
        :return: None
        NOTE: On 11-5-2020 I added the return of self.cur.rowcount for Mailchimp subscriber project
        """
        self.cur.executemany(query, values)
        self.conn.commit()
        return self.cur.rowcount

    def insert(self, query, values):
        """
        Insert a record into a database table.
        You can interrogate the returned cursor object:
            cur.lastrowid > int (id of last row inserted)
            cur.rowcount > int (number of rows affected - see warnings)
        :param query: a SQL query as a string
        :param values: the values to insert.
        :return: cursor object (has properties lastrowid, rowcount, etc.)
        """
        try:
            cur = self.cur.execute(query, values)
            self.conn.commit()
        except TypeError as t:
            raise TypeError("Please check your values and try again.") from t
        except sqlite3.DatabaseError as e:            
            raise sqlite3.DatabaseError("Error inserting data!") from e
        return cur

    def delete(self, query, pid):
        self.cur.execute(query, (pid,))
        self.conn.commit()

    def delete_all(self, table_name):
        """
        Delete all records from specified table
        :param table_name: name of table
        :return: None
        """
        self.cur.execute(F"""DELETE FROM {table_name};""")
        self.conn.commit()

    def update(self, query, values):
        self.cur.execute(query, values)
        self.conn.commit()

    def fetch(self, query):
        """
        run .fetchall()
        :param query: an SQL SELECT query as a string
        :return: list
        """
        self.cur.execute(query)
        return self.cur.fetchall()

    def fetchone(self, query):
        self.cur.execute(query)
        return self.cur.fetchone()
        
    def query_with_data(self, query, values):
        """Returns a cursor object with fetchone, fetchall, etc."""
        return self.cur.execute(query, values)
        
        
    def create_table(self, query):
        """
        Create a table using query
        :query: query as string
        :return: None
        """
        self.cur.execute(query)
        self.conn.commit()

    def __del__(self):
        self.conn.close()

    def join(self, join_type, left_table, right_table, left_join_field, right_join_field, left_field_list,
             right_field_list):
        """
        Return results from a left join.
        :param join_type: LEFT JOIN (returns matched and unmatched columns) or INNER JOIN (returns matched only)
        :param left_table: 'left side' table for the join
        :param right_table: 'right side' table for the join
        :param left_join_field: matching field from left table
        :param right_join_field: matching field from right table
        :param left_field_list: a list of fields from the left table to return (accepts '*')
        :param right_field_list: a list of fields from the left table to return (accepts '*')
        :return: cur.fetchall() object
        """

        left_fields = [f'_left.{field}' for field in left_field_list]
        right_fields = [f'_right.{field}' for field in right_field_list]

        query = f"""SELECT {','.join(left_fields)}, {','.join(right_fields)} FROM {left_table} _left
        {join_type} {right_table} _right
        ON _left.{left_join_field} = _right.{right_join_field};"""

        self.cur.execute(query)
        return self.cur.fetchall()
