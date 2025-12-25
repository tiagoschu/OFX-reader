"""
Constants for OFX Consolidador Pro
"""

# Application Information
APP_NAME = "OFX Consolidador Pro"
VERSION = "3.0.0"
AUTHOR = "Tiago Schubert"
RELEASE_DATE = "Janeiro 2025"
DESCRIPTION = "Análise Inteligente de Extratos Bancários"

# Window Settings
WINDOW_TITLE = f"{APP_NAME} v{VERSION}"
WINDOW_MIN_WIDTH = 1200
WINDOW_MIN_HEIGHT = 800
SPLASH_DURATION = 2000  # milliseconds

# Colors (Material Design inspired)
COLOR_PRIMARY = "#1976D2"       # Blue
COLOR_PRIMARY_DARK = "#1565C0"
COLOR_PRIMARY_LIGHT = "#42A5F5"
COLOR_ACCENT = "#FF4081"        # Pink
COLOR_SUCCESS = "#4CAF50"       # Green
COLOR_WARNING = "#FFC107"       # Amber
COLOR_ERROR = "#F44336"         # Red
COLOR_INFO = "#2196F3"          # Light Blue

# Background colors
COLOR_BG_DARK = "#263238"
COLOR_BG_LIGHT = "#ECEFF1"
COLOR_CARD_BG = "#FFFFFF"

# Text colors
COLOR_TEXT_PRIMARY = "#212121"
COLOR_TEXT_SECONDARY = "#757575"
COLOR_TEXT_DISABLED = "#BDBDBD"

# Transaction categories
CATEGORIES = {
    'Alimentação': {
        'keywords': ['mercado', 'supermercado', 'padaria', 'restaurante', 'lanchonete',
                    'ifood', 'rappi', 'uber eats', 'delivery'],
        'color': '#FF6F00',
        'icon': '🍽️'
    },
    'Transporte': {
        'keywords': ['uber', '99', 'combustivel', 'gasolina', 'posto', 'estacionamento',
                    'pedágio', 'transporte', 'onibus', 'metro'],
        'color': '#1976D2',
        'icon': '🚗'
    },
    'Transferências': {
        'keywords': ['pix', 'ted', 'doc', 'transferencia', 'transferência'],
        'color': '#7B1FA2',
        'icon': '💸'
    },
    'Investimentos': {
        'keywords': ['aplicacao', 'aplicação', 'resgate', 'investimento', 'cdb',
                    'tesouro', 'fundo', 'acao', 'ação'],
        'color': '#388E3C',
        'icon': '📈'
    },
    'Salário/Receitas': {
        'keywords': ['salario', 'salário', 'vencimento', 'pagamento recebido',
                    'deposito', 'depósito'],
        'color': '#4CAF50',
        'icon': '💰'
    },
    'Contas/Serviços': {
        'keywords': ['conta', 'fatura', 'energia', 'agua', 'água', 'internet',
                    'telefone', 'celular', 'tv', 'streaming', 'netflix', 'spotify'],
        'color': '#F57C00',
        'icon': '📄'
    },
    'Saúde': {
        'keywords': ['farmacia', 'farmácia', 'drogaria', 'hospital', 'clinica',
                    'clínica', 'medico', 'médico', 'consulta', 'exame'],
        'color': '#C62828',
        'icon': '⚕️'
    },
    'Educação': {
        'keywords': ['escola', 'faculdade', 'universidade', 'curso', 'livro',
                    'material escolar'],
        'color': '#0277BD',
        'icon': '📚'
    },
    'Lazer': {
        'keywords': ['cinema', 'show', 'teatro', 'viagem', 'hotel', 'passeio',
                    'parque', 'ingresso'],
        'color': '#E91E63',
        'icon': '🎭'
    },
    'Compras': {
        'keywords': ['loja', 'shopping', 'magazine', 'eletronico', 'eletrônico',
                    'roupa', 'calçado'],
        'color': '#9C27B0',
        'icon': '🛍️'
    },
    'Cartão': {
        'keywords': ['fatura de cartao', 'fatura de cartão', 'pagamento cartao'],
        'color': '#455A64',
        'icon': '💳'
    },
    'Outros': {
        'keywords': [],
        'color': '#607D8B',
        'icon': '📦'
    }
}

# Export formats
EXPORT_FORMATS = {
    'csv': {'name': 'CSV (separado por ;)', 'extension': '.csv'},
    'excel': {'name': 'Excel (.xlsx)', 'extension': '.xlsx'},
    'ofx': {'name': 'OFX Consolidado', 'extension': '.ofx'},
    'json': {'name': 'JSON', 'extension': '.json'},
    'pdf': {'name': 'PDF com Relatório', 'extension': '.pdf'},
}

# Date formats
DATE_FORMAT_DISPLAY = "%d/%m/%Y"
TIME_FORMAT_DISPLAY = "%H:%M:%S"
DATETIME_FORMAT_DISPLAY = f"{DATE_FORMAT_DISPLAY} {TIME_FORMAT_DISPLAY}"

# Chart settings
CHART_HEIGHT = 400
CHART_COLORS = [
    '#1976D2', '#FF4081', '#4CAF50', '#FFC107', '#9C27B0',
    '#FF5722', '#00BCD4', '#8BC34A', '#FF9800', '#E91E63'
]
