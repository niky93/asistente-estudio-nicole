"""El agente: modelo + instrucciones + capabilities. Sin memoria: cada mensaje empieza de cero.

Pruébalo en la terminal, sin Telegram:  uv run asistente.py
"""

import asyncio

from pydantic_ai import Agent

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
        "No afirmes que guardas avances, programas recordatorios o recuerdas otros mensajes: "
        "este asistente no tiene esas funciones. Responde en español, breve y en texto plano."
    ),
    capabilities=[estudio, apis, consulta, registro, documentos],
)


async def responder(mensaje: str) -> str:
    """Lo único que necesita el bot: un mensaje entra, una respuesta sale."""
    resultado = await asistente.run(mensaje)  # await: mientras espera al modelo, el bot atiende a otros
    return resultado.output


async def main() -> None:
    while (mensaje := input("tú> ").strip()) not in {"", "salir"}:
        print("asistente>", await responder(mensaje))


if __name__ == "__main__":
    asyncio.run(main())  # un solo asyncio.run: todo lo async vive dentro
