import mysql.connector
import glob
import json
import csv
from io import StringIO
import itertools
import hashlib
import os
import cryptography
from cryptography.fernet import Fernet
from math import pow

class database:

    def __init__(self, purge = False):

        # Grab information from the configuration file
        self.database       = 'db'
        self.host           = '127.0.0.1'
        self.user           = 'master'
        self.port           = 3306
        self.password       = 'master'
        self.tables         = ['users', 'transactions', 'test']

        
        # NEW IN HW 3-----------------------------------------------------------------
        self.encryption     =  {   'oneway': {'salt' : b'averysaltysailortookalongwalkoffashortbridge',
                                                 'n' : int(pow(2,5)),
                                                 'r' : 9,
                                                 'p' : 1
                                             },
                                'reversible': { 'key' : '7pK_fnSKIjZKuv_Gwc--sZEMKn2zc8VvD6zS96XcNHE='}
                                }
        #-----------------------------------------------------------------------------

    def query(self, query = "SELECT * FROM users", parameters = None):

        cnx = mysql.connector.connect(host     = self.host,
                                      user     = self.user,
                                      password = self.password,
                                      port     = self.port,
                                      database = self.database,
                                      charset  = 'latin1'
                                     )


        if parameters is not None:
            cur = cnx.cursor(dictionary=True)
            cur.execute(query, parameters)
        else:
            cur = cnx.cursor(dictionary=True)
            cur.execute(query)

        # Fetch one result
        row = cur.fetchall()
        cnx.commit()

        if "INSERT" in query:
            cur.execute("SELECT LAST_INSERT_ID()")
            row = cur.fetchall()
            cnx.commit()
        cur.close()
        cnx.close()
        return row

    def createTables(self, purge=False, data_path = 'flask_app/database/'):
        ''' FILL ME IN WITH CODE THAT CREATES YOUR DATABASE TABLES.'''

        #should be in order or creation - this matters if you are using forign keys.

        if purge:
            for table in self.tables[::-1]:
                # self.query(f"""DROP TABLE IF EXISTS {table}""")
                pass

        # Execute all SQL queries in the /database/create_tables directory.
        for table in self.tables:

            #Create each table using the .sql file in /database/create_tables directory.
            with open(data_path + f"create_tables/{table}.sql") as read_file:
                create_statement = read_file.read()
            self.query(create_statement)

            # Import the initial data
            try:
                params = []
                with open(data_path + f"initial_data/{table}.csv") as read_file:
                    scsv = read_file.read()
                for row in csv.reader(StringIO(scsv), delimiter=','):
                    params.append(row)

                # Insert the data
                cols = params[0]; params = params[1:]
                self.insertRows(table = table,  columns = cols, parameters = params)
            except:
                print('no initial data')



    def insertRows(self, table='table', columns=['x','y'], parameters=[['v11','v12'],['v21','v22']]):
        
        # Check if there are multiple rows present in the parameters
        has_multiple_rows = any(isinstance(el, list) for el in parameters)
        keys, values      = ','.join(columns), ','.join(['%s' for x in columns])
        
        # Construct the query we will execute to insert the row(s)
        query = f"""INSERT IGNORE INTO {table} ({keys}) VALUES """
        if has_multiple_rows:
            for p in parameters:
                query += f"""({values}),"""
            query     = query[:-1] 
            parameters = list(itertools.chain(*parameters))
        else:
            query += f"""({values}) """                      
        
        insert_id = self.query(query,parameters)[0]['LAST_INSERT_ID()']         
        return insert_id



#######################################################################################
# AUTHENTICATION RELATED
#######################################################################################

    def insertTransaction(self, table='table', columns=['x', 'y'], parameters=[['v11', 'v12'], ['v21', 'v22']]):

        if table == 'transaction_table':

            for param in parameters:

                self.query('INSERT INTO transactions(user_id, player_id, pass, rush, rec) VALUES(%s, %s, %s, %s, %s)', parameters=param)



    def insertTest(self, table='table', columns=['x', 'y'], parameters=[['v11', 'v12'], ['v21', 'v22']]):

        if table == 'transaction_table':

            for param in parameters:
                self.query(
                    'INSERT INTO test(user_id, player_id, pass, rush, rec) VALUES(%s, %s, %s, %s, %s)', parameters=param)



    def insertUserInfo(self, table='table', columns=['x', 'y'], parameters=[['v11', 'v12'], ['v21', 'v22']]):

        if table == 'user_table':

            for param in parameters:

                # self.query('INSERT INTO users(role, email, password, token) VALUES(%s, %s, %s, %s)', parameters=param)

                self.query('INSERT INTO users(role, email, password, token) VALUES(%s, %s, %s, %s)', parameters=param)

    def createUser(self, email='me@email.com', password='password', role='user', tokens=100):

        password = self.onewayEncrypt(password)
        #self.insertUserInfo('user_table', parameters=[[role, email, password, tokens]])

        # check if user already exists
        user_table = self.query("SELECT * FROM users")

        for item in user_table:

            if item["email"] == email:
                return {'success': 1}

        self.insertUserInfo('user_table', parameters=[[role, email, password, tokens]])

        return {'success': 1}

    def authenticate(self, email='me@email.com', password='password'):
        # lst = self.query('SELECT * from users')
        #
        # for item in lst:
        #
        #     if item["email"] == email and item["password"] == password:
        #
        #         return {'success': 1}
        #
        # return {'success': -1}

        lst = self.query("Select * From users Where email = '"+email+"'")
        for item in lst:

            if item["email"] == email and item["password"] == password:

                return {'success': 1}

        return {'success': -1}


    def onewayEncrypt(self, string):
        encrypted_string = hashlib.scrypt(string.encode('utf-8'),
                                          salt = self.encryption['oneway']['salt'],
                                          n    = self.encryption['oneway']['n'],
                                          r    = self.encryption['oneway']['r'],
                                          p    = self.encryption['oneway']['p']
                                          ).hex()
        return encrypted_string


    def reversibleEncrypt(self, type, message):
        fernet = Fernet(self.encryption['reversible']['key'])
        
        if type == 'encrypt':
            message = fernet.encrypt(message.encode())
        elif type == 'decrypt':
            message = fernet.decrypt(message).decode()

        return message


