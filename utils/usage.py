import configparser
import os

IA_INI_FILE = "ia.ini"

def read_ia_file():
    """
    Lê os valores atuais do arquivo ia.ini.
    """
    if not os.path.exists(IA_INI_FILE):
        initialize_ia_file()

    config = configparser.ConfigParser()
    config.read(IA_INI_FILE)

    # Converte os valores para inteiros ou floats
    ncm = float(config['USAGE']['ncm'])
    ia = float(config['USAGE']['ia'])

    return {'ncm': ncm, 'ia': ia}

def initialize_ia_file():
    """
    Inicializa o arquivo ia.ini com valores iniciais.
    """
    config = configparser.ConfigParser()
    config['USAGE'] = {
        'ncm': '0',
        'ia': '0'
    }
    with open(IA_INI_FILE, 'w') as configfile:
        config.write(configfile)
    print(f"Arquivo {IA_INI_FILE} criado com valores iniciais.")

def update_ncm_usage(ncm_increment):
    """
    Atualiza os valores de ncm no arquivo ia.ini.
    """
    current_usage = read_ia_file()
    new_ncm = current_usage['ncm'] + ncm_increment

    # Atualiza o arquivo
    config = configparser.ConfigParser()
    config['USAGE'] = {
        'ncm': str(new_ncm),
        'ia': str(current_usage['ia'])
    }
    with open(IA_INI_FILE, 'w') as configfile:
        config.write(configfile)

    print(f"NCM atualizado: ncm={new_ncm}")

def update_ia_usage(ia_increment):
    """
    Atualiza os valores de ia no arquivo ia.ini.
    """
    current_usage = read_ia_file()
    new_ia = current_usage['ia'] + ia_increment

    # Atualiza o arquivo
    config = configparser.ConfigParser()
    config['USAGE'] = {
        'ncm': str(current_usage['ncm']),
        'ia': str(new_ia)
    }
    with open(IA_INI_FILE, 'w') as configfile:
        config.write(configfile)

    print(f"IA atualizado: ia={new_ia}")
