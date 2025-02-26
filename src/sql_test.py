import MySQLdb

try:
    connection = MySQLdb.connect(
        host='localhost',
        user='itilite',
        password='marwa1234',
        database='eauthor_db',
    )
    print("Connection successful!")
    connection.close()
except MySQLdb.Error as e:
    print(f"Error: {e}")