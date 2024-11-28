import os
from openai import OpenAI
import openai
from tool import videoreader
import json


def build_info_json

# 创建一个OpenAI客户端实例
client = OpenAI(
    api_key="",
    base_url=""  # 替换为你的自定义API域
)

## Set the API key and model name
MODEL="gpt-4o-2024-08-06"
models = ['cogvideox5b','gen3','kling','videocrafter2','pika','show1','lavie']

dimension = 'imaging_quality'
from PromptTemplate4GPTeval import Prompt4ImagingQuality
prompt_template = Prompt4ImagingQuality


data_prepath = ''
with open("./Human_anno/{}.json".format(dimension)) as f:
    human_anno = json.load(f)




    requests = []
    for model in  models:
        modelname = model
        examplemodels = [x for x in models if x != modelname]
        frames = videoreader.process_video(data_prepath,human_anno[i]['videos'],1)


        prompten = human_anno[i]['prompt_en']
        # question = human_anno[i]['question_en']
        # subject = human_anno[i]['subject_en']
        # scene = human_anno[i]['scene_en']
        # objet = human_anno[i]['object']
        messages=[
        {
        "role": "system", "content":
            prompt_template
            }
            ,
        {
            "role": "user", "content":[
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