from .connection import start_connection
from .models import Models
import time


def start_db_with_docker():
    dbstatus = True
    while dbstatus:
        try:
            start_db()
            dbstatus = False
        except:
            print("Waiting for connection to Postgres Container")
            time.sleep(2)


def start_db():
    connection, cursor = start_connection()
    # add tables
    cursor.execute(Models.users)
    cursor.execute(Models.videos)
    cursor.execute(Models.users_videos)
    cursor.execute(Models.comments)
    cursor.execute(Models.token_revokes)

    connection.commit()
    print("Tables created successfully in PostgreSQL ")
    cursor.close()
    connection.close()
