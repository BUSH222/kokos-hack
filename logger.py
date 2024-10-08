'''
- Debug (10): самый низкий уровень логирования, предназначенный для отладочных сообщений, для вывода диагностической
информации о приложении.

- Info (20): этот уровень предназначен для вывода данных о фрагментах кода, работающих так, как ожидается.

- Warning (30): этот уровень логирования предусматривает вывод предупреждений, он применяется для записи сведений о
событиях, на которые программист обычно обращает внимание. Такие события вполне могут привести к проблемам при работе
приложения. Если явно не задать уровень логирования — по умолчанию используется именно warning.

- Error (40): этот уровень логирования предусматривает вывод сведений об ошибках — о том, что часть приложения работает
не так как ожидается, о том, что программа не смогла правильно выполниться.

- Critical (50): этот уровень используется для вывода сведений об очень серьёзных ошибках, наличие которых угрожает
нормальному функционированию всего приложения. Если не исправить такую ошибку — это может привести к тому, что
приложение прекратит работу.
'''

import logging
from dbloader import connect_to_db

conn, cur = connect_to_db()


def setup_custom_logger(name):
    debug_format_string = '%(asctime)s - %(levelname)s \n' \
                          '%(message)s \n'

    debug_formatter = logging.Formatter(debug_format_string)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    console_handler.setFormatter(debug_formatter)

    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    logger.addHandler(console_handler)
    return logger


custom_logger = setup_custom_logger('combined')


def log_event(event_description: str, log_level=logging.DEBUG, **kwargs) -> None:
    full_event_description = event_description if not kwargs else event_description + '\n' + str(kwargs)
    try:
        cur.execute("INSERT INTO logs (log_time, log_text) VALUES (NOW(), %s);", (event_description, ))
        conn.commit()
        custom_logger.log(log_level, full_event_description)
    except Exception as e:
        conn.rollback()
        print(f"ERROR CREATING LOG, full error: {e}")
