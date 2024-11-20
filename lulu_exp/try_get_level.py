import requests

# 接口地址
base_url = "http://106.54.192.233:8080"

# 初始数据
card_info = [
    {
        "description": "十以内的加法",
        "cardCode": """  
        spawn_card({text:"5",x:100, y: 200, draggable:false});
        spawn_card({text:"+",x:220, y: 200, draggable:false});
        spawn_card({text:"3",x:340, y: 200, draggable:false});
        spawn_card({text:"=",x:460, y: 200});
        set_target({answer:"8",x:580, y: 200});
        spawn_card({text:"4"});
        spawn_card({text:"6"});
        spawn_card({text:"8"});
        spawn_card({text:"53"});
        """,
    },
    {
        "description": "数字的前后关系",
        "cardCode": """  
        spawn_card({text:"4",x:220, y:200, draggable:false});
        set_target({answer:"3",x:100, y: 200});
        set_target({answer:"5",x:340, y: 200});
        spawn_card({text:"1"});
        spawn_card({text:"3"});
        spawn_card({text:"5"});
        spawn_card({text:"7"});
        """,
    },
    {
        "description": "古诗诗句排序",
        "cardCode": """  
        set_target({answer:"床前明月光",x:100, y: 200,correct_text:"没错，第一句是床前明月光", error_text:"好好想想静夜思的第一句是什么"});
        set_target({answer:"疑是地上霜",x:220, y: 200});
        set_target({answer:"举头望明月",x:340, y: 200});
        set_target({answer:"低头思故乡",x:460, y: 200});
        spawn_card({text:"疑是地上霜"});
        spawn_card({text:"床前明月光"});
        spawn_card({text:"低头思故乡"});
        spawn_card({text:"举头望明月"});
        """,
    },
]

# 补全数据字段
for i, item in enumerate(card_info):
    item["id"] = i + 1  # 补全 id
    item["data"] = item["cardCode"]  # 补全 code
    item["title"] = item["description"]  # 补全 title
    # item["data"] = None  # 预留 data 字段
    item["assetFinished"] = False  # 预留 assetFinished
    item["ifReference"] = True  # 预留 ifReference

# 打印准备上传的数据
print("准备上传的数据：", card_info)

# 上传数据
post_url = f"{base_url}/uploadLevel"
response = requests.post(post_url, json=card_info)

# 检查上传响应
if response.status_code == 200:
    print("数据上传成功:", response.json())
else:
    print(f"上传失败，状态码: {response.status_code}, 响应: {response.text}")

# 下载数据
get_url = f"{base_url}/getAllLevels"
response = requests.get(get_url)

# 检查下载响应
if response.status_code == 200:
    levels = response.json()
    print("下载的数据：", levels)
else:
    print(f"下载失败，状态码: {response.status_code}, 响应: {response.text}")
