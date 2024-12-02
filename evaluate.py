
import os
from HAbench import HABench
from datetime import datetime
import argparse
import json

def parse_args():

    CUR_DIR = os.path.dirname(os.path.abspath(__file__))
    parser = argparse.ArgumentParser(description='HABench', formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument(
        "--output_path",
        type=str,
        default='./evaluation_results/',
        help="output path to save the evaluation results",
    )
    parser.add_argument(
        "--config_path",
        type=str,
        default='./config.json',
        help="path to the config file",
    )
    parser.add_argument(
        "--full_json_dir",
        type=str,
        default=f'{CUR_DIR}/HAbench/HABench_full_info.json',
        help="path to save the json file that contains the prompt and dimension information",
    )
    parser.add_argument(
        "--videos_path",
        type=str,
        required=True,
        help="folder that contains the sampled videos",
    )
    parser.add_argument(
        "--dimension",
        nargs='+',
        required=True,
        help="list of evaluation dimensions, usage: --dimension <dim_1> <dim_2>",
    )
    args = parser.parse_args()
    return args


def main():
    args = parse_args()
    HAVBench = HABench(args.full_json_dir, args.output_path, args.config_path)

    current_time = datetime.now().strftime('%Y-%m-%d-%H:%M:%S')

    kwargs = {}

    dimension_str = args.dimension[0]
    last_part = os.path.basename(args.videos_path)
    HAVBench.evaluate(
        videos_path = args.videos_path,
        #name = f'results_{current_time}',
        name = f'results_{dimension_str}_{last_part}',
        dimension_list = args.dimension,
        **kwargs
    )
    print('done')


if __name__ == "__main__":
    main()
