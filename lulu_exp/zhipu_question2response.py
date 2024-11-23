import os
from zhipuai import ZhipuAI

def question2response(user_input):
    client = ZhipuAI(api_key=os.getenv("ZHIPU_API_KEY"))  # 创建客户端实例
    response = client.chat.completions.create(  # 发送请求
        model="glm-4-0520",
        messages=[
            {"role": "system", "content": "Output with JSON format."},
            {"role": "user", "content": user_input}
        ],
    )
    return response.choices[0].message.content  # 返回AI的回答内容