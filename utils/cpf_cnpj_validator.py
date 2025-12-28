"""
CPF/CNPJ Validator and Formatter
Validates and formats Brazilian CPF and CNPJ numbers
"""


def validate_cpf(cpf):
    """
    Validate Brazilian CPF number

    Args:
        cpf: CPF string (with or without formatting)

    Returns:
        bool: True if valid, False otherwise
    """
    # Remove formatting
    cpf = ''.join(filter(str.isdigit, str(cpf)))

    # Must have 11 digits
    if len(cpf) != 11:
        return False

    # Cannot be all same digit
    if cpf == cpf[0] * 11:
        return False

    # Validate first check digit
    sum_digits = sum(int(cpf[i]) * (10 - i) for i in range(9))
    digit1 = (sum_digits * 10 % 11) % 10

    if int(cpf[9]) != digit1:
        return False

    # Validate second check digit
    sum_digits = sum(int(cpf[i]) * (11 - i) for i in range(10))
    digit2 = (sum_digits * 10 % 11) % 10

    if int(cpf[10]) != digit2:
        return False

    return True


def validate_cnpj(cnpj):
    """
    Validate Brazilian CNPJ number

    Args:
        cnpj: CNPJ string (with or without formatting)

    Returns:
        bool: True if valid, False otherwise
    """
    # Remove formatting
    cnpj = ''.join(filter(str.isdigit, str(cnpj)))

    # Must have 14 digits
    if len(cnpj) != 14:
        return False

    # Cannot be all same digit
    if cnpj == cnpj[0] * 14:
        return False

    # Validate first check digit
    weights1 = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    sum_digits = sum(int(cnpj[i]) * weights1[i] for i in range(12))
    digit1 = 11 - (sum_digits % 11)
    digit1 = 0 if digit1 >= 10 else digit1

    if int(cnpj[12]) != digit1:
        return False

    # Validate second check digit
    weights2 = [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    sum_digits = sum(int(cnpj[i]) * weights2[i] for i in range(13))
    digit2 = 11 - (sum_digits % 11)
    digit2 = 0 if digit2 >= 10 else digit2

    if int(cnpj[13]) != digit2:
        return False

    return True


def format_cpf(cpf):
    """
    Format CPF with standard formatting (###.###.###-##)

    Args:
        cpf: CPF string

    Returns:
        str: Formatted CPF or original if invalid
    """
    cpf = ''.join(filter(str.isdigit, str(cpf)))

    if len(cpf) != 11:
        return cpf

    return f"{cpf[:3]}.{cpf[3:6]}.{cpf[6:9]}-{cpf[9:]}"


def format_cnpj(cnpj):
    """
    Format CNPJ with standard formatting (##.###.###/####-##)

    Args:
        cnpj: CNPJ string

    Returns:
        str: Formatted CNPJ or original if invalid
    """
    cnpj = ''.join(filter(str.isdigit, str(cnpj)))

    if len(cnpj) != 14:
        return cnpj

    return f"{cnpj[:2]}.{cnpj[2:5]}.{cnpj[5:8]}/{cnpj[8:12]}-{cnpj[12:]}"


def clean_cpf_cnpj(value):
    """
    Remove all non-digit characters

    Args:
        value: CPF or CNPJ string

    Returns:
        str: Only digits
    """
    return ''.join(filter(str.isdigit, str(value)))


def identify_and_format(value):
    """
    Identify if value is CPF or CNPJ and format accordingly

    Args:
        value: CPF or CNPJ string

    Returns:
        tuple: (type, formatted_value, is_valid)
        type: 'CPF', 'CNPJ', or 'UNKNOWN'
    """
    clean = clean_cpf_cnpj(value)

    if len(clean) == 11:
        is_valid = validate_cpf(clean)
        return ('CPF', format_cpf(clean), is_valid)
    elif len(clean) == 14:
        is_valid = validate_cnpj(clean)
        return ('CNPJ', format_cnpj(clean), is_valid)
    else:
        return ('UNKNOWN', value, False)


def validate_cpf_cnpj(value):
    """
    Validate CPF or CNPJ automatically

    Args:
        value: CPF or CNPJ string

    Returns:
        bool: True if valid CPF or CNPJ
    """
    clean = clean_cpf_cnpj(value)

    if len(clean) == 11:
        return validate_cpf(clean)
    elif len(clean) == 14:
        return validate_cnpj(clean)
    else:
        return False
