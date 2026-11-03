"""Recordatorios de Jarvis guardados en Neon."""
from datetime import datetime, timedelta, timezone

from config import settings
from memoria import conexion


async def preparar_recordatorios() -> None:
    async with conexion() as conn:
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS recordatorios (
                id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
                chat_id TEXT NOT NULL,
                texto TEXT NOT NULL
                    CHECK (char_length(texto) BETWEEN 1 AND 1000),
                fecha TIMESTAMPTZ NOT NULL,
                estado TEXT NOT NULL DEFAULT 'pendiente'
                    CHECK (
                        estado IN ('pendiente', 'enviado', 'cancelado')
                    ),
                creado TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                enviado TIMESTAMPTZ
            )
        """)
        await conn.execute("""
            CREATE INDEX IF NOT EXISTS recordatorios_pendientes
            ON recordatorios (fecha)
            WHERE estado = 'pendiente'
        """)

HORA_BOLIVIA = timezone(timedelta(hours=-4))


async def crear_recordatorio(
    chat_id: str, texto: str, fecha_hora: str
) -> dict:
    """Crea un recordatorio. Fecha local: AAAA-MM-DD HH:MM."""
    if chat_id not in settings.permitidos:
        return {"error": "Chat no autorizado."}

    texto = texto.strip()
    if not 1 <= len(texto) <= 1000:
        return {"error": "El texto debe tener entre 1 y 1000 caracteres."}

    try:
        fecha = datetime.strptime(
            fecha_hora, "%Y-%m-%d %H:%M"
        ).replace(tzinfo=HORA_BOLIVIA)
    except ValueError:
        return {"error": "Usa una fecha válida con formato AAAA-MM-DD HH:MM."}

    if fecha <= datetime.now(HORA_BOLIVIA):
        return {"error": "La fecha y hora deben estar en el futuro."}

    async with conexion() as conn:
        cursor = await conn.execute(
            """
            INSERT INTO recordatorios (chat_id, texto, fecha)
            VALUES (%s, %s, %s)
            RETURNING id
            """,
            (chat_id, texto, fecha),
        )
        fila = await cursor.fetchone()

    return {
        "id": fila[0],
        "texto": texto,
        "fecha_hora_bolivia": fecha.strftime("%Y-%m-%d %H:%M"),
        "estado": "pendiente",
    }

async def listar_recordatorios(chat_id: str) -> dict:
    """Devuelve hasta 20 recordatorios pendientes del chat."""
    if chat_id not in settings.permitidos:
        return {"error": "Chat no autorizado."}

    async with conexion() as conn:
        cursor = await conn.execute(
            """
            SELECT id, texto, fecha
            FROM recordatorios
            WHERE chat_id = %s AND estado = 'pendiente'
            ORDER BY fecha, id
            LIMIT 20
            """,
            (chat_id,),
        )
        filas = await cursor.fetchall()

    return {
        "recordatorios": [
            {
                "id": fila[0],
                "texto": fila[1],
                "fecha_hora_bolivia": fila[2].astimezone(
                    HORA_BOLIVIA
                ).strftime("%Y-%m-%d %H:%M"),
            }
            for fila in filas
        ]
    }


async def cancelar_recordatorio(chat_id: str, numero: int) -> dict:
    """Cancela un recordatorio pendiente que pertenece al chat."""
    if chat_id not in settings.permitidos:
        return {"error": "Chat no autorizado."}

    async with conexion() as conn:
        cursor = await conn.execute(
            """
            UPDATE recordatorios
            SET estado = 'cancelado'
            WHERE id = %s
              AND chat_id = %s
              AND estado = 'pendiente'
            RETURNING id
            """,
            (numero, chat_id),
        )
        fila = await cursor.fetchone()

    if fila is None:
        return {"error": "No encontré ese recordatorio entre tus pendientes."}

    return {"id": fila[0], "estado": "cancelado"}