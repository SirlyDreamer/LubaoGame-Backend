from openai import OpenAI

def get_api_key(file_path):
    with open(file_path, 'r') as file:
        return file.read().strip()

def question2response(user_input):
    deepseek_api_key = get_api_key("lulu_exp/deepseek_apikey.txt")  # 读取API密钥
    client = OpenAI(api_key=deepseek_api_key, base_url="https://api.deepseek.com")  # 创建客户端实例

    response = client.chat.completions.create(  # 发送请求
        model="deepseek-chat",
        messages=[
            {"role": "user", "content": user_input}
        ],
        stream=False,
        response_format={
            'type': 'json_object'
        }
    )

    return response.choices[0].message.content  # 返回AI的回答内容
