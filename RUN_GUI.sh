#!/bin/bash
# Script para executar OFX Consolidador Pro no Linux/Mac

# Configurar encoding UTF-8
export LANG=pt_BR.UTF-8
export LC_ALL=pt_BR.UTF-8
export PYTHONIOENCODING=utf-8

echo "================================================"
echo "  OFX Consolidador Pro v3.0"
echo "  Por: Tiago Schubert"
echo "================================================"
echo ""

# Ativa ambiente virtual se existir
if [ -d "venv" ]; then
    echo "Ativando ambiente virtual..."
    source venv/bin/activate
fi

# Executa a aplicação GUI
echo "Iniciando aplicacao..."
python3 main_gui.py
