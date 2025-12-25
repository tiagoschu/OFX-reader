# 🚀 Guia de Instalação e Uso - OFX Consolidador Pro v3.0

## 📋 Requisitos

- Python 3.8 ou superior
- pip (gerenciador de pacotes Python)

## 🔧 Instalação

### 1. Criar Ambiente Virtual (Recomendado)

**Windows:**
```cmd
python -m venv venv
venv\Scripts\activate
```

**Linux/Mac:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 2. Instalar Dependências GUI

```bash
pip install -r requirements-gui.txt
```

Isso irá instalar:
- PyQt5 (interface gráfica)
- Plotly (gráficos interativos)
- fpdf2 (geração de PDF)
- E todas as dependências do core (ofxparse, pandas, etc)

## ▶️ Como Executar

### Método 1: Scripts Prontos

**Windows:**
```cmd
RUN_GUI.bat
```

**Linux/Mac:**
```bash
chmod +x RUN_GUI.sh
./RUN_GUI.sh
```

### Método 2: Comando Direto

```bash
python main_gui.py
```

## 🎯 Primeira Execução

1. **Splash Screen** aparecerá com suas informações
2. **Janela Principal** abrirá com 8 abas
3. Vá para aba **"Importar"**
4. Clique em **"📁 Adicionar Arquivos OFX"**
5. Selecione seus arquivos OFX
6. Clique em **"⚡ Processar Arquivos"**
7. Aguarde o processamento
8. Visualize o resumo e exporte!

## 📊 Abas Disponíveis

### ✅ Funcionais (v3.0 MVP):
- **🏠 Início**: Dashboard com visão geral
- **📥 Importar**: Importação e processamento de OFX

### 🚧 Em Desenvolvimento:
- **📊 Análises**: Análises detalhadas (em breve)
- **📈 Gráficos**: Visualizações interativas (em breve)
- **🎯 Categorias**: Gerenciar categorias (em breve)
- **📋 Relatórios**: Relatórios personalizados (em breve)
- **💾 Exportar**: Exportação multi-formato (em breve)
- **⚙️ Config**: Configurações (em breve)

## 🐛 Solução de Problemas

### Erro: "No module named 'PyQt5'"

```bash
pip install PyQt5
```

### Erro: "ModuleNotFoundError: No module named 'tkinter'"

Não precisa! A versão GUI usa PyQt5, não tkinter.

### Erro: "cannot import name 'OFXProcessor'"

Certifique-se de estar no diretório correto:
```bash
cd OFX-reader
python main_gui.py
```

### Interface não abre

1. Verifique se PyQt5 está instalado:
   ```bash
   pip list | grep PyQt5
   ```

2. Teste a instalação:
   ```bash
   python -c "from PyQt5.QtWidgets import QApplication; print('OK')"
   ```

## 🎨 Personalização

### Desabilitar Splash Screen

Edite `~/.ofx_consolidador/config.json`:
```json
{
  "show_splash": false
}
```

### Alterar Diretório Padrão

O diretório padrão é salvo automaticamente após a primeira seleção.

## 📝 Notas

- **Dados processados** não são salvos automaticamente
- **Configurações** são salvas em `~/.ofx_consolidador/`
- **Geometria da janela** é restaurada na próxima execução

## 🆘 Suporte

Para problemas ou dúvidas:
1. Verifique este guia
2. Leia o README.md principal
3. Abra uma issue no repositório

---

**Desenvolvido por Tiago Schubert - Janeiro 2025**
