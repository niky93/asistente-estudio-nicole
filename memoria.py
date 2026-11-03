"""Historial de conversaciones guardado en PostgreSQL."""

from contextlib import asynccontextmanager

from psycopg import AsyncConnection
from pydantic_ai import Conversation
from pydantic_ai.conversation import ConversationTypeAdapter

from config import settings


@asynccontextmanager
async def conexion():
    url = settings.database_url.get_secret_value()
    if not url:
        raise RuntimeError("Falta configurar DATABASE_URL.")

    async with await AsyncConnection.connect(
        url, connect_timeout=15
    ) as conn:
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS conversaciones (
                chat_id TEXT PRIMARY KEY,
                contenido TEXT NOT NULL,
                actualizado TIMESTAMPTZ NOT NULL DEFAULT NOW()
            )
        """)
        yield conn


async def cargar_conversacion(chat_id: str) -> Conversation | None:
    async with conexion() as conn:
        cursor = await conn.execute(
            "SELECT contenido FROM conversaciones WHERE chat_id = %s",
            (chat_id,),
        )
        fila = await cursor.fetchone()

    if fila is None:
        return None

    return ConversationTypeAdapter.validate_json(fila[0])


async def guardar_conversacion(
    chat_id: str, conversacion: Conversation
) -> None:
    contenido = ConversationTypeAdapter.dump_json(
        conversacion
    ).decode("utf-8")

    async with conexion() as conn:
        await conn.execute(
            """
            INSERT INTO conversaciones (chat_id, contenido)
            VALUES (%s, %s)
            ON CONFLICT (chat_id) DO UPDATE
            SET contenido = EXCLUDED.contenido,
                actualizado = NOW()
            """,
            (chat_id, contenido),
        )