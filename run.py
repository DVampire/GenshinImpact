import sys
import warnings

warnings.filterwarnings('ignore')
import argparse
import asyncio
import os
import pathlib

from dotenv import load_dotenv
from mmengine import DictAction

load_dotenv(verbose=True)

root = str(pathlib.Path(__file__).resolve().parents[0])
sys.path.append(root)

from crawler.config import build_config
from crawler.core import Crawler
from crawler.utils.file_utils import assemble_project_path


def get_args_parser():
    parser = argparse.ArgumentParser(description='Crawler')
    parser.add_argument(
        '--config', default=os.path.join('configs', 'exp.py'), help='Config file path'
    )
    parser.add_argument(
        '--cfg-options',
        nargs='+',
        action=DictAction,
        help='override some settings in the used config, the key-value pair '
        'in xxx=yyy format will be merged into config file. If the value to '
        'be overwritten is a list, it should be like key="[a,b]" or key=a,b '
        'It also allows nested list/tuple values, e.g. key="[(a,b),(c,d)]" '
        'Note that the quotation marks are necessary and that no white space '
        'is allowed.',
    )

    parser.add_argument('--workdir', type=str, default='workdir')
    parser.add_argument('--tag', type=str, default=None)
    parser.add_argument('--exp-path', type=str, default=None)
    parser.add_argument('--if_remove', action='store_true', default=False)

    return parser


async def main(args):
    # 1. build config
    config = build_config(assemble_project_path(args.config), args)

    # 2. init crawler
    crawler = Crawler(config=config)
    await crawler.start()


if __name__ == '__main__':
    parser = get_args_parser()
    args = parser.parse_args()
    try:
        asyncio.get_event_loop().run_until_complete(main(args))
    except KeyboardInterrupt:
        sys.exit()
