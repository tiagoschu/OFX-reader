#!/bin/bash

# Script para executar a aplicação OFX Consolidador

# Ativa o ambiente virtual se existir
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Executa a aplicação
python app.py
