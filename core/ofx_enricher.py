"""
OFX Data Enricher - Extract CPF/CNPJ from memo field
"""

import re
from utils.cpf_cnpj_validator import clean_cpf_cnpj, validate_cpf_cnpj


def extract_cpf_cnpj_from_text(text):
    """
    Extract CPF or CNPJ from text (memo, description, etc.)

    Args:
        text: String to search for CPF/CNPJ

    Returns:
        str: Clean CPF/CNPJ digits or empty string
    """
    if not text or not isinstance(text, str):
        return ''

    # Patterns for CPF and CNPJ
    cpf_pattern = r'\d{3}\.?\d{3}\.?\d{3}-?\d{2}'
    cnpj_pattern = r'\d{2}\.?\d{3}\.?\d{3}/?\\d{4}-?\d{2}'

    # Try CNPJ first (longer)
    cnpj_match = re.search(cnpj_pattern, text)
    if cnpj_match:
        cnpj = clean_cpf_cnpj(cnpj_match.group())
        if validate_cpf_cnpj(cnpj):
            return cnpj

    # Try CPF
    cpf_match = re.search(cpf_pattern, text)
    if cpf_match:
        cpf = clean_cpf_cnpj(cpf_match.group())
        if validate_cpf_cnpj(cpf):
            return cpf

    return ''


def enrich_ofx_data(df):
    """
    Enrich OFX DataFrame with CPF/CNPJ column

    Args:
        df: OFX DataFrame

    Returns:
        DataFrame: Enriched with 'cpf_cnpj' column
    """
    if df is None or df.empty:
        return df

    # Extract CPF/CNPJ from memo field
    if 'memo' in df.columns:
        df['cpf_cnpj'] = df['memo'].apply(extract_cpf_cnpj_from_text)
    else:
        df['cpf_cnpj'] = ''

    # If memo didn't have CPF, try description
    if 'descricao' in df.columns:
        mask = df['cpf_cnpj'] == ''
        df.loc[mask, 'cpf_cnpj'] = df.loc[mask, 'descricao'].apply(extract_cpf_cnpj_from_text)

    return df
