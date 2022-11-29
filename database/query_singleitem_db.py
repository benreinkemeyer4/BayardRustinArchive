import psycopg2
from psycopg2 import Error
import urllib.parse as up

url = up.urlparse("postgres://oegsfiae:WUg1B4yX8l8PXcVH_E87mjkgD6IfcTOV@peanut.db.elephantsql.com/oegsfiae")


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
        return record

    except (Exception, Error) as error:
        print("Error while connecting to PostgreSQL", error)

    finally:
        if (connection):
            cursor.close()
            connection.close()
            print("PostgreSQL connection is closed")