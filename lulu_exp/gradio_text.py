import os

proxy = 'http://localhost:8234'
os.environ['HTTP_PROXY'] = proxy
os.environ['HTTPS_PROXY'] = proxy

import gradio as gr
from generate_prompt import parse_jsonl, get_prompt
from text_embedding import TextBase
import json
import zhipu_question2response as zhipu_qr
import deepseek_question2response as deepseek_qr

save_file = "lulu_exp/output_log.txt"

current_query = None

# 假设的函数
def get_response(prompt, model_choice):
    # 根据模型选择调用相应的函数
    if model_choice == "Zhipu":
        response = zhipu_qr.question2response(prompt)
    elif model_choice == "DeepSeek":
        response = deepseek_qr.question2response(prompt)
    else:
        raise ValueError("Invalid model choice")
    
    # 如果成功返回，用jsonl格式续写到save_file中，有 prompt 和 response 两个字段
    with open(save_file, "a", encoding="utf-8") as f:
        f.write(json.dumps({"prompt": prompt, "response": response}, ensure_ascii=False) + "\n")
    
    return response

# 预加载数据
level_data_file = "lulu_exp/sample_levels_python.jsonl"
base_save_file = "lulu_exp/id_text_vector.parquet"

level_datas = parse_jsonl(level_data_file)
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

def generate_prompt(query):
    global current_query
    current_query = query
    prompt = get_prompt(query, text_base, level_datas, layout_data, if_english=False)
    return prompt

def prompt2response(prompt, model_choice):
    response = get_response(prompt, model_choice)
    return response

# 处理用户输入的函数
def process_query(query, model_choice):
    prompt = get_prompt(query, text_base, level_datas, layout_data, if_english=False)
    response = get_response(prompt, model_choice)
    return response, prompt

from post_extract import post_extract

def callback_post_extract(response):
    data = post_extract(response)

    python_code = ""
    if "python_code" in data:
        python_code = data["python_code"]

    global current_query
    with open(save_file, "a", encoding="utf-8") as f:
        f.write(json.dumps({"query": current_query, "response": response, "python_code": python_code}, ensure_ascii=False) + "\n")

    return python_code

# Gradio UI 定义
with gr.Blocks() as demo:
    with gr.Row():
        input_query = gr.Textbox(label="请输入查询内容", placeholder="学习一首李白的古诗", scale=20)
        submit_button = gr.Button("生成结果", scale=1)

    # 新增模型选择单选框
    with gr.Row():
        model_selector = gr.Radio(
            choices=["Zhipu", "DeepSeek"],
            value="DeepSeek",
            label="选择模型"
        )

    with gr.Row():
        python_code_output = gr.TextArea(label="生成的 Python 代码", interactive=False)

    with gr.Row():
        result_output = gr.TextArea(label="生成的结果(JSON)", interactive=False)
        
    with gr.Row():
        prompt_output = gr.TextArea(label="生成的 Prompt", interactive=False)

    # 按钮点击事件
    submit_button.click(
        generate_prompt,
        inputs=[input_query],
        outputs=[prompt_output]
    ).then(
        prompt2response,
        inputs=[prompt_output, model_selector],  # 同步传入模型选择
        outputs=[result_output]
    ).then(
        callback_post_extract,
        inputs=[result_output],
        outputs=[python_code_output]
    )

# 启动 Gradio Demo
if __name__ == "__main__":
    demo.launch(share=True)
