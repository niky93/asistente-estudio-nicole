"""El agente: modelo + instrucciones + capabilities. Sin memoria: cada mensaje empieza de cero.

Pruébalo en la terminal, sin Telegram:  uv run asistente.py
"""

import asyncio

from pydantic_ai import Agent, Conversation

from capacidades import apis, consulta, documentos, estudio, registro
from config import modelo

asistente = Agent(
    modelo,
    # ← Cambia esto por tu caso: para quién es, qué hace y qué NO hace.
    instructions=(
        "Eres el asistente de estudio de Nicole. Ayuda a comprender conceptos, practicar "
        "con ejercicios y organizar sesiones según los temas y el tiempo disponible. "
        "Explica con ejemplos sencillos y pasos cortos. Cuando te pidan practicar, da una "
        "pregunta o ejercicio y espera el intento antes de mostrar la solución. "
        "Para crear un plan usa planificar_estudio y respeta su duración total. "
        "Distingue las explicaciones generales de la información de documentos: solo cita "
        "un documento si una herramienta lo ha recuperado. Si falta material o no sabes "
        "algo, dilo. Los contratos y gastos de ejemplo no son apuntes de una asignatura. "
        "Usa las capacidades de finanzas y clima únicamente si te lo piden expresamente. "
        "Usa el historial disponible para continuar el ejercicio y evaluar la respuesta. "
        "Si estamos estudiando Python, propone ejercicios de programación en Python. "
        "No afirmes guardar avances permanentemente ni programar recordatorios. "
        "Responde en español, breve y en texto plano, sin Markdown ni LaTeX."
    ),
    capabilities=[estudio, apis, consulta, registro, documentos],
)


conversaciones: dict[str, Conversation] = {}


async def responder(mensaje: str, chat_id: str | None = None) -> str:
    anterior = conversaciones.get(chat_id) if chat_id is not None else None

    resultado = await asistente.run(
        mensaje,
        conversation=anterior,
    )

    if chat_id is not None:
        conversaciones[chat_id] = resultado.conversation

    return resultado.output


async def main() -> None:
    while (mensaje := input("tú> ").strip()) not in {"", "salir"}:
        print("asistente>", await responder(mensaje))


if __name__ == "__main__":
    asyncio.run(main())  # un solo asyncio.run: todo lo async vive dentro
