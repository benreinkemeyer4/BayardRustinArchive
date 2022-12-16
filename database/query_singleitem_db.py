import psycopg2
from psycopg2 import Error
import urllib.parse as up
import os
from dotenv import load_dotenv


load_dotenv()

DATABASE_URL = os.environ.get('DATABASE_URL')
url = up.urlparse(DATABASE_URL)

def query_singleitem_db(media_id):
    try:
        up.uses_netloc.append("postgres")

        # Connect to an existing database
        connection = psycopg2.connect(database=url.path[1:],
        user=url.username,
        password=url.password,
        host=url.hostname,
        port=url.port)

        print(media_id)

        # Create a cursor to perform database operations
        cursor = connection.cursor()
        stmt = "SELECT * FROM public.submissions WHERE submission_id = %s;"
        # Executing a SQL query
        cursor.execute(stmt, (media_id,))
        # Fetch result
        record = cursor.fetchall()

        return {"res": record, "error":False}

    except (Exception, Error) as error:
        print("Error while connecting to PostgreSQL", error)
        return {"res": error, "error":True}

    finally:
        if (connection):
            cursor.close()
            connection.close()
            print("PostgreSQL connection is closed")