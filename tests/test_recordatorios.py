import os

os.environ.setdefault("GEMINI_API_KEY_LOCAL", "clave-de-prueba")

import httpx
import pytest
from pydantic import SecretStr

import envios
from config import settings
from recordatorios import (
    crear_recordatorio,
    listar_recordatorios,
    cancelar_recordatorio,
)


async def test_recordatorios_rechazan_chat_ajeno(monkeypatch):
    monkeypatch.setattr(settings, "telegram_permitidos", "123")

    resultados = [
        await crear_recordatorio("999", "Estudiar", "2099-01-01 18:00"),
        await listar_recordatorios("999"),
        await cancelar_recordatorio("999", 1),
    ]

    assert all(r == {"error": "Chat no autorizado."} for r in resultados)


@pytest.mark.parametrize("fecha", ["fecha incorrecta", "2000-01-01 18:00"])
async def test_fecha_invalida_o_pasada_no_se_guarda(monkeypatch, fecha):
    monkeypatch.setattr(settings, "telegram_permitidos", "123")

    resultado = await crear_recordatorio("123", "Estudiar", fecha)

    assert "error" in resultado


async def test_envios_rechaza_sin_clave(monkeypatch):
    monkeypatch.setattr(settings, "cron_token", SecretStr("clave-de-prueba"))

    transporte = httpx.ASGITransport(app=envios.app)
    async with httpx.AsyncClient(
        transport=transporte, base_url="http://prueba"
    ) as cliente:
        respuesta = await cliente.post("/procesar")

    assert respuesta.status_code == 401