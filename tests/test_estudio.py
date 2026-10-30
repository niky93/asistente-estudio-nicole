"""La planificación y su integración se comprueban sin llamar a Gemini."""

import os

os.environ.setdefault("GEMINI_API_KEY_LOCAL", "clave-de-prueba")

import pytest
from pydantic_ai import ModelResponse, TextPart, ToolCallPart, ToolReturnPart
from pydantic_ai.models.function import FunctionModel

import asistente
from capacidades import planificar_estudio


@pytest.mark.parametrize("minutos", [15, 41, 60, 180])
def test_el_plan_respeta_el_tiempo_disponible(minutos):
    resultado = planificar_estudio(["funciones", "listas"], minutos)
    assert resultado["minutos_totales"] == minutos
    assert sum(b["minutos"] for b in resultado["bloques"]) == minutos
    assert all(b["minutos"] > 0 for b in resultado["bloques"])
    assert any(b["actividad"] == "Descanso" for b in resultado["bloques"]) == (minutos >= 45)


@pytest.mark.parametrize("temas,minutos", [([], 60), ([" "], 60), (["tema"], 0), (["tema"], 181), (["tema"] * 6, 15)])
def test_el_plan_explica_entradas_invalidas(temas, minutos):
    assert "error" in planificar_estudio(temas, minutos)


async def test_el_agente_puede_usar_el_planificador():
    def modelo_falso(mensajes, info):
        ultimo = mensajes[-1].parts[-1]
        if isinstance(ultimo, ToolReturnPart):
            return ModelResponse(parts=[TextPart(str(ultimo.content))])
        return ModelResponse(parts=[ToolCallPart("planificar_estudio", {"temas": ["funciones"], "minutos": 45})])

    with asistente.asistente.override(model=FunctionModel(modelo_falso)):
        respuesta = await asistente.responder("Planifica 45 minutos para estudiar funciones")
    assert "45" in respuesta
    assert "Planificador local" in respuesta
