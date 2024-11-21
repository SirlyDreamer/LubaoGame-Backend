# 我们希望有一个prompt生成的函数

# 整体游戏生成prompt的设想

# # 系统函数说明
# {系统函数的说明，如spawn_card, bind_event}

# # Reference
# {根据{用户Query}选取的 query-低代码 的2个例子}

# [ # Layout
# 用户也可以通过交互界面直接预先排好一个layout ]

# # Goal
# {描述如何参考函数说明和Reference，根据用户Query来进行低代码的编写}

from text_embedding import TextBase

import json

def get_task_prompt( query_str, if_english = False):
    if not if_english:
        return f"""我正在编写一个简易的早教js游戏。请参考系统函数说明中的函数，以及对应例子。编写一个Query = "{query_str}"相关的js游戏。"""
    else:
        return f"""I am writing a simple early education game. Please refer to the function description in the system function description, as well as the corresponding example. Write a game related to the Query = "{query_str}"."""
    
def get_function_prompt( function_name, if_english = False):
    return """# 系统函数说明

整个游戏的画面是800 * 450的，并且提供以下函数

## spawn_card

spawn_card({text:"卡片内容"}) 或 spawn_card({text:"卡片内容", x: x, y: y})
根据text对应的卡片，在x,y中心位置生成卡片，如spawn_card({text:"苹果"})或者spawn_card({text:"一个盘子", x: 400, y: 300})

其中可选参数为
text 卡片的描述，或者卡片的文件hash名，没有卡片的时候会自动调用dalle3进行文生图
x,y 中心位置，候选卡牌一般不需要指定x和y，此时卡片会进入下方的“候选卡片区域”。一些'道具和场景'卡片需要指定x和y
scale 默认为1， 卡片的大小
if_moveable 卡片是否能被移动，一般题目卡片不能被移动
click_text 默认为空，如果指定，则点击的时候会语音播放对应的文本（或者audio hash名对应的音频)

## set_target

set_target({answer:"目标卡片内容",x: x, y: y}) 在x,y中心位置生成一个虚线框，如果用户将答案对应的card拖动到框中，则会播放correct_text

其中可选参数为
answer 默认的答案卡片
x,y 中心位置，必要， 如果题目只有一行一般y = 225，有两行时y = 150 和 300 以此类推
scale 默认为1
error_text 默认为空，如果指定，当拖动错误卡片的时候，会播放语音，并把卡片弹回原来的位置
correct_text 默认为空，如果指定，拖动正确卡片时，会播放对应的语音

## 游戏结束

所有的targets的文本都吻合的时候，游戏成功

## 最简单的例子

```JavaScript
spawn_card( {text:"你好"} ) # 自动生成在候选区
set_target( {answer:"你好", x: 400, y: 225, correct_text: "成功啦"} )
```"""

import random

def get_reference_prompt( query_str, text_base,level_datas,if_english = False):
    # 先随机选取一个例子作为reference
    # 稍后升级为使用embedding进行相似度计算
    # level_datas = [random.choice(level_datas)]
    datas = text_base.search_with_text(query_str, 2)
    ids = [ data['id'] for data in datas ]
    print(ids)
    level_datas = [ level_datas[id] for id in ids]

    prompt = "# Reference"

    for data in level_datas:
        prompt += f"\nQuery: {data['query_str']}\nAnswer:\n{data['js_code']}\n"

    return prompt.strip()

def parse_jsonl(file_name):
    """
    读取 JSONL 文件并将其解析为列表。
    
    Args:
        file_name (str): JSONL 文件的路径。
    
    Returns:
        list: 包含所有 JSON 对象的列表。
    """
    levels = []
    try:
        with open(file_name, 'r', encoding='utf-8') as file:
            for line in file:
                # 将每行解析为 JSON 对象
                levels.append(json.loads(line.strip()))
    except FileNotFoundError:
        print(f"文件 {file_name} 未找到，请检查路径是否正确。")
    except json.JSONDecodeError as e:
        print(f"JSON 格式错误：{e}")
    return levels

def get_task_suffix_prompt( query_str, if_english = False):
    if not if_english:
        return f"""# Goal

请参考系统函数说明中的函数，以及对应例子。编写一个Query = "{query_str}"相关的游戏。

根据Query的需求，参考Reference中的例子，进行JavaScript程序的编写 

Let's think it step-by-step 并输出为json格式，包含两个字段
- analysis 分析具体的实现思路
- js_code 整段JavaScript代码的具体实现"""
    else:
        return f"""# Goal

Please refer to the function description in the system function description, as well as the corresponding example. Write a game related to the Query = "{query_str}".

According to the requirements of Query, refer to the example in Reference, and write a JavaScript program.

Let's think it step-by-step and output it in json format
- analysis: Analyze the specific implementation ideas
- js_code: Specific implementation"""
    

def get_layout_prompt_python( layout_datas, if_english = False):
    prompt = """# Layout
用户已经在编辑器中编辑了部分card和target的位置，参考下列信息"""
    for data in layout_datas:
        # 读取isTarget 字段，默认为空
        isTarget = data.get("isTarget", None)
        if isTarget is None:
            continue

        if isTarget:
            answer_text = data.get("text", "\{TBD\}")
            x = data.get("x", None)
            y = data.get("y", None)
            if x is None or y is None:
                continue
            correctText = data.get("correctText", "")
            opt_correct_text = "" if correctText == "" else f""", correct_text = "{correctText}" """
            errorText = data.get("errorText", "")
            opt_error_text = "" if errorText == "" else f""", error_text = "{errorText}" """
            
            line = f"""set_target("{answer_text}",{x},{y}{opt_correct_text}{opt_error_text})"""
            prompt += "\n" + line
        else:
            text = data.get("text", "\{TBD\}")
            x = data.get("x", None)
            y = data.get("y", None)
            try:
                x = int(x)
                y = int(y)
            except:
                pass
            candSelect = data.get("candSelect", "auto")
            xy_str = ""
            if x is None or y is None:
                continue
            if candSelect == "auto":
                # 如果y > 510 则 xy_str = ""，否则为x,y
                if y > 510:
                    xy_str = ""
                else:
                    xy_str = f",{x},{y}"
            elif candSelect == "cand":
                xy_str = ""
            else:
                xy_str = f",{x},{y}"

            if_moveable = data.get("if_moveable", "moveable")
            opt_moveable = "" if if_moveable == "moveable" else """, if_moveable = False """
            clickText = data.get("clickText", "")
            opt_click_text = "" if clickText == "" else f""", click_text = "{clickText}" """

            line = f"""add_card("{text}"{xy_str}{opt_moveable}{opt_click_text})"""
            prompt += "\n" + line

    prompt = prompt.strip()
    prompt += "\n" + "在分析时请思考除了上述用户指定的元素，是否还要添加元素，并且把\{TBD\}的字段自动补充完整。"

    return prompt.strip()

def get_layout_prompt(layout_datas, if_english=False):
    prompt = """// Layout
// 用户已经在编辑器中编辑了部分 card 和 target 的位置，参考下列信息"""
    for data in layout_datas:
        # Read isTarget field, default to None
        isTarget = data.get("isTarget", None)
        if isTarget is None:
            continue

        if isTarget:
            answer_text = data.get("text", "<TBD>")
            x = data.get("x", None)
            y = data.get("y", None)
            if x is None or y is None:
                continue
            correctText = data.get("correctText", "")
            opt_correct_text = "" if correctText == "" else f', correct_text: "{correctText}"'
            errorText = data.get("errorText", "")
            opt_error_text = "" if errorText == "" else f', error_text: "{errorText}"'

            line = f'''set_target({{ answer: "{answer_text}", x: {x}, y: {y}{opt_correct_text}{opt_error_text} }});'''
            prompt += "\n" + line
        else:
            text = data.get("text", "<TBD>")
            x = data.get("x", None)
            y = data.get("y", None)
            try:
                x = int(x)
                y = int(y)
            except:
                pass
            candSelect = data.get("candSelect", "auto")
            xy_str = ""
            if x is None or y is None:
                continue
            if candSelect == "auto":
                # If y > 510, then xy_str = "", otherwise it is x, y
                if y > 510:
                    xy_str = ""
                else:
                    xy_str = f', x: {x}, y: {y}'
            elif candSelect == "cand":
                xy_str = ""
            else:
                xy_str = f', x: {x}, y: {y}'

            if_moveable = data.get("if_moveable", "moveable")
            opt_moveable = "" if if_moveable == "moveable" else ", if_moveable: false"
            clickText = data.get("clickText", "")
            opt_click_text = "" if clickText == "" else f', click_text: "{clickText}"'

            line = f'''spawn_card({{ text: "{text}"{xy_str}{opt_moveable}{opt_click_text} }});'''
            prompt += "\n" + line

    prompt = prompt.strip()
    prompt += "\n" + "// 在分析时请思考除了上述用户指定的元素，是否还要添加元素，并且把 <TBD> 的字段自动补充完整。"

    return prompt.strip()


def get_prompt(query, text_base,level_datas, layout_data=None, if_english=False):
    """
    生成完整的prompt字符串。
    
    Args:
        query (str): 用户Query。
        text_base (TextBase): 参考的低代码数据。
        level_datas (list): 低代码数据
        layout_data (list): 布局数据，默认为None。
        if_english (bool): 是否生成英文prompt，默认为False。
        
    Returns:
        str: 完整的prompt字符串。
    """
    # 生成各部分prompt
    task_prompt = get_task_prompt(query, if_english)
    function_prompt = get_function_prompt("spawn_card", if_english)
    reference_prompt = get_reference_prompt(query, text_base,level_datas, if_english)
    task_suffix_prompt = get_task_suffix_prompt(query, if_english)

    # 如果有layout_data，则生成layout_prompt
    layout_prompt = ""
    if layout_data:
        layout_prompt = get_layout_prompt(layout_data, if_english)

    # 组装prompt
    full_prompt = "\n".join(filter(None, [task_prompt, function_prompt, reference_prompt, layout_prompt, task_suffix_prompt]))
    return full_prompt


import os

# 测试代码
if __name__ == '__main__':
    query = "学习一首李白的古诗"
    out_file = "lulu_exp/output.txt"

    # 载入数据
    level_data_file = "lulu_exp/sample_levels.jsonl"
    example_layout_file = "lulu_exp/古诗模板.txt"

    level_datas = parse_jsonl(level_data_file)
    layout_data = parse_jsonl(example_layout_file)

    base_save_file = "lulu_exp/id_text_vector.parquet"

    text_base = TextBase()

    query_texts = [d["query_str"] for d in level_datas]

    rebuild = True

    if os.path.exists(base_save_file):
        text_base.load(base_save_file)
        rebuild = False
        for query_text in query_texts:
            if text_base.strong_match( query_text ) is None:
                rebuild = True
                break

    if rebuild:
        text_base = TextBase()
        text_base.build_base(query_texts)
        text_base.save(base_save_file)

    # 调用get_prompt生成完整prompt
    prompt = get_prompt(query, text_base,level_datas, layout_data, if_english=False)

    # 将输出写入文件
    with open(out_file, "w", encoding="utf-8") as f:
        f.write(prompt)
