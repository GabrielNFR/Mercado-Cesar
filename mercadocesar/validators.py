"""
Validadores para cartão de crédito
"""
import re
from datetime import datetime
from decimal import Decimal


def validar_numero_cartao(numero):
    numero = re.sub(r'[\s-]', '', numero)
    
    if not numero.isdigit():
        return False, "Número do cartão deve conter apenas dígitos"
    
    if len(numero) < 13 or len(numero) > 19:
        return False, "Número do cartão deve ter entre 13 e 19 dígitos"
    
    def luhn_checksum(card_number):
        def digits_of(n):
            return [int(d) for d in str(n)]
        digits = digits_of(card_number)
        odd_digits = digits[-1::-2]
        even_digits = digits[-2::-2]
        checksum = sum(odd_digits)
        for d in even_digits:
            checksum += sum(digits_of(d * 2))
        return checksum % 10
    
    if luhn_checksum(numero) != 0:
        return False, "Número do cartão inválido"
    
    return True, ""


def validar_cvv(cvv):
    """Valida CVV (3 ou 4 dígitos)"""
    if not cvv.isdigit():
        return False, "CVV deve conter apenas dígitos"
    
    if len(cvv) < 3 or len(cvv) > 4:
        return False, "CVV deve ter 3 ou 4 dígitos"
    
    return True, ""


def validar_validade(mes, ano):
    """Valida data de validade do cartão"""
    try:
        mes = int(mes)
        ano = int(ano)
    except (ValueError, TypeError):
        return False, "Mês e ano devem ser números válidos"
    
    if mes < 1 or mes > 12:
        return False, "Mês deve estar entre 1 e 12"
    
    if ano < 100:
        ano += 2000
    
    if ano < 2000 or ano > 2099:
        return False, "Ano inválido"
    
    hoje = datetime.now()
    if ano < hoje.year or (ano == hoje.year and mes < hoje.month):
        return False, "Cartão vencido"
    
    return True, ""


def identificar_bandeira(numero):
    """Identifica a bandeira do cartão pelo número"""
    numero = re.sub(r'[\s-]', '', numero)
    
    if not numero:
        return "Desconhecida"
    
    if numero[0] == '4':
        return "Visa"
    
    if numero[:2] in ['51', '52', '53', '54', '55']:
        return "Mastercard"
    if len(numero) >= 4 and 2221 <= int(numero[:4]) <= 2720:
        return "Mastercard"
    
    if numero[:2] in ['34', '37']:
        return "American Express"
    
    elo_bins = ['636368', '438935', '504175', '451416', '636297', '5067', '4576', '4011']
    for bin_code in elo_bins:
        if numero.startswith(bin_code):
            return "Elo"
    
    if numero.startswith('606282'):
        return "Hipercard"
    
    if numero[:2] in ['36', '38']:
        return "Diners Club"
    
    return "Outra"


def validar_cep(cep):
    """Valida formato de CEP brasileiro"""
    cep = cep.strip()
    
    # Verifica formato XXXXX-XXX ou XXXXXXXX
    pattern = r'^\d{5}-?\d{3}$'
    
    if not re.match(pattern, cep):
        return False, "CEP inválido. Por favor, insira um CEP válido no formato 12345-678"
    
    # Remove o hífen
    cep_numeros = re.sub(r'[^0-9]', '', cep)
    
    # Verifica se não é um CEP obviamente inválido
    if cep_numeros == '00000000':
        return False, "CEP inválido"
    
    return True, cep_numeros


def verificar_area_entrega(cep):
    """
    Verifica se o CEP está na área de entrega
    Recife (CEPs começando com 5) está na área de entrega
    """
    cep_numeros = re.sub(r'[^0-9]', '', cep)
    
    # CEPs de Recife começam com 5 (50000-000 a 54999-999)
    # Vamos aceitar também CEPs próximos (50-54)
    primeiro_digito = cep_numeros[0]
    dois_primeiros = cep_numeros[:2]
    
    # Recife e região metropolitana
    if primeiro_digito == '5' and dois_primeiros in ['50', '51', '52', '53', '54']:
        return True, "Área de entrega disponível"
    else:
        return False, "Entrega não disponível para este endereço. Escolha retirada na loja."


def calcular_frete(cep):
    """
    Calcula o custo de frete baseado no CEP
    Recife tem frete fixo de R$ 15,00
    """
    cep_numeros = re.sub(r'[^0-9]', '', cep)
    dois_primeiros = cep_numeros[:2]
    
    # Recife e região metropolitana - frete fixo
    if dois_primeiros in ['50', '51', '52', '53', '54']:
        return Decimal('15.00')
    
    # Outros CEPs (caso sejam aceitos no futuro)
    return Decimal('25.00')


def calcular_prazo_entrega(cep):
    """
    Calcula prazo de entrega em dias úteis baseado no CEP
    Recife: 2-3 dias úteis
    """
    cep_numeros = re.sub(r'[^0-9]', '', cep)
    dois_primeiros = cep_numeros[:2]
    
    # Recife centro (50, 51) - 2 dias
    if dois_primeiros in ['50', '51']:
        return 2
    
    # Recife outras áreas e região metropolitana (52, 53, 54) - 3 dias
    if dois_primeiros in ['52', '53', '54']:
        return 3
    
    # Outros (caso sejam aceitos no futuro)
    return 5
