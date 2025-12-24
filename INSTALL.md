# Guia de Instalação - OFX Consolidador

## Instalação Rápida

### Windows

1. **Instale o Python**
   - Baixe Python 3.8+ em: https://www.python.org/downloads/
   - Durante a instalação, marque "Add Python to PATH"

2. **Baixe o projeto**
   - Extraia o ZIP ou clone o repositório

3. **Execute o instalador**
   ```cmd
   cd OFX-reader
   python -m venv venv
   venv\Scripts\activate
   pip install -r requirements.txt
   ```

4. **Execute a aplicação**
   - Dê um duplo clique em `run.bat`
   - Ou execute no terminal: `python app.py`

### Linux/Mac

1. **Verifique o Python**
   ```bash
   python3 --version
   ```
   - Deve ser 3.8 ou superior

2. **Clone/Baixe o projeto**
   ```bash
   cd OFX-reader
   ```

3. **Crie ambiente virtual e instale**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

4. **Execute a aplicação**
   ```bash
   chmod +x run.sh
   ./run.sh
   ```
   - Ou: `python app.py`

## Verificação da Instalação

Execute este comando para verificar se tudo está instalado:

```bash
python -c "import ofxparse, pandas, chardet, openpyxl; print('Tudo OK!')"
```

Se aparecer "Tudo OK!", a instalação foi bem-sucedida!

## Problemas Comuns

### "python não é reconhecido como comando"
- **Windows**: Reinstale o Python marcando "Add to PATH"
- **Linux/Mac**: Use `python3` em vez de `python`

### "ModuleNotFoundError: No module named 'tkinter'"

**Ubuntu/Debian:**
```bash
sudo apt-get install python3-tk
```

**Fedora:**
```bash
sudo dnf install python3-tkinter
```

**Mac:**
- Tkinter já vem com Python instalado via python.org
- Se instalou via Homebrew: `brew install python-tk`

### Erros ao instalar dependências

Tente atualizar o pip:
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

## Desinstalação

Para remover o projeto e suas dependências:

1. Desative o ambiente virtual:
   ```bash
   deactivate
   ```

2. Delete a pasta do projeto

## Próximos Passos

Após a instalação, consulte o [README.md](README.md) para instruções de uso.
