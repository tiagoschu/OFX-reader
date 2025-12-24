#!/usr/bin/env python3
"""
Script de diagnóstico para arquivos OFX problemáticos
"""

import os
import sys
import chardet

def diagnose_ofx_file(file_path):
    """Diagnóstica um arquivo OFX"""
    print("\n" + "=" * 70)
    print(f"Diagnóstico: {os.path.basename(file_path)}")
    print("=" * 70)

    # 1. Verificar se o arquivo existe e tamanho
    if not os.path.exists(file_path):
        print("❌ Arquivo não encontrado!")
        return

    file_size = os.path.getsize(file_path)
    print(f"✓ Tamanho: {file_size} bytes ({file_size/1024:.2f} KB)")

    if file_size == 0:
        print("❌ Arquivo vazio!")
        return

    if file_size < 100:
        print("⚠️ Arquivo muito pequeno - pode estar incompleto")

    # 2. Detectar encoding
    with open(file_path, 'rb') as f:
        raw_data = f.read()
        detected = chardet.detect(raw_data)
        print(f"✓ Encoding detectado: {detected['encoding']} (confiança: {detected['confidence']*100:.1f}%)")

    # 3. Verificar primeiras linhas
    print("\n📄 Primeiras 15 linhas do arquivo:")
    print("-" * 70)

    try:
        # Tentar UTF-8 primeiro
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            for i, line in enumerate(f):
                if i >= 15:
                    break
                # Limitar tamanho da linha
                line = line.strip()[:70]
                print(f"{i+1:2d}: {line}")
    except Exception as e:
        print(f"❌ Erro ao ler: {e}")

        # Tentar Latin-1
        try:
            print("\nTentando com Latin-1...")
            with open(file_path, 'r', encoding='latin-1', errors='ignore') as f:
                for i, line in enumerate(f):
                    if i >= 15:
                        break
                    line = line.strip()[:70]
                    print(f"{i+1:2d}: {line}")
        except Exception as e2:
            print(f"❌ Erro ao ler com Latin-1: {e2}")

    # 4. Verificar estrutura OFX
    print("\n🔍 Validação de estrutura OFX:")
    print("-" * 70)

    content = raw_data.decode('latin-1', errors='ignore')

    # Verificar headers OFX
    has_ofx_header = 'OFXHEADER' in content or 'ofxheader' in content.lower()
    has_ofx_tag = '<OFX>' in content or '<ofx>' in content.lower()
    has_transactions = '<STMTTRN>' in content or '<stmttrn>' in content.lower()

    print(f"{'✓' if has_ofx_header else '❌'} OFXHEADER encontrado: {has_ofx_header}")
    print(f"{'✓' if has_ofx_tag else '❌'} Tag <OFX> encontrada: {has_ofx_tag}")
    print(f"{'✓' if has_transactions else '⚠️'} Transações encontradas: {has_transactions}")

    # Contar transações
    if has_transactions:
        txn_count = content.upper().count('<STMTTRN>')
        print(f"  → Total de transações: {txn_count}")

    # 5. Procurar por caracteres problemáticos
    print("\n🔤 Análise de caracteres:")
    print("-" * 70)

    # Procurar bytes problemáticos
    problem_bytes = []
    for i, byte in enumerate(raw_data[:1000]):  # Primeiros 1000 bytes
        if byte > 127:  # Não-ASCII
            problem_bytes.append((i, byte, chr(byte) if byte < 256 else '?'))

    if problem_bytes:
        print(f"⚠️ Encontrados {len(problem_bytes)} bytes não-ASCII nos primeiros 1000 bytes:")
        for pos, byte, char in problem_bytes[:10]:  # Mostrar primeiros 10
            print(f"  Posição {pos}: byte 0x{byte:02x} ('{char}')")
        if len(problem_bytes) > 10:
            print(f"  ... e mais {len(problem_bytes) - 10} bytes")
    else:
        print("✓ Apenas caracteres ASCII nos primeiros 1000 bytes")

    # 6. Procurar por declaração de encoding no arquivo
    print("\n📋 Encoding declarado no arquivo:")
    print("-" * 70)

    for line in content.split('\n')[:20]:
        if 'ENCODING' in line.upper() or 'CHARSET' in line.upper():
            print(f"  → {line.strip()}")

    # 7. Verificar se é HTML ou erro de download
    print("\n🌐 Verificação de formato:")
    print("-" * 70)

    is_html = '<html>' in content.lower() or '<!doctype' in content.lower()
    is_json = content.strip().startswith('{') or content.strip().startswith('[')
    is_xml = content.strip().startswith('<?xml')

    if is_html:
        print("❌ PROBLEMA: Arquivo parece ser HTML, não OFX!")
        print("   → Provavelmente página de erro do banco")
    elif is_json:
        print("❌ PROBLEMA: Arquivo parece ser JSON, não OFX!")
    elif is_xml:
        print("✓ Arquivo parece ser XML válido")
    elif has_ofx_header:
        print("✓ Arquivo parece ser OFX válido (formato SGML)")
    else:
        print("⚠️ Formato não identificado claramente")

    # 8. Recomendações
    print("\n💡 Recomendações:")
    print("-" * 70)

    if not has_ofx_header and not has_ofx_tag:
        print("❌ Arquivo NÃO parece ser OFX válido")
        print("   → Baixe o arquivo novamente do banco C6")
        print("   → Verifique se está selecionando o formato correto (OFX, não CSV/PDF)")
    elif is_html:
        print("❌ Arquivo é uma página HTML (erro do site)")
        print("   → Baixe novamente, garantindo que não é página de erro")
    elif not has_transactions:
        print("⚠️ Arquivo OFX válido mas sem transações")
        print("   → Período pode não ter movimentações")
    elif file_size < 500:
        print("⚠️ Arquivo muito pequeno")
        print("   → Pode estar incompleto ou corrompido")
    else:
        print("✓ Arquivo parece válido - problema pode ser de encoding específico")
        print("   → Tente abrir no editor e salvar como UTF-8")
        print("   → Ou use ferramenta de conversão de encoding")


def main():
    """Função principal"""
    print("=" * 70)
    print("DIAGNÓSTICO DE ARQUIVOS OFX PROBLEMÁTICOS")
    print("=" * 70)

    if len(sys.argv) < 2:
        print("\nUso: python diagnose_files.py <arquivo.ofx> [arquivo2.ofx] ...")
        print("\nOu arraste os arquivos problemáticos para este script")
        print("\nArquivos problemáticos conhecidos:")
        print("  - Extrato_Conta_Corrente_C6Bank_23_12_2025.ofx")
        print("  - C6 08 Extrato_Conta_Corrente_C6Bank_05_09_2025.ofx")
        print("  - c6-03-2501JRJGP3767FBA0G8ZR9BYYTGC.ofx")
        print("  - c6-02-25 01JRJGT82DET8GZ92MYNBXNX2Q.ofx")
        print("  (e outros 6 arquivos C6 Bank)")
        return

    # Diagnosticar cada arquivo
    for file_path in sys.argv[1:]:
        diagnose_ofx_file(file_path)

    print("\n" + "=" * 70)
    print("Diagnóstico concluído!")
    print("=" * 70)


if __name__ == "__main__":
    main()
