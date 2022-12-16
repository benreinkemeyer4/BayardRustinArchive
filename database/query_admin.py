import psycopg2
from psycopg2 import Error
import urllib.parse as up
import os
from dotenv import load_dotenv


load_dotenv()

DATABASE_URL = os.environ.get('DATABASE_URL')
url = up.urlparse(DATABASE_URL)


def query_admin():
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
        cursor.execute("SELECT * FROM public.admins;")
        # Fetch result
        record = cursor.fetchall()
        emails = []
        for r in record:
            emails.append(r[1])
        return {"result":emails, "error":False}

    except (Exception, Error) as error:
        print("Error while connecting to PostgreSQL", error)
        return {"error":True, "result":error}

    finally:
        if (connection):
            cursor.close()
            connection.close()
            print("PostgreSQL connection is closed")