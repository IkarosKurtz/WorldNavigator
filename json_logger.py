import os
import logging
from datetime import datetime
from logging.handlers import TimedRotatingFileHandler
from pythonjsonlogger import jsonlogger

# Crear el directorio de logs si no existe
log_dir = "./tmp"
os.makedirs(log_dir, exist_ok=True)

# Nombre base del archivo de log
log_file = os.path.join(log_dir, "application.log")

# Configurar el manejador de archivos con rotación diaria a medianoche
file_handler = TimedRotatingFileHandler(
    filename=log_file,
    when="midnight",
    interval=1,
    backupCount=30,  # Mantener logs de 30 días
    encoding="utf-8",
    utc=True
)

# Crear el formateador de logs en formato JSON


class CustomJsonFormatter(jsonlogger.JsonFormatter):
  def add_fields(self, log_record, record, message_dict):
    super().add_fields(log_record, record, message_dict)
    # Añadir timestamp en formato ISO
    log_record['timestamp'] = datetime.utcnow().isoformat()
    log_record['level'] = record.levelname
    # Añadir información de módulo y línea
    log_record['module'] = record.module
    log_record['lineno'] = record.lineno


# Configurar el formateador
formatter = CustomJsonFormatter(
    '%(message)s %(level)s %(timestamp)s %(name)s %(module)s %(lineno)s',
    json_indent=2
)
file_handler.setFormatter(formatter)

# Configurar logger raíz
logger = logging.getLogger()
logger.setLevel(logging.INFO)
logger.addHandler(file_handler)

# Función para obtener un logger específico


def get_logger(name):
  return logging.getLogger(name)
