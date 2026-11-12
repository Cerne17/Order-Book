"""
ESTRATEGIAS EXTERNAS DO SIMULADOR DE MERCADO DE ACOES (EEL670 - LINGUAGENS DE PROGRAMACAO)

Pacote importado pelo gerenciador C++ via pybind11 com `import agents`.
"""

import random

from .profile import Profile
from .validation import FieldReader, Side
from .styles import Conservador, Moderado, Agressivo, StyleRegistry, StyleStrategy

def generate_profile(style: str, overrides: dict, seed: int) -> dict:
    """Gera o perfil de um agente a partir do estilo, dos ajustes e da semente."""
    # mapeamento para o estilo de agente
    strategy = StyleRegistry.resolve(style.strip().lower())
    # checagem do tipo da seed
    FieldReader.require_int(seed, "seed")
    # geração do agente
    profile = strategy.draw_profile(random.Random(seed))
    # customização do agente gerado com base no dicionario recebido
    return profile.with_overrides(overrides).to_dict()



__all__ = [
    "Profile", # Profile
    "Side", "FieldReader", # Validation
    "StyleStrategy", "Conservador", "Moderado", "Agressivo", "StyleRegistry" # Styles
    ]