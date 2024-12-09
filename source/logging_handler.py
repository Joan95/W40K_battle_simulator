import logging
import re


class RemoveAnsiEscapeCodesFilter(logging.Filter):
    ansi_escape = re.compile(r'\x1B[@-_][0-?]*[ -/]*[@-~]')

    def filter(self, record):
        record.msg = self.ansi_escape.sub('', record.msg)
        return True


# Initialize logging to a file
logging.basicConfig(filename='game.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Create and add the filter
remove_ansi_filter = RemoveAnsiEscapeCodesFilter()
logging.getLogger().addFilter(remove_ansi_filter)


def log(message, print_message=False):
    logging.info(message)
    if print_message:
        print(message)


def set_logging_level(level):
    logging.getLogger().setLevel(level)