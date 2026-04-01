# Re-exports para manter compatibilidade com imports existentes.
from whatsapp.services.cliente_waha import (
    enviar_mensagem,
    ids_enviados_pelo_bot,
)
from whatsapp.services.processador import (
    PREFIXO_BOT,
    _normalizar_corpo,
    processar_mensagem,
)
from whatsapp.services.utils import (
    MENU_TEXTO,
    _escolher_item,
    _listar_categorias,
    _listar_fontes,
    _obter_resumo,
    _parse_valor,
    _sem_cadastro,
)

__all__ = [
    "MENU_TEXTO",
    "PREFIXO_BOT",
    "enviar_mensagem",
    "ids_enviados_pelo_bot",
    "processar_mensagem",
    "_escolher_item",
    "_listar_categorias",
    "_listar_fontes",
    "_normalizar_corpo",
    "_obter_resumo",
    "_parse_valor",
    "_sem_cadastro",
]
