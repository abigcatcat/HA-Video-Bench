import os
from openai import OpenAI
import openai
from .utils import Video_Dataset
import json
import logging
from tenacity import retry, stop_after_attempt, wait_random_exponential


def eval(config, prompt,dimension):
    # 设置日志
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    file_handler = logging.FileHandler(config[f'log_path_{dimension}'])
    formatter = logging.Formatter('%(message)s')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    client = OpenAI(
        api_key="",
        base_url=""
    )

    MODEL="gpt-4o-2024-08-06"
    models = ['cogvideox5b','gen3','kling','videocrafter2','pika','show1','lavie']

    dataset = Video_Dataset(data_dir=config['dataset_root_path'])
    results = {}    # 存储最终评分结果
    
    l1 = list(range(0, len(dataset)))
    for i in l1:
        logger.info(f'>>>>>>>>This is the {i} round>>>>>>>')
        data = dataset[i]
        results[i] = {}
        
        for model in models:
            try:
                modelname = model
                examplemodels = [x for x in models if x != modelname]
                frames = data['frames']
                prompten = data['prompt']

                messages=[
                    {
                        "role": "system", 
                        "content": prompt
                    },
                    {
                        "role": "user", 
                        "content":[
                            "According to **Important Notes** in system meassage, there are examples from other models.\n",
                            *[item for examplemodel in examplemodels for item in [
                                "This example is from model {} \n".format(examplemodels.index(examplemodel)+1),
                                {"type": "image_url", "image_url": {"url": f'data:image/jpg;base64,{frames[examplemodel][0]}', "detail": "low"}}
                            ]],              
                            
                            "These are the frames from the video you are evaluating. \n",
                            *map(lambda x: {"type": "image_url", 
                                "image_url": {"url": f'data:image/jpg;base64,{x}', "detail": "low"}},frames[modelname]),    

                            "Assuming there are a video ' scoring 'x',provide your analysis and explanation in the output format as follows:\n"
                            "- video: x ,because ..."
                        ],
                    }
                ]

                # 调用API获取响应
                response = client.chat.completions.create(
                    model=MODEL,
                    messages=messages,
                    temperature=0
                )
                response_content = response.choices[0].message.content
                
                # 记录评估结果
                results[i][modelname] = response_content      # 可以根据需要提取分数部分
                
                logger.info(f'>>>>>>>Model {modelname} evaluation:\n{response_content}')

            except Exception as e:
                logger.error(f'Error evaluating model {modelname}: {str(e)}')
                results[i][modelname] = 'Error'

    # 返回符合主类期望的结构
    return {
        'score': results             # 评分结果
    }