import os, sys
import json

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from generate_prompt import parse_jsonl
from text_embedding import TextBase
import zhipu_question2response as zhipu_qr
import deepseek_question2response as deepseek_qr
from post_extract import post_extract
from post_extract import post_extract_js

# 环境变量
#proxy = 'http://localhost:8234'
#os.environ['HTTP_PROXY'] = proxy
#os.environ['HTTPS_PROXY'] = proxy

# 文件路径
# global save_file
# save_file = "output_test_results.jsonl"
level_data_file = "lulu_exp/sample_levels.jsonl"
level_data_python_file = "lulu_exp/sample_levels_python.jsonl"
base_save_file = "lulu_exp/id_text_vector.parquet"

# 预加载数据
level_datas = parse_jsonl(level_data_file)
level_datas_python = parse_jsonl(level_data_python_file)
layout_data = None

text_base = TextBase()
query_texts = [d["query_str"] for d in level_datas]

# 构建或加载基础数据
if os.path.exists(base_save_file):
    text_base.load(base_save_file)
    rebuild = any(text_base.strong_match(query_text) is None for query_text in query_texts)
else:
    rebuild = True

if rebuild:
    text_base = TextBase()
    text_base.build_base(query_texts)
    text_base.save(base_save_file)

# 假设的函数
def get_response(prompt, model_choice):
    if model_choice == "Zhipu":
        response = zhipu_qr.question2response(prompt)
    elif model_choice == "DeepSeek":
        response = deepseek_qr.question2response(prompt)
    else:
        raise ValueError("Invalid model choice")
    return response

import generate_prompt as gp_python
import generate_prompt_js as gp_js

# for js
def generate_prompt_js(query):
    prompt = gp_js.get_prompt(query, text_base, level_datas, layout_data, if_english=False)
    return prompt

# for python
def generate_prompt_python(query):
    prompt = gp_python.get_prompt(query, text_base, level_datas_python, layout_data, if_english=False)
    return prompt

def generate_prompt(query, mode="python"):
    if mode == "python":
        prompt = generate_prompt_python(query)
    elif mode == "js":
        prompt = generate_prompt_js(query)
    else:
        raise ValueError("Invalid mode")
    return prompt

def callback_post_extract(response, mode="python"):
    if mode == "python":
        data = post_extract(response)
    elif mode == "js":
        data = post_extract_js(response)
    else:
        raise ValueError("Invalid mode")
    
    code = data.get(f"{mode}_code", "")
    return code

def gen_code(query, mode="python", model_choice="DeepSeek"):
    prompt = generate_prompt(query, mode)
    response = get_response(prompt, model_choice)
    code = callback_post_extract(response, mode)
    result = {
        "query": query,
        f"{mode}_code": code,
        "response": response,
        "prompt": prompt
    }
    return result

from tqdm import tqdm
import requests

# 主测试逻辑
def test_queries(queries, model_choice="DeepSeek", mode="python", save_file = "lulu_exp/save.jsonl"):
    results = []
    for query in tqdm(queries):
        # Step 1: 生成 Prompt
        prompt = generate_prompt(query, mode)
        
        # Step 2: 调用模型获取 Response
        response = get_response(prompt, model_choice)
        
        # Step 3: 提取代码（Python 或 JS）
        code = callback_post_extract(response, mode)
        
        # Step 4: 保存结果到 JSONL
        result = {
            "query": query,
            f"{mode}_code": code,
            "response": response,
            "prompt": prompt
        }
        results.append(result)
        
        with open(save_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(result, ensure_ascii=False) + "\n")
    
    return results

# 测试输入
queries = [
    "爸爸的爸爸和妈妈分别叫什么",
    "学习一首经典的宋词",
    "生成一个认识水果的游戏",
    "生成一个认识形状的游戏",
    "红色的水果是什么",
    "认识植物的不同部位",
    "写一个认识中国菜的游戏",
    "关于水可以电解成氢气和氧气的游戏",
    "学习一下祖国-中国有哪些特色建筑",
    "学习一下哪个国旗是五星红旗"
]

# 执行测试
if __name__ == "__main__":
    headers = {'Content-Type': 'application/json'}
    data = {"query":"爸爸的爸爸和妈妈分别叫什么",
            "mode":'python',
            "model_choice":"DeepSeek"}
    url = 'http://127.0.0.1:8080/getCode'
    response = requests.post(url, data=json.dumps(data), headers=headers)
    response.encoding = 'utf-8'
    print(response.text)
