"""Pruebas de la red de agentes sin llamar a ninguna API real.

Ejecutar:  python -m unittest discover tests
"""

import unittest

from app.agents.orchestrator import YaelCore
from app.agents.safety import SafetyGate
from app.agents.tool import PELIGROSO, params, texto, tool
from app.brain import llm
from app.brain.llm import Conversation, LLMProvider, ToolCall, Turn
from app.commands.command_manager import CommandManager
from app.tools import system


class ScriptedConversation(Conversation):
    """Devuelve turnos predefinidos según el agente (system prompt)."""

    def __init__(self, script, system_prompt, log):
        self.turns = list(script)
        self.system = system_prompt
        self.log = log

    def add_user(self, text):
        self.log.append(("user", text))

    def next(self):
        return self.turns.pop(0)

    def add_tool_results(self, results):
        for r in results:
            self.log.append(("tool_result", r.content, r.is_error))


class ScriptedProvider(LLMProvider):

    def __init__(self, scripts):
        # scripts: {fragmento del system prompt: [Turn, ...]}
        self.scripts = scripts
        self.log = []

    def new_conversation(self, system_prompt, tools):
        for fragment, script in self.scripts.items():
            if fragment in system_prompt:
                return ScriptedConversation(script, system_prompt, self.log)

        raise AssertionError("Sin guion para este agente")


class RedDeAgentesTest(unittest.TestCase):

    def tearDown(self):
        llm.set_provider(None)

    def test_orquestador_delega_y_especialista_usa_herramienta(self):
        provider = ScriptedProvider({
            "coordinar la red": [
                Turn(tool_calls=[ToolCall("1", "delegar_sistema", {"tarea": "estado de la PC"})]),
                Turn(text="Su PC está en buen estado."),
            ],
            "Agente de Sistema": [
                Turn(tool_calls=[ToolCall("a", "info_sistema", {})]),
                Turn(text="CPU y memoria normales."),
            ],
        })
        llm.set_provider(provider)

        core = YaelCore(confirmer=lambda d: True)
        respuesta = core.handle("¿cómo está mi computadora?")

        self.assertEqual(respuesta, "Su PC está en buen estado.")
        resultados = [e for e in provider.log if e[0] == "tool_result"]
        self.assertIn("CPU:", resultados[0][1])
        self.assertEqual(resultados[1][1], "CPU y memoria normales.")

    def test_accion_peligrosa_rechazada_no_se_ejecuta(self):
        ejecutado = []

        @tool("borrar", "prueba", params({"x": texto("x")}, ["x"]), risk=PELIGROSO)
        def borrar(x):
            ejecutado.append(x)
            return "borrado"

        from app.agents.base_agent import Agent

        provider = ScriptedProvider({
            "probador": [
                Turn(tool_calls=[ToolCall("1", "borrar", {"x": "a"})]),
                Turn(text="No se autorizó."),
            ],
        })
        llm.set_provider(provider)

        preguntas = []
        safety = SafetyGate(mode="confirmar_peligroso", confirmer=lambda d: preguntas.append(d) or False)
        agente = Agent("t", "probador", "probar", "", [borrar], safety)

        self.assertEqual(agente.run("borra a"), "No se autorizó.")
        self.assertEqual(ejecutado, [])
        self.assertEqual(len(preguntas), 1)
        self.assertTrue(provider.log[-1][2])  # is_error

    def test_modos_de_seguridad(self):
        seguro = system.info_sistema
        peligroso = system.ejecutar_powershell

        self.assertFalse(SafetyGate(mode="confirmar_peligroso").needs_confirmation(seguro))
        self.assertTrue(SafetyGate(mode="confirmar_peligroso").needs_confirmation(peligroso))
        self.assertTrue(SafetyGate(mode="confirmar_todo").needs_confirmation(seguro))
        self.assertFalse(SafetyGate(mode="autonomo").needs_confirmation(peligroso))

    def test_powershell_bloquea_comandos_destructivos(self):
        with self.assertRaises(PermissionError):
            system.ejecutar_powershell.func("Format-Volume -DriveLetter C")

    def test_comandos_rapidos(self):
        cm = CommandManager()
        self.assertTrue(cm.execute("¿Qué hora es?").startswith("Son las"))
        self.assertIsNone(cm.execute("hola, abre chrome y busca noticias"))


if __name__ == "__main__":
    unittest.main()
