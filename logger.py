from settings_loader import settings
import logging

'''
Debug (10): самый низкий уровень логирования, предназначенный для отладочных сообщений, для вывода диагностической информации о приложении.

Info (20): этот уровень предназначен для вывода данных о фрагментах кода, работающих так, как ожидается.

Warning (30): этот уровень логирования предусматривает вывод предупреждений, он применяется для записи сведений о событиях, на которые программист обычно обращает внимание. Такие события вполне могут привести к проблемам при работе приложения. Если явно не задать уровень логирования — по умолчанию используется именно warning.

Error (40): этот уровень логирования предусматривает вывод сведений об ошибках — о том, что часть приложения работает не так как ожидается, о том, что программа не смогла правильно выполниться.

Critical (50): этот уровень используется для вывода сведений об очень серьёзных ошибках, наличие которых угрожает нормальному функционированию всего приложения. Если не исправить такую ошибку — это может привести к тому, что приложение прекратит работу.
'''


def setup_custom_logger(name):
    debug_format_string = '%(asctime)s - %(levelname)s \n' \
                          '%(message)s \n'

    debug_formatter = logging.Formatter(debug_format_string)

    debug_file_handler = logging.FileHandler(settings['debug_log_file_path'], encoding='utf-8')
    debug_file_handler.setLevel(logging.DEBUG)
    debug_file_handler.setFormatter(debug_formatter)

    errors_file_handler = logging.FileHandler(settings['errors_log_file_path'], encoding='utf-8')
    errors_file_handler.setLevel(logging.ERROR)
    errors_file_handler.setFormatter(debug_formatter)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    console_handler.setFormatter(debug_formatter)

    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    logger.addHandler(debug_file_handler)
    logger.addHandler(errors_file_handler)
    logger.addHandler(console_handler)

    return logger


custom_logger = setup_custom_logger('combined')


def log_event(event_description: str, log_level=logging.DEBUG, **kwargs) -> None:
    full_event_description = event_description if not kwargs else event_description + '\n' + str(kwargs)
    # print(full_event_description)
    custom_logger.log(log_level, full_event_description)
    # errors_logger.log(log_level, full_event_description)
