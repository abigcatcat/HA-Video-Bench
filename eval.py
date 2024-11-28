import os
import json
import argparse

def build_info_json(model2eval=None,dimension2eval=None, json_file_path='HABench_full.json'):
    model2eval = model2eval
    dimension = dimension2eval
    prompt4dimension = []



    models = ['cogvideox5b', 'gen3', 'kling', 'videocrafter2', 'pika', 'show1', 'lavie']

    if model2eval != None and model2eval not in models:
        models.append(model2eval)
    

    dimension4data = {
        "temporal_consistency": "action",
        "aesthetic_quality": "overall_consistency",
        "imaging_quality": "overall_consistency",
        "motion_effects": "action",
        "object_class": "object_class",
        "color": "color",
        "scene": "scene",
        "action": "action",
        "event_order": "event_order",
        "overall_consistency": "overall_consistency"
    }

    # Load the prompts from the JSON file
    with open(json_file_path, 'r') as f:
        prompt4dimension = json.load(f)

    result = {}

    # Process each dimension
    dim4data = dimension4data[dimension]
    jsonlist = []

    for prompt in prompt4dimension:
        if prompt['dimension'] != dim4data:
            continue
        else:
            for videos4prompt in range(0, 3):
                meta_dict = {
                    "prompt_en": "prompt",
                    "videos": {},
                }
                meta_dict['prompt_en'] = prompt['prompt']
                for model in models:
                    video_filename = f"{dim4data}/{model}/{prompt['prompt']}_{videos4prompt}.mp4"
                    meta_dict['videos'][model] = video_filename
                jsonlist.append(meta_dict)

    result[dimension] = jsonlist

    return result


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Arguments for the evaluation script.")
    parser.add_argument('--model', type=str, default=None, help='Video generation model name you want to evaluate.',required=True)
    parser.add_argument('--dimension', type=str, default=None, help='Dimension you want to evaluate.',required=True)

    args = parser.parse_args()

    result = build_info_json(model2eval=args.model,dimension2eval=args.dimension)