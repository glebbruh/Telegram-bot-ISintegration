import os

import psycopg
from dotenv import load_dotenv

load_dotenv()

DB_URL = os.getenv("DB_URL")

def get_connection():
    return psycopg.connect(DB_URL)

def get_cursor(connection):
    return connection.cursor()

async def save_link(chat_id: int, user_id: int):
    async with get_connection() as connection:
        async with get_cursor(connection) as cursor:
            await cursor.execute('''
            INSERT INTO id_links (chat_id, user_id) 
            VALUES (%s, %s)
            ON CONFLICT (chat_id)
            DO UPDATE SET user_id = EXCLUDED.user_id;''',
                                 (chat_id, user_id))

async def delete_link(chat_id: int):
    async with get_connection() as connection:
        async with get_cursor(connection) as cursor:
            await cursor.execute('''
            DELETE FROM id_links WHERE chat_id = %s;''',
                                 (chat_id,))

async def get_chat_id(user_id: int):
    async with get_connection() as connection:
        async with get_cursor(connection) as cursor:
            await cursor.execute('''
            SELECT chat_id FROM id_links WHERE user_id = %s;''',
                                 (user_id,))
            return await cursor.fetchone()





