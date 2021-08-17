import argparse
import pathlib

from trafaret_config import commandline

from app.grouper.utils import TRAFARET


BASE_DIR = pathlib.Path(__file__).parent
DEFAULT_CONFIG_PATH = BASE_DIR / 'config/grouper.yaml'


def get_config(argv=None):
    arg_parser = argparse.ArgumentParser()
    commandline.standard_argparse_options(
        arg_parser,
        default_config=DEFAULT_CONFIG_PATH
    )

    # ignore unknown options
    options, unknown = arg_parser.parse_known_args(argv)
    config = commandline.config_from_options(options, TRAFARET)

    return config
