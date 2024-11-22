from openai import OpenAI

def get_api_key(file_path):
    with open(file_path, 'r') as file:
        return file.read().strip()

def question2response(user_input):
    qwen_api_key = get_api_key("lulu_exp/qwen_apikey.txt")  # 读取API密钥
    client = OpenAI(api_key=qwen_api_key, base_url="https://dashscope.aliyuncs.com/compatible-mode/v1")  # 创建客户端实例

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
