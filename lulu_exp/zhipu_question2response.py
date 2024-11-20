from zhipuai import ZhipuAI

def get_api_key(file_path):
    with open(file_path, 'r') as file:
        return file.read().strip()

def question2response(user_input):
    zhipu_api_key = get_api_key("lulu_exp/zhipu_apikey.txt")  # 读取API密钥
    client = ZhipuAI(api_key=zhipu_api_key)  # 创建客户端实例
    response = client.chat.completions.create(  # 发送请求
        model="glm-4-0520",
        messages=[
            {"role": "system", "content": "Output with JSON format."},
            {"role": "user", "content": user_input}
        ],
    )
    return response.choices[0].message.content  # 返回AI的回答内容