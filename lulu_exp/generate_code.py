import os, sys
import json
import requests

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from generate_prompt import parse_jsonl
from text_embedding import TextBase
import zhipu_question2response as zhipu_qr
import deepseek_question2response as deepseek_qr
import qwen_question2response as qwen_qr
from post_extract import post_extract
from post_extract import post_extract_js

# 环境变量
#proxy = 'http://localhost:8234'
#os.environ['HTTP_PROXY'] = proxy
#os.environ['HTTPS_PROXY'] = proxy

# 文件路径
# global save_file
# save_file = "output_test_results.jsonl"
level_data_file = "/app/lulu_exp/sample_levels.jsonl"
level_data_python_file = "/app/lulu_exp/sample_levels_python.jsonl"
base_save_file = "/app/lulu_exp/id_text_vector.parquet"
level_data_file_ts = None
level_data_python_file_ts = None
level_datas = None
level_datas_python = None
layout_data = None
text_base = TextBase()

def load_datas():
    global level_data_file_ts, level_data_python_file_ts,\
            level_datas, level_datas_python, text_base

    rebuild = False
    ts = os.path.getmtime(level_data_file)
    if ts != level_data_file_ts:
        level_data_file_ts = ts
        level_datas = parse_jsonl(level_data_file)
        query_texts = [d["query_str"] for d in level_datas]

        if os.path.exists(base_save_file):
            text_base.load(base_save_file)
            rebuild = any(text_base.strong_match(query_text) is None for query_text in query_texts)
        else:
            rebuild = True

    ts = os.path.getmtime(level_data_python_file)
    if ts != level_data_python_file_ts:
        level_data_python_file_ts = ts
        level_datas_python = parse_jsonl(level_data_python_file)

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
    elif model_choice == "Qwen":
        response = qwen_qr.question2response(prompt)
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
    load_datas()
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
