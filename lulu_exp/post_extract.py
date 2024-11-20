# -*- coding: utf-8 -*-

import json

def markdown_to_json(markdown_str):
    # 移除Markdown语法中可能存在的标记，如代码块标记等
    if markdown_str.startswith("```json"):
        markdown_str = markdown_str[7:].strip("` \n\t").strip()
    elif markdown_str.startswith("```"):
        markdown_str = markdown_str[3:].strip("` \n\t").strip()
    # 如果在markdown_str开头的50个字符内能够发现```json
    elif markdown_str[:50].find("```json") != -1:
        start_index = markdown_str[:50].find("```json")
        markdown_str = markdown_str[start_index + 7:].strip("` \n\t").strip()
    elif markdown_str[:50].find("```") != -1:
        start_index = markdown_str[:50].find("```")
        markdown_str = markdown_str[start_index:].strip("` \n\t").strip()

    print("尝试解析")
    print(markdown_str[:12],"...",markdown_str[-12:])
    print()

    # 将字符串转换为JSON字典
    json_dict = json.loads(markdown_str)

    return json_dict

import re

def forced_extract(input_str, keywords):
    result = {key: "" for key in keywords}

    for key in keywords:
        # 使用正则表达式来查找关键词-值对
        pattern = f'"{key}":\s*"(.*?)"'
        match = re.search(pattern, input_str)
        if match:
            result[key] = match.group(1)
    
    return result

import re

def forced_extract_python_code(input_str, key="python_code"):
    """
    从输入字符串中提取 "python_code" 字段的内容，字段内容可能跨多行。
    """
    result = ""
    # 定义正则表达式匹配 "python_code" 的内容
    if key == "python_code":
        pattern = r'"python_code":\s*"(.*?)"\s*}'
    elif key == "js_code":
        pattern = r'"js_code":\s*"(.*?)"\s*\n}'
    match = re.search(pattern, input_str, re.DOTALL)
    if match:
        result = match.group(1)
    return result


def post_extract_js(input_str):
    # 关键词定义
    keywords = ["analysis", "js_code"]

    result = None

    try:
        # 尝试使用 markdown_to_json 提取
        result = markdown_to_json(input_str)
        
        # 检查是否包含所有关键词
        if "js_code" in result:
            return result
    except (json.JSONDecodeError, AttributeError):
        # 如果 JSON 解析失败，则继续尝试强制提取
        # print error 
        
        pass

    print("call forced_extract")

    # 使用强制提取方法
    result = forced_extract(input_str, keywords)
    result["js_code"] = forced_extract_python_code(input_str,"js_code")
    return result



def post_extract(input_str):
    # 关键词定义
    keywords = ["analysis", "python_code"]

    result = None

    try:
        # 尝试使用 markdown_to_json 提取
        result = markdown_to_json(input_str)
        
        # 检查是否包含所有关键词
        if "python_code" in result:
            return result
    except (json.JSONDecodeError, AttributeError):
        # 如果 JSON 解析失败，则继续尝试强制提取
        # print error 
        
        pass

    print("call forced_extract")

    # 使用强制提取方法
    result = forced_extract(input_str, keywords)
    result["js_code"] = forced_extract_python_code(input_str,"js_code")
    return result


# 测试代码
if __name__ == "__main__":
    input_str = """```json
{
  "analysis": "为了创建一个认识中国菜的游戏，我们可以设计一系列的卡片，每张卡片上都有一种中国菜的名称和图片。游戏的目标是将这些卡片与对应的中国菜名称匹配。我们将使用spawn_card函数来生成这些中国菜的卡片，并放置在画面的候选卡片区域。然后，使用set_target函数在每个目标位置创建一个虚线框，并设置正确的菜名作为答案。当玩家将正确的卡片拖动到虚线框内时，游戏将播放正确的提示音。以下是具体的实现步骤：

  1. 使用set_game函数开始游戏，并播放一段介绍音频。
  2. 使用spawn_card函数生成一系列代表不同中国菜的卡片。
  3. 使用set_target函数为每种中国菜设置一个目标位置和正确答案。
  4. 为每个目标设置正确的提示音和错误的提示音。

  游戏成功结束的条件是所有的目标位置都匹配了正确的中菜卡片。",
  "js_code": "set_game({\"start_audio\":\"欢迎来到认识中国菜的游戏！请将下面的菜名与其图片匹配。\"});
spawn_card({text:\"宫保鸡丁\"});
spawn_card({text:\"麻婆豆腐\"});
spawn_card({text:\"北京烤鸭\"});
spawn_card({text:\"红烧肉\"});
spawn_card({text:\"清蒸鲈鱼\"});
set_target({answer:\"宫保鸡丁\", x: 150, y: 225, correct_text: \"宫保鸡丁，匹配正确！\", error_text: \"这个不是宫保鸡丁，请再试一次。\"});
set_target({answer:\"麻婆豆腐\", x: 350, y: 225, correct_text: \"麻婆豆腐，匹配正确！\", error_text: \"这个不是麻婆豆腐，请再试一次。\"});
set_target({answer:\"北京烤鸭\", x: 550, y: 225, correct_text: \"北京烤鸭，匹配正确！\", error_text: \"这个不是北京烤鸭，请再试一次。\"});
set_target({answer:\"红烧肉\", x: 150, y: 325, correct_text: \"红烧肉，匹配正确！\", error_text: \"这个不是红烧肉，请再试一次。\"});
set_target({answer:\"清蒸鲈鱼\", x: 350, y: 325, correct_text: \"清蒸鲈鱼，匹配正确！\", error_text: \"这个不是清蒸鲈鱼，请再试一次。\"});"
}
```
    """

    output = post_extract(input_str)
    print(output)
