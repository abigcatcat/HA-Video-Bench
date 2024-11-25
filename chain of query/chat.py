import os
from typing import List, Dict, Any
from tqdm import tqdm
os.environ["TOKENIZERS_PARALLELISM"] = "false"
import re
import json
import yaml
import logging
import tenacity
from tenacity import retry, stop_after_attempt, wait_random_exponential
from torch.utils.data import DataLoader
from openai import OpenAI
from openai import AzureOpenAI
from load_dataset import *

class Agent():
    def __init__(self, agent, logger, prompt, config) -> None:
        """
        initialize agents, including functions that initiate chats and mllm calling
        agents: list of strings, each string is the name of an agent
        logger: logger object
        prompt: dict, system prompt, user prompt, and summary prompt
        config: dict, configurations
        """
        self.agent = agent
        self.logger = logger
        self.prompt = prompt
        self.config = config

        self.yaml_log = []
        self.history = []
        self.qa_history = []
        self.messages = []
        self.messages_text =[]
        #self.video_path = ''
        self.video_prompt=''
        self.frames = []
        self.completion_tokens = 0
        self.prompt_tokens = 0

        # openai configurations
        self.api_key = " "
        self.base_url = " "
        self.model = "gpt-4o-mini"

    # reset everything, avoid initializing too many classes
    def reset(self):
        self.messages = []
        self.messages_text = []
        self.yaml_log = []
        self.history = []
        self.qa_history = []
        self.frames=[]
        self.video_prompt = ''

        #self.video_path = ''

        self.completion_tokens = 0
        self.prompt_tokens = 0

    @tenacity.retry(wait=tenacity.wait_exponential(max=60),
                    stop=tenacity.stop_after_attempt(5),
                    retry=tenacity.retry_if_exception_type(TypeError),
                    reraise=True)

        # call openai, input messages, get response
    @retry(wait=wait_random_exponential(min=1, max=60), stop=stop_after_attempt(6))
    def call_oai(self, mess):
        client = OpenAI(api_key=self.api_key, base_url=self.base_url)
        response = client.chat.completions.create(
            model=self.model,
            messages=mess,
            temperature=0
        )
        completion_tokens = response.usage.completion_tokens
        prompt_tokens = response.usage.prompt_tokens

        self.completion_tokens += completion_tokens
        self.prompt_tokens += prompt_tokens

        return response.choices[0].message.content

    # def initiate_agents(self) -> None:
    #     # self.logger.info('initiating agents...')
    #     self.video_prompt=f'This is the video\'s prompt:\n{self.video_prompt}'
    #     self.messages= [{'role': 'system',
    #                     'content': self.prompt["system"]}]
    #     self.logger.info(self.video_prompt)
    # prepare message
    def prepare_message(self,agent):
        # self.logger.info('initiating agents...')
        self.video_prompt = f'This is the video\'s prompt:\n{self.video_prompt}'
        #self.logger.info(self.video_prompt)
        # if history is empty, it's the first round
        if not self.history:
            message_ = 'It\'s the first round.' + self.prompt[agent]+self.video_prompt
        # if not, get the history, and concat everything with proper format
        else:
            history_ = 'This is the discussion history:\n\n<history>\n'.join(self.history)
            message_ = self.prompt[agent]+ history_+'\n</history>\n\n'+self.video_prompt

        self.messages=[{"role": "system", "content": self.prompt['agent-system']},
            {"role": "user", "content": [
                 {"type": "text", "text":  message_},
                 {"type": "text", "text": "These are the frames from the video"},
                 {"type": "text", "text": "frames from lavie"},
                *map(lambda x: {"type": "image_url",
                                "image_url": {"url": f'data:image/jpg;base64,{x}', "detail": "low"}}, self.frames['lavie']),
                 {"type": "text", "text": "frames from videocrafter"},
                *map(lambda x: {"type": "image_url",
                                "image_url": {"url": f'data:image/jpg;base64,{x}', "detail": "low"}}, self.frames['videocraft']),
                {"type": "text", "text": "frames from modelscpoe"},
                *map(lambda x: {"type": "image_url",
                                "image_url": {"url": f'data:image/jpg;base64,{x}', "detail": "low"}}, self.frames['modelscope']),
                {"type": "text", "text": "frames from cogvideo"},
                *map(lambda x: {"type": "image_url",
                                "image_url": {"url": f'data:image/jpg;base64,{x}', "detail": "low"}}, self.frames['cogvideo'])
                ],
            }]
        #print(self.messages)
        return self.messages

    def prepare_message_text(self,agent):
        # self.logger.info('initiating agents...')
        #self.video_prompt = f'This is the video\'s prompt:\n{self.video_prompt}'
        #self.logger.info(self.video_prompt)
        # if history is empty, it's the first round
        self.video_prompt = f'This is the text prompt:\n{self.video_prompt}'
        if not self.history:
            message_ = 'It\'s the first round.' + self.prompt[agent]+self.video_prompt
        # if not, get the history, and concat everything with proper format
        else:
            #prefix = ''
            # Create a header for the history section
            history_header = "There are the detailed video descriptions of the video:\n\n"
            history_content = '\n'.join(self.history)
            #print(history_content)
            # Combine the header with the content
            history_ = history_header + "<video's description>\n" + history_content + "\n</video's description>"
            # Construct the final message with the provided prefix, history, and prompts
            message_ = self.video_prompt + '\n\n' + history_
            # history_ = 'This is the evaluation history:\n\n<evaluation history>\n'.join(self.history)
            # message_ = self.prompt[agent]+prefix+ history_+'\n</history>\n\n'+self.video_prompt
        self.messages_text=[{"role": "system", "content": self.prompt[agent]},
            {"role": "user", "content": message_+'\n\nYour questions must be deisplayed in the format: \n<question>\n[your questions] or [I have no question]\n</question>.' + '\n\nDisplay the results in the specified Output Format'}]
        #print(self.messages_text)
        return self.messages_text

    # chat for one round, for each agent, get response, call mllm to get answer if needed, and store the history
    # return True means ealy ending, will return chat_for_n_rounds also
    def chat_for_one_round(self, agent) -> str:
        self.logger.info(f'-----Agent:{agent}-----')
        message = self.prepare_message(agent)
        #print(message)
        response = self.call_oai(message)
        #self.history.append(response)
        self.logger.info(f'Round of {agent}:{response}')
        print("the response is :",response)
        print("=============================================")
        print("self.history is :",self.history)
        return response

    def chat_for_one_round_text(self, agent) -> str:
        self.logger.info(f'-----Agent:{agent}-----')
        message = self.prepare_message_text(agent)
        #print(message)
        response = self.call_oai(message)
        #self.history.append(response)
        self.logger.info(f'Round of {agent}:{response}')
        # print("the response is :",response)
        # print("=============================================")
        # print("self.history is :",self.history)
        return response

    def check_score(self, final_result):
        self.logger.info('-----scorechecker------')
        header = "This is the assigned score by the AI model:\n"
        #history_content = '\n'.join(self.history)
        score = header + "<AI model's score>\n" + final_result + "\n</AI model's score>"
        # Construct the final message with the provided prefix, history, and prompts
        message_ = self.video_prompt + '\n\n' + score
        messages = [{"role": "system", "content": self.prompt['scorechecker']},
                              {"role": "user",
                               "content": message_}]
        response = self.call_oai(messages)
        return response

    # Loop chat_for_one_round for n times
    def chat_for_n_rounds(self, n):
        for i in range(n):
            if self.chat_for_one_round():  # if True, means early ending (patter not found or TERMINATE), return
                return

# summarize the conversation and get the results

class Host():
    def __init__(self, name: str, logger, prompt, config, modelname,modelmessage,agents: List[Agent]):
        self.name = name
        self.agents = agents
        self.logger = logger
        self.prompt = prompt
        self.config = config
        self.modelname = modelname
        self.modelmessage = modelmessage
        self.video_prompt=" "
        self.frames=[]
        self.history = []
        self.qa_history = []
        self.description = ''
        # self.video_description = ''
        self.api_key = " "
        self.base_url = " "

        self.model = "gpt-4o-2024-08-06"
        self.completion_tokens = 0
        self.prompt_tokens = 0

    def reset(self):
        #self.messages = {}
        self.yaml_log = []
        self.history = []
        self.qa_history = []
        self.frames=[]
        self.video_prompt = " "
        self.description = ''
        self.messages = []

        #self.video_path = ''

        self.completion_tokens = 0
        self.prompt_tokens = 0
    def call_oai(self, mess):
        client = OpenAI(api_key=self.api_key, base_url=self.base_url)
        # client = AzureOpenAI(api_key=self.api_key, api_version=self.api_version, azure_endpoint=self.azure_endpoint)
        response = client.chat.completions.create(
            model=self.model,
            messages=mess,
            temperature=0
        )
        completion_tokens = response.usage.completion_tokens
        prompt_tokens = response.usage.prompt_tokens

        self.completion_tokens += completion_tokens
        self.prompt_tokens += prompt_tokens

        return response.choices[0].message.content

    def initial_result(self):
        self.video_prompt = f'This is the text prompt:\n{self.video_prompt}'
        # history_header = "This is their all evaluation history:\n\n"
        # history_content = '\n'.join(self.history)
        # print(history_content)
        # # Combine the header with the content
        # history_ = history_header + "< evaluation history>\n" + history_content + "\n</evaluation history>"
        # history_ = 'This is the their evaluation history:\n\n<history>\n'.join(self.history)
        message_ = "You must think following the 'Evaluation Steps' one by one.\n"
        self.messages = [{"role": "system", "content": self.prompt['gpt4o-system']},
                         {"role": "user", "content": [
                             {"type": "text", "text": message_},
                             {"type": "text", "text": '\n\nThese are the frames from the video generated by {}\n'.format(self.modelname)},
                             {"type": "text", "text": self.modelmessage},
                             *map(lambda x: {"type": "image_url",
                                             "image_url": {"url": f'data:image/jpg;base64,{x}', "detail": "low"}},
                                  self.frames[self.modelname])
                             # {"type": "text", "text": "frames from videocrafter"},
                             # *map(lambda x: {"type": "image_url",
                             #                 "image_url": {"url": f'data:image/jpg;base64,{x}', "detail": "low"}},
                             #      self.frames['videocraft']),
                             # {"type": "text", "text": "frames from modelscpoe"},
                             # *map(lambda x: {"type": "image_url",
                             #                 "image_url": {"url": f'data:image/jpg;base64,{x}', "detail": "low"}},
                             #      self.frames['modelscope']),
                             # {"type": "text", "text": "frames from cogvideo"},
                             # *map(lambda x: {"type": "image_url",
                             #                 "image_url": {"url": f'data:image/jpg;base64,{x}', "detail": "low"}},
                             #      self.frames['cogvideo'])
                         ]}]
        # print(messages)
        self.logger.info('==============initial response============')
        response = self.call_oai(self.messages)
        match = re.search(r'\[Video Description\]:\s*(.*)', response, re.DOTALL)
        if match:
            video_description = match.group(1).strip()
        #match = re.search(r'\[Video Description\]:\s*(.*?)(?=\[Evaluation Result\]|\Z)', response, re.DOTALL)
            self.history.append(f"This is the initial information: \n{video_description}\n\n")
        else:
            self.logger.warning("No video captured Description")
            video_description = "No video captured Description"
            self.history.append(f"This is the initial information: \n{video_description}\n\n")
        self.description = f'This is the video\'s initial description:\n<description>\n{response}\n</description>'
        # self.video_description = f'This is the video\'s initial description:\n<description>\n{video_description}\n</description>'
        #else:
        #    print('Something went wrong')
        return response

    def get_question(self, response):
        pattern = r"\[Your questions?\]:\s*(.*)"

        # 搜索并提取 [Your question]: 或 [Your questions]: 后的内容
        result = re.search(pattern, response, re.DOTALL)

        if result:
            # 提取 [Your question]: 或 [Your questions]: 后面的所有内容
            question = result.group(1).strip()
            return question
        else:
            # 如果没有匹配到 [Your question]: 或 [Your questions]:，返回 None
            return None

    def question(self) :

        #all_histories = []

        # 1. 各智能体独立获得响应并添加到各自的历史记录中
        self.logger.info('==============agent qa_history============')
        # 2. 按顺序让每个智能体基于当前的历史记录做出回答
        #self.logger.info('==============reflect============')
        for i, agent in enumerate(self.agents):
            #combined_history = "\n".join(self.description)
            #print(combined_history)
            agent.history.append(self.description)
            #print(agent.history)
            response = agent.chat_for_one_round_text(agent.agent)
            question = self.get_question(response)
            self.qa_history.append(f"This is the question of the {agent.agent}: {question}\n")
            #self.history.append("There are the feedback from assistants.\n")
            #self.history.append(f"This is the question of the {agent.agent}: {question}\n")
            self.description = self.description+f'\nThis is a question of another assistant:\n<question-one>\n{question}\n</question-one>'

        return self.qa_history

    def answer(self):
        #self.video_prompt = f'This is the text prompt:\n{self.video_prompt}'
        # history_header = "This is their all evaluation history:\n\n"
        # history_content = '\n'.join(self.history)
        # print(history_content)
        # # Combine the header with the content
        # history_ = history_header + "< evaluation history>\n" + history_content + "\n</evaluation history>"
        # history_ = 'This is the their evaluation history:\n\n<history>\n'.join(self.history)
        #message_ = "You must think following the 'Evaluation Steps' one by one.\n" + self.video_prompt
        qa_history_header = '\n\nThere are the questions of two assistants:\n\n'
        qa_history_content = '\n'.join(self.qa_history)
        qa_history = qa_history_header + "<qa_history>\n" + qa_history_content + "\n</qa_history>\n"
        #print(qa_history)
        self.messages = [{"role": "system", "content":self.prompt['gpt4o-answer']},
                         {"role": "user", "content": [
                             {"type": "text", "text": self.video_prompt},
                             {"type": "text", "text": qa_history},
                             {"type": "text", "text": 'These are the frames from the video generated by {}\n'.format(self.modelname)},
                             # {"type": "text", "text": f"{self.modelmessage}; Please carefully observe whether the actions required by the text prompt appear in the video\n"},
                             {"type": "text", "text": f"{self.modelmessage}\n"},
                             *map(lambda x: {"type": "image_url",
                                             "image_url": {"url": f'data:image/jpg;base64,{x}', "detail": "low"}},
                                  self.frames[self.modelname])
                             # {"type": "text", "text": "frames from videocrafter"},
                             # *map(lambda x: {"type": "image_url",
                             #                 "image_url": {"url": f'data:image/jpg;base64,{x}', "detail": "low"}},
                             #      self.frames['videocraft']),
                             # {"type": "text", "text": "frames from modelscpoe"},
                             # *map(lambda x: {"type": "image_url",
                             #                 "image_url": {"url": f'data:image/jpg;base64,{x}', "detail": "low"}},
                             #      self.frames['modelscope']),
                             # {"type": "text", "text": "frames from cogvideo"},
                             # *map(lambda x: {"type": "image_url",
                             #                 "image_url": {"url": f'data:image/jpg;base64,{x}', "detail": "low"}},
                             #      self.frames['cogvideo'])
                         ]}]
        # print(messages)
        self.logger.info('==============qa_history============')
        response = self.call_oai(self.messages)
        match = re.search(r'\[Descriptions\]:(.*?)\[Answers\]', response, re.DOTALL)
        if match:
            description = match.group(1).strip()  # 提取匹配的内容并去除首尾空格
        else:
            print("No information found.")
        self.qa_history.append(f"\nThis is the answer of the questions: {response}\n\n")
        self.history.append(f"\nThis is the second information: {description}")
        #self.logger.info(f'>>>>>>>>>>qa_history:\n' + self.qa_history)
        return response
    def summarize_and_get_results(self) -> str:
        self.logger.info('==============final evaluation results============')
        #self.video_prompt = f'This is the text prompt:\n{self.video_prompt}\n'
        history_header = "There are the two informations:\n"
        history_content = '\n'.join(self.history)
        #print(history_content)
        # Combine the header with the content
        history_ = history_header + "<history>\n" + history_content + "\n</history>"
        #history_ = 'This is the their evaluation history:\n\n<history>\n'.join(self.history)
        message_ = "You must think following the 'evaluation steps' one by one.\n\n" + history_ + '\n\n' + self.video_prompt+'\n\n'
        self.messages = [{"role": "system", "content": self.prompt['summer-system']},
                         {"role": "user", "content":[
                             {"type": "text", "text": message_},
                             {"type": "text", "text": f"{self.modelmessage}\n"},
                             *map(lambda x: {"type": "image_url",
                                             "image_url": {"url": f'data:image/jpg;base64,{x}', "detail": "low"}},
                                  self.frames[self.modelname]),
                             {"type": "text", "text": 'The name of the AI medel is {}\n'.format(self.modelname)}
                         ]
                            }]
        #print(messages)
        response = self.call_oai(self.messages)
        return response


def chat(config, prompt):
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    file_handler = logging.FileHandler(config['log_path_color-1'])
    formatter = logging.Formatter('%(message)s')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # load data
    dataset = Video_Dataset(data_dir=config['dataset_root_path'])
    # print(type(dataset))
    # print(len(dataset))
    # print(dataset)
    # batch_size = 1
    # data_loader = DataLoader(data, batch_size=batch_size, shuffle=False, drop_last=False)

    # initiate agents, add more if needed
    # agents = [Agent('Assistant-one', logger, prompt, config), Agent('Assistant-two', logger, prompt, config)]
    # host = Host('Host', logger, prompt, config, agents)

    result_dict = {'id': [], 'gt_label': [], 'pred_label': [], 'text': [], 'error': []}
    #
    index = 0
    s = dict()
    des = dict()
    history = {}
    #for data in dataset[57:]:
    #for i in range(0, len(dataset)):
    l1 = list(range(0, len(dataset), 3))
    #l1 = [84]
    #for i in range(2, len(dataset)):
    for i in l1:
        data=dataset[i]
        # for agent in agents:
        #     # agent.video_path = batch['img_path'][0]
        #     # agent.video_prompt = batch['prompt'][0]
        #     #agent.frames = data['frames']
        #     agent.video_prompt = data['prompt']
        # host.video_prompt = data['prompt']
        # host.frames = data['frames']
        model2message = {
             'lavie': "5 frames from lavie.",
             'pika': "7 frames from pika.",
             'show1': "8 frames from show1.",
             'videocrafter2': "4 frames from videocrafter2.",
              'cogvideox5b': "12 frames from cogvideox5b. ",
             'kling': "10 frames from kling." ,
             'gen3': "20 frames from gen3.",
        }
        for key, value in model2message.items():
            modelname = key
            modelmessage = value
            agents = [Agent('Assistant-one', logger, prompt, config), Agent('Assistant-two', logger, prompt, config)]
            host = Host('Host', logger, prompt, config, modelname, modelmessage, agents)
            for agent in agents:
                # agent.video_path = batch['img_path'][0]
                # agent.video_prompt = batch['prompt'][0]
                # agent.frames = data['frames']
                agent.video_prompt = data['prompt']
            host.video_prompt = data['prompt']
            host.frames = data['frames']
        # id = batch['id'][0]
        # gt_label = int(batch['label'][0])
            logger.info(f'>>>>>>>>This is the {index} round>>>>>>>')
            try:

                # for agent in agents:
                #     agent.prepare_message(agent.agent)
                # 主持人收集结果
                init_response = host.initial_result()
                logger.info(f'>>>>>>>>>>initial response:\n{init_response}')
                questions = host.question()
                #print(questions)
                logger.info(f'>>>>>>>>>>questions:\n{questions}')
                answers = host.answer()
                logger.info(f'>>>>>>>>>>answers:\n{answers}')
                # 主持人基于评分结果和问答记录给出最终评分
                final_result = host.summarize_and_get_results()
                history[index] = {
                    'initial_response': init_response,
                    'qa_history': questions,
                    'final_result': final_result
                }
                logger.info(f'>>>>>>>the {index} round >>>>>>Discussion and judge:\n' + final_result)

                valid_start_letters = ['l', 'p', 'k', 'v', 'g', 's', 'c']
                content_des = ""
                extracted_content = ""
                #start_index = final_result.find("Evaluation Result")
                start_index = final_result.find("Updated Video Description")
                if start_index != -1:
                    # 提取 "Updated Video Description" 后面的内容
                    all_content = final_result[start_index + len("Updated Video Description"):].strip()

                    while True:
                        # 查找 "Evaluation Result" 的位置
                        eval_result_index = all_content.find("Evaluation Result")
                        if eval_result_index != -1:
                            # 提取 "Updated Video Description" 到 "Evaluation Result" 之间的内容
                            content_des = all_content[:eval_result_index].strip()

                            # 提取 "Evaluation Result" 后面的内容
                            remaining_content = all_content[eval_result_index + len("Evaluation Result"):].strip()

                            # 遍历剩余内容，找到第一个符合要求的字母
                            for a, char in enumerate(remaining_content):
                                if char.isalpha():  # 判断是否是字母
                                    # 判断是否为指定字母集合中的字母，忽略大小写
                                    if char.lower() in valid_start_letters:
                                        # 提取从第一个有效字母开始的所有内容
                                        extracted_content = remaining_content[a:].strip()
                                        break
                            else:
                                extracted_content = ""  # 如果找不到符合条件的字母

                            # 如果提取到了符合条件的内容，则输出结果并退出循环
                            if extracted_content:
                                print(extracted_content)
                                break  # 找到符合条件的结果后，退出循环
                            else:
                                # 没有找到符合条件的内容，继续查找下一个 "Evaluation Result"
                                all_content = all_content[eval_result_index + len("Evaluation Result"):].strip()
                        else:
                            print("未找到更多 'Evaluation Result' 部分")
                            break  # 没有更多 "Evaluation Result" 时，退出循环
                else:
                    print("未找到 'Updated Video Description' 部分")

                des[index] = content_des
                s[index] = extracted_content
                # score = agents[0].check_score(extracted_content)
                # logger.info(f'>>>>>>>the {index} round >>>>>>updated score:\n' + score)
                # score_content = ""
                # start_index = score.find("Updated Evaluation Result")
                # while start_index != -1:
                #     # 从 "Evaluation Result" 后开始截取内容
                #     remaining_content = score[start_index + len("Updated Evaluation Result"):].strip()
                #     # 遍历剩余内容，找到第一个字母
                #     for a, char in enumerate(remaining_content):
                #         if char.isalpha():  # 判断是否是字母
                #             # 判断是否为指定字母集合中的字母，忽略大小写
                #             if char.lower() in valid_start_letters:
                #                 # 提取从第一个有效字母开始的所有内容
                #                 score_content = remaining_content[a:].strip()
                #                 break
                #     else:
                #         score_content = ""  # 如果找不到符合条件的字母
                #
                #     # 如果提取到了符合条件的内容，则退出循环
                #     if score_content:
                #         print(score_content)
                #         break  # 找到符合条件的结果后，退出循环
                #
                #     # 如果未找到符合条件的字母，继续查找下一个 "Evaluation Result"
                #     start_index = score.find("Updated Evaluation Result", start_index + len("Updated Evaluation Result"))

                # 如果没有符合条件的 "Evaluation Result"，提示未找到
                # if not score_content:
                #     print("未找到符合条件的 'Updated Evaluation Result' 部分")
                # logger.info('>>>>>endlogger.info(f'>>>>>>>>>>questions:\n' , questions)ofmemeID')
                #
                # pred_label = final_result
                # result_dict['id'].append(id)
                # result_dict['gt_label'].append(gt_label)
                # result_dict['pred_label'].append(pred_label)

            except Exception as e:
                logger.info('>>>>>>>>>>>Error occurred during conversation...')
                logger.info('Errormessage: ' + str(e))
                print(f"An error occurred: {e}")
                s[index] = 'Error'
                # logger.info(f'ID:{id} Result: ERROR')
                # result_dict['error'].append(id)

            for agent in agents:
                agent.reset()
            host.reset()
            index += 1

    with open("../hidtory.json", "w") as f:
        json.dump(history, f,indent=4)
    with open("../description.json", "w") as f:
        json.dump(des, f,indent=4)
    with open("../result.json", "w") as f:
        json.dump(s, f,indent=4)
    # pred_label = result_dict['pred_label']
    # gt_label = result_dict['gt_label']
    # pearson_corr, _ = pearsonr(pred_label, gt_label)
    #
    # logger.info(f'human reference:{pearson_corr:.4f}')
    #
    # with open(config['result_path'], 'w') as f:
    #     json.dump(result_dict, f, indent=4, ensure_ascii=False)
    #
    # return


if __name__ == '__main__':
    # load config from json
    with open('.../config.json', 'r') as f:
        config = json.load(f)

    # load prompt from prompt_dict.py
    from prompt_dict import prompt

    chat(config, prompt['color'])
