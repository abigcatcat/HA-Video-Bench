import os
from openai import OpenAI
import openai
from tool import videoreader
import json
# 创建一个OpenAI客户端实例
client = OpenAI(
    api_key="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",
    base_url="https://gateway.ai.cloudflare.com/v1/627f1b1f372e3a198dc32573bbc6f720/openai-gpt/openai"  # 替换为你的自定义API域
)

## Set the API key and model name
MODEL="gpt-4o-2024-08-06"

dimension = 'aesthetic_quality'
from PromptTemplate4GPTeval import Prompt4AestheticQuality
prompt_template = Prompt4AestheticQuality


import json
# data_prepath = r'D:\Astudying\VideoEval\data4dimensions'
data_prepath = "../../data4dimensions/"
with open("./Human_anno/{}.json".format(dimension)) as f:
    human_anno = json.load(f)

file_path ="./GPT4o_eval_results/{}/{}_llmeval.json".format(dimension,dimension)

with open(file_path,'r') as f:
    s = json.load(f)

l1 = [int(i) for i in ['161', '182']]
# l2 = list(range(2,len(human_anno),3))
l = l1

# skip_index = list(range(0, len(human_anno),5))
for i in l:             
    # if i in skip_index:
    #     continue
    # # frames = videoreader.process_video(data_dir,human_anno[i]['videos'],4 )
    # else:
        frames = videoreader.process_video(data_prepath,human_anno[i]['videos'],2 ,resize_fx=1,resize_fy=1)
        prompten = human_anno[i]['prompt_en']
        # question = human_anno[i]['question_en']
        # subject = human_anno[i]['subject_en']
        # scene = human_anno[i]['scene_en']
        # objet = human_anno[i]['object']
        try:
            response = client.chat.completions.create(
            model=MODEL, 
            messages=[
            {
            "role": "system", "content":
             prompt_template
             }
             ,
            {
                "role": "user", "content": [
                "These are the frames from the video.The prompt is '{}'.".format(prompten),
                "12 frames from cogvideox5b \n ", 
                *map(lambda x: {"type": "image_url", 
                                "image_url": {"url": f'data:image/jpg;base64,{x}', "detail": "low"}}, frames['cogvideox5b']),
                "10 frames from kling \n ", 
                *map(lambda x: {"type": "image_url", 
                                "image_url": {"url": f'data:image/jpg;base64,{x}', "detail": "low"}}, frames['kling']),
                "10 frames from gen3 \n ", 
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
            ],
            temperature=0,
            )
            print(response.choices[0].message.content) 
            s[str(i)] = response.choices[0].message.content.replace('\n\n','\n')
        except Exception as e:
            print(f"An error occurred: {e}")
            s[i] = 'Error'

import json
# 使用 json 保存字典
with open(file_path, "w") as f:
    json.dump(s, f,indent=4)