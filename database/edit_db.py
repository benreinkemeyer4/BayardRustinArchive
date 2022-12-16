import psycopg2
from psycopg2 import Error
import urllib.parse as up
import os
from dotenv import load_dotenv


load_dotenv()

DATABASE_URL = os.environ.get('DATABASE_URL')
url = up.urlparse(DATABASE_URL)

def edit_db(submission):
    sub_name = submission["submitter-name"]
    date_taken = submission["date_taken"]
    sub_email = submission["submitter-email"]
    tags = ", ".join(submission["tags"])
    title = submission["title"]
    desc = submission["description"]
    sub_pronouns = submission["submitter-pronouns"]
    mediaid = submission["mediaid"]



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
        #cursor.execute('''INSERT INTO submissions (name,date_taken,date_uploaded,email,tags,title,description,media_url) VALUES ('Bob Dylan', '1993-03-15','2022-10-29', 'sw42@princeton.edu', 'document', 'test', 'test', 'test');''')

        stmt = '''UPDATE submissions
        SET name = %s, date_taken=%s, email=%s, tags=%s, title=%s, description=%s, pronouns=%s
        WHERE submission_id = %s;'''
        cursor.execute(stmt, (sub_name, date_taken, sub_email, tags, title, desc, sub_pronouns, mediaid))
        connection.commit()
        print("1 Record edited successfully")

        return True
        # Fetch result
        # cursor.execute("SELECT * from submissions")
        # record = cursor.fetchall()
        # print("Result ", record)

    except (Exception, Error) as error:
        print("Error while connecting to PostgreSQL", error)
        return False

    finally:
        if (connection):
            cursor.close()
            connection.close()
            print("PostgreSQL connection is closed")