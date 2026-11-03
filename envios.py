"""Servicio protegido para enviar recordatorios de Jarvis."""

import secrets

import httpx
from fastapi import Depends, FastAPI, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from config import settings
from memoria import conexion
from recordatorios import preparar_recordatorios

app = FastAPI(title="Envíos de Jarvis")
seguridad = HTTPBearer(auto_error=False)


def autorizar(
    credenciales: HTTPAuthorizationCredentials | None = Depends(seguridad),
) -> None:
    esperado = settings.cron_token.get_secret_value()
    recibido = credenciales.credentials if credenciales else ""

    if not esperado or not secrets.compare_digest(recibido, esperado):
        raise HTTPException(401, "No autorizado")


@app.get("/")
async def estado():
    return {"servicio": "Envíos de Jarvis", "estado": "activo"}


@app.post("/procesar", dependencies=[Depends(autorizar)])
async def procesar():
    token = settings.telegram_token.get_secret_value()
    if not token:
        raise HTTPException(503, "Falta configurar Telegram")

    enviados = 0

    try:
        await preparar_recordatorios()

        async with httpx.AsyncClient(timeout=10) as cliente:
            for _ in range(5):
                async with conexion() as conn:
                    cursor = await conn.execute("""
                        SELECT id, chat_id, texto
                        FROM recordatorios
                        WHERE estado = 'pendiente'
                          AND fecha <= NOW()
                        ORDER BY fecha, id
                        LIMIT 1
                        FOR UPDATE SKIP LOCKED
                    """)
                    fila = await cursor.fetchone()

                    if fila is None:
                        break

                    numero, chat, texto = fila

                    if chat not in settings.permitidos:
                        await conn.execute(
                            """
                            UPDATE recordatorios
                            SET estado = 'cancelado'
                            WHERE id = %s
                            """,
                            (numero,),
                        )
                        continue

                    respuesta = await cliente.post(
                        f"https://api.telegram.org/bot{token}/sendMessage",
                        json={
                            "chat_id": chat,
                            "text": f"Recordatorio #{numero}\n\n{texto}",
                        },
                    )
                    respuesta.raise_for_status()

                    if not respuesta.json().get("ok"):
                        raise RuntimeError("Telegram no confirmó el envío")

                    await conn.execute(
                        """
                        UPDATE recordatorios
                        SET estado = 'enviado', enviado = NOW()
                        WHERE id = %s
                        """,
                        (numero,),
                    )

                enviados += 1

    except Exception as error:
        print("Error en envíos:", type(error).__name__, flush=True)
        raise HTTPException(
            503, "No se pudo completar el procesamiento"
        ) from None

    return {"enviados": enviados}