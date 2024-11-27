import os
from openai import OpenAI

def question2response(user_input):
    client = OpenAI(
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
        api_key=os.getenv("DASHSCOPE_API_KEY")
    )  # 创建客户端实例

    response = client.chat.completions.create(  # 发送请求
        model="qwen-max-latest",
        messages=[
            {"role": "user", "content": user_input}
        ],
        stream=False,
        response_format={
            'type': 'json_object'
        }
    )

    return response.choices[0].message.content  # 返回AI的回答内容
