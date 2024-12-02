import os
from openai import OpenAI
import openai
from .utils import Video_Dataset
import json
import logging
from tenacity import retry, stop_after_attempt, wait_random_exponential

@retry(wait=wait_random_exponential(min=1, max=60), stop=stop_after_attempt(6))
def call_api(client, messages, model):
    """调用 OpenAI API 的函数，包含重试机制"""
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=0
    )
    return response.choices[0].message.content

def chat(config, prompt, dimension):
    """
    Evaluate videos using OpenAI API
    Args:
        config: configuration dictionary
        prompt: prompt template
        dimension: evaluation dimension name
    Returns:
        dict: containing evaluation scores
    """
    # 设置日志
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    file_handler = logging.FileHandler(config[f'log_path_{dimension}'])
    formatter = logging.Formatter('%(message)s')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    client = OpenAI(
        api_key=config['api_key'],
        base_url=config['base_url']
    )
    MODEL = config['model_name']

    # 初始化结果字典
    results = {}
    
    # 加载数据集
    dataset = Video_Dataset(data_dir=config['dataset_root_path'])
    
    # 处理每个视频
    l1 = list(range(0, len(dataset)))
    for i in l1:
        try:
            logger.info(f'Processing video {i}...')
            data = dataset[i]
            frames = data['frames']
            prompten = data['prompt']
            
            # 构建消息
            messages = [
                {
                    "role": "system",
                    "content": prompt
                },
                {
                    "role": "user", "content": [
                        "These are the frames from the video.The prompt is '{}'.".format(prompten),
                        "12 frames from cogvideox5b \n ", 
                        *map(lambda x: {"type": "image_url", 
                                        "image_url": {"url": f'data:image/jpg;base64,{x}', "detail": "low"}}, frames['cogvideox5b']),
                        "10 frames from kling \n ", 
                        *map(lambda x: {"type": "image_url", 
                                        "image_url": {"url": f'data:image/jpg;base64,{x}', "detail": "low"}}, frames['kling']),
                        "20 frames from gen3 \n ", 
                        *map(lambda x: {"type": "image_url", 
                                        "image_url": {"url": f'data:image/jpg;base64,{x}', "detail": "low"}}, frames['gen3']),
                        " 4 frames from videocrafter2 \n ",
                        *map(lambda x: {"type": "image_url", 
                                        "image_url": {"url": f'data:image/jpg;base64,{x}', "detail": "low"}}, frames['videocrafter2']),   
                        "\n 7 frames from pika \n",
                        *map(lambda x: {"type": "image_url", 
                                        "image_url": {"url": f'data:image/jpg;base64,{x}', "detail": "low"}}, frames['pika']),
                        "\n 8 frames from show1\n ",
                        *map(lambda x: {"type": "image_url", 
                                        "image_url": {"url":    f'data:image/jpg;base64,{x}', "detail": "low"}}, frames['show1']),                             
                        "\n5 frames from lavie\n ",
                        *map(lambda x: {"type": "image_url", 
                                        "image_url": {"url": f'data:image/jpg;base64,{x}', "detail": "low"}},frames['lavie']),
                                                                ], 
            }
            ]

            # 调用 API 并获取结果
            response = call_api(client, messages, MODEL)
            results[str(i)] = response
            
            logger.info(f'Successfully evaluated video {i}')
            logger.debug(f'Response for video {i}: {response}')
            
        except Exception as e:
            logger.error(f'Error processing video {i}: {str(e)}')
            results[str(i)] = f'Error: {str(e)}'

    return {
        'score': results
    }