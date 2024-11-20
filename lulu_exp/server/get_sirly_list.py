import requests

# 定义 URL
url = "http://106.54.192.233:8080/getAllAssets"

# 定义请求头（如果需要）
headers = {
    "Content-Type": "application/json"  # 确保请求头与后端预期格式匹配
}

# 定义请求体（如果需要）
data = {
    # 如果 API 要求请求体包含某些字段，在这里添加
    # 示例: "key": "value"
}

import json

try:
    # 发送 POST 请求
    response = requests.post(url, json=data, headers=headers)
    
    # 检查响应状态码
    if response.status_code == 200:
        # 解析并打印返回的 JSON 数据
        assets = response.json()
        print("素材列表:", assets)

        save_file = "lulu_exp/server/asset_list.json"
        with open(save_file, 'w', encoding='utf-8') as f:
            json.dump(assets, f, ensure_ascii=False, indent=4)
    else:
        print(f"请求失败，状态码: {response.status_code}, 响应: {response.text}")

except requests.exceptions.RequestException as e:
    print("请求发生错误:", e)
