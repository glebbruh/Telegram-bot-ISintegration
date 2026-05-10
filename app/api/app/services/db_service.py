import os

import psycopg
from dotenv import load_dotenv

load_dotenv()

DB_URL = os.getenv("DB_URL")

async def get_connection():
    if DB_URL is None:
        raise Exception("DB_URL is not set")

    return await psycopg.AsyncConnection.connect(DB_URL)


async def save_link(chat_id: int, user_id: int):
    async with await get_connection() as connection:
        async with connection.cursor() as cursor:
            await cursor.execute('''
            INSERT INTO id_links (chat_id, user_id) 
            VALUES (%s, %s)
            ON CONFLICT (chat_id)
            DO UPDATE SET user_id = EXCLUDED.user_id;''',
                                 (chat_id, user_id))

async def delete_link(chat_id: int):
    async with await get_connection() as connection:
        async with connection.cursor() as cursor:
            await cursor.execute('''
            DELETE FROM id_links WHERE chat_id = %s;''',
                                 (chat_id,))

async def get_chat_id(user_id: int):
    async with await get_connection() as connection:
        async with connection.cursor() as cursor:
            await cursor.execute('''
            SELECT chat_id FROM id_links WHERE user_id = %s;''',
                                 (user_id,))

            row = await cursor.fetchone()
            if row is None:
                return None

            return row[0]





