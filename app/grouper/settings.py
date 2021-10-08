import argparse
import os
import pathlib

from trafaret_config import commandline

from grouper.utils import TRAFARET


BASE_DIR = pathlib.Path(__file__).parent
DEFAULT_CONFIG_PATH = BASE_DIR / 'config/grouper.yaml'


REDIS_HOST = os.environ.get('REDIS_HOST', 'localhost')
REDIS_PORT = os.environ.get('REDIS_PORT', 6379)


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
