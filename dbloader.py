import psycopg2
from psycopg2 import sql
import logging


def create_db(db_name='kokos', postgres_pwd='12345678', host='localhost', port='5432') -> None:
    """Creates an empty database inside the postgres server.
    Args:
        db_name (str): name of the created database
        postgres_pwd (str): password of the user "postgres"
        host (str): host of the postgres server
        port (str): port of the postgres server
    Returns:
        None
    Raises:
        None
    """
    logging.info('Database creation operation started')
    logging.info('Connecting to the PostgreSQL server')
    conn = psycopg2.connect(
        dbname='postgres',  # estabilish a connection to the default postgres db
        user='postgres',
        password=postgres_pwd,
        host=host,
        port=port,
    )
    conn.autocommit = True  # Enable autocommit mode
    cursor = conn.cursor()

    logging.info('Checking if the database exists')
    cursor.execute('SELECT 1 FROM pg_database WHERE datname = %s', (db_name,))
    exists = cursor.fetchone()

    if not exists:
        logging.info('Database doesn\'t exist, creating a new one')
        cursor.execute(sql.SQL(
            'CREATE DATABASE {} WITH OWNER = %s ENCODING = %s LOCALE_PROVIDER = %s CONNECTION LIMIT = %s'
        ).format(sql.Identifier(db_name)),
            ('postgres', 'UTF8', 'libc', -1)
        )
        logging.info(f"Database '{db_name}' created successfully.")
    else:
        logging.info(f"Database '{db_name}' already exists.")

    cursor.close()
    conn.close()
    logging.info('Database creation operation completed')


def create_tables(populate=False, db_name='kokos', postgres_pwd='12345678', host='localhost', port='5432') -> None:
    """Creates the tables according to schema.sql and populates them with data according to populate.sql
    Args:
        populate (bool): whether to populate the newly created tables with data
        db_name (str): name of the created database
        postgres_pwd (str): password of the user "postgres"
        host (str): host of the postgres server
        port (str): port of the postgres server
    Returns:
        None
    """
    conn = psycopg2.connect(database=db_name,
                            user='postgres',
                            host=host,
                            password=postgres_pwd,
                            port=port)
    cursor = conn.cursor()
    with open('schema.sql', 'r') as schema_obj:
        schema = schema_obj.read()
        cursor.execute(schema)
    conn.commit()
    if populate:
        with open('populate.sql', 'r') as populate_obj:
            populate_query = populate_obj.read()
            cursor.execute(populate_query)
    conn.commit()
    cursor.close()
    conn.close()


if __name__ == '__main__':
    create_db()
    create_tables(populate=True)
