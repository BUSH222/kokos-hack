"""
Library for managing the server's database connection.
Run this file to create the database, and fill it with data;
Import connect_to_db to receive connection and cursor objects.

Here logging is used instead of logger due to circular import issues.
"""

import psycopg2
from psycopg2 import sql
import logging

dinamic_host = 'db'


def connect_to_db(db_name='kokos', postgres_pwd='12345678', host=dinamic_host, port='5432'):
    """
    Creates a connection to a postgres database and returns the connection and cursor objects
    Args:
        db_name (str): name of the created database
        postgres_pwd (str): password of the user "postgres"
        host (str): host of the postgres server
        port (str): port of the postgres server
    Returns:
        conn (psycopg2.extensions.connection): connection object to the postgres server
        cursor (psycopg2.extensions.cursor): cursor object to the postgres server
    """
    conn = psycopg2.connect(database=db_name,
                            user='postgres',
                            host=host,
                            password=postgres_pwd,
                            port=port)
    cursor = conn.cursor()
    logging.info('Connected to {db_name}')
    return conn, cursor


def create_db(db_name='kokos', postgres_pwd='12345678', host=dinamic_host, port='5432') -> None:
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
    # estabilishing a connection to the default postgres db
    conn, cursor = connect_to_db(db_name='postgres', postgres_pwd=postgres_pwd, host=host, port=port)
    conn.autocommit = True
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


def create_tables(populate=False, db_name='kokos', postgres_pwd='12345678', host=dinamic_host, port='5432') -> None:
    """Creates the tables according to schema.sql and populates them with data according to populate.sql
    Args:
        populate (bool): whether to populate the newly created tables with data from populate.sql
        db_name (str): name of the created database
        postgres_pwd (str): password of the user "postgres"
        host (str): host of the postgres server
        port (str): port of the postgres server
    Returns:
        None
    """
    logging.info('Table creation operation started')
    logging.info('Connecting to the PostgreSQL server')
    conn, cursor = connect_to_db(db_name=db_name, postgres_pwd=postgres_pwd, host=host, port=port)
    logging.info('Creating tables')
    with open('schema.sql', 'r') as schema_obj:
        schema = schema_obj.read()
        cursor.execute(schema)
    conn.commit()
    if populate:
        logging.info('Populating tables')
        with open('populate.sql', 'r') as populate_obj:
            populate_query = populate_obj.read()
            cursor.execute(populate_query)
    conn.commit()
    cursor.close()
    conn.close()
    logging.info('Table creation operation completed')


if __name__ == '__main__':
    create_db()
    create_tables(populate=True)
