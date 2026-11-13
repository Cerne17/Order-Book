"""
Estratégias externas do simulador de mercado de ações (EEL670 - Linguagens de Programação).

Pacote importado pelo gerenciador C++ via pybind11 com `import agents`.
O C++ envia e recebe apenas dicts; a validação e a lógica ficam neste pacote.

Módulos:
- profile: `Profile`, parâmetros de comportamento de um agente.
- styles: estilos (Conservador, Moderado, Agressivo) e `StyleRegistry`.
- validation: `Side` e `FieldReader`, validação de dados vindos do C++.
- market: `MarketContext`, `AgentView`, `Suggestion`.
- report: relatório final da simulação.
- suggester: em desenvolvimento (sugestão de ordens).

Função de entrada:
- generate_profile: gera o perfil de um agente a partir de estilo, ajustes e semente.
"""

import random

from .profile import Profile
from .validation import FieldReader, Side
from .styles import Conservador, Moderado, Agressivo, StyleRegistry, StyleStrategy
from .market import AgentView, MarketContext, Suggestion
from .report import ParticipantResult, PortfolioView, Report, ReportCalculator, TradeRecord

def generate_profile(style: str, overrides: dict, seed: int) -> dict:
    """
    Gera o perfil de um agente a partir do estilo, dos ajustes e da semente.
    Args:
        style: nome do estilo ("conservador", "moderado" ou "agressivo"); ignora caixa e espaços.
        overrides: campos do perfil a substituir após o sorteio (pode ser vazio).
        seed: semente do gerador aleatório; mesma semente gera o mesmo perfil.
    Returns:
        dict: perfil do agente, com as chaves de `Profile.LIMITS`.
    Raises:
        TypeError: se `seed` não for int ou `overrides` não for dict.
        ValueError: se o estilo for desconhecido ou algum ajuste for inválido.
    """
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
    "StyleStrategy", "Conservador", "Moderado", "Agressivo", "StyleRegistry", # Styles
    "AgentView", "MarketContext", "Suggestion", # Market
    "TradeRecord", "PortfolioView", "ParticipantResult", "Report", "ReportCalculator", # Report
    ]