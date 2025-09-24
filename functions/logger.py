import logging
import os
from datetime import datetime

LOG_DIR = os.path.join(os.path.dirname(__file__), '..', 'logs')
os.makedirs(LOG_DIR, exist_ok=True)
LOG_FILE = os.path.join(LOG_DIR, 'auditoria.log')

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE, encoding='utf-8'),
        logging.StreamHandler()
    ]
)

def registrar_log(nivel, usuario, operacao, detalhes=None, id_obj=None):
    msg = f"usuario={usuario} operacao={operacao}"
    if id_obj is not None:
        msg += f" id={id_obj}"
    if detalhes:
        msg += f" detalhes={detalhes}"
    if nivel == 'INFO':
        logging.info(msg)
    elif nivel == 'ERROR':
        logging.error(msg)
    else:
        logging.warning(msg)
