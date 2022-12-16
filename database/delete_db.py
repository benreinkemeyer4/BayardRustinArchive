import psycopg2
from psycopg2 import Error
import urllib.parse as up
import os
from dotenv import load_dotenv


load_dotenv()

DATABASE_URL = os.environ.get('DATABASE_URL')
url = up.urlparse(DATABASE_URL)

def delete_db(media_id):

    try:
        up.uses_netloc.append("postgres")

        # Connect to an existing database
        connection = psycopg2.connect(database=url.path[1:],
        user=url.username,
        password=url.password,
        host=url.hostname,
        port=url.port)

        # Create a cursor to perform database operations
        cursor = connection.cursor()
        # Executing a SQL query
        stmt = '''DELETE FROM submissions WHERE submission_id= %s;'''
        cursor.execute(stmt, (media_id,))
        connection.commit()
        print("1 Record updated successfully")
        # Fetch result
        cursor.execute("SELECT * from submissions WHERE submission_id = %s", (media_id,))
        record = cursor.fetchall()
        print("Result ", record)
        return True

    except (Exception, Error) as error:
        print("Error while connecting to PostgreSQL", error)
        return False

    finally:
        if (connection):
            cursor.close()
            connection.close()
            print("PostgreSQL connection is closed")