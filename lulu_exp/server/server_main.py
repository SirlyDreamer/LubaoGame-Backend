from flask import Flask, send_from_directory
import os
import json

app = Flask(__name__)

# 初始化时扫描目录并生成映射文件
def init_map():
    image_map = []
    image_map_output = {
        "imageMap": {},
        "audioMap": {}
    }

    # 扫描images目录
    for filename in os.listdir('images'):
        if filename.endswith('.png') or filename.endswith('.mp3'):
            file_type = 'cardImage' if filename.endswith('.png') else 'audio'
            name = os.path.splitext(filename)[0]
            url = f'http://127.0.0.1:5000/{file_type}/{name}'

            # 添加到映射列表
            image_map.append({
                "type": file_type,
                "url": url,
                "name": name
            })

            # 添加到输出字典
            if file_type == 'cardImage':
                image_map_output["imageMap"][name] = url
            else:
                image_map_output["audioMap"][name] = url

    # 写入jsonl文件
    with open('lulu_exp/server/image_map.jsonl', 'w', encoding='utf-8') as f:
        for item in image_map:
            f.write(json.dumps(item, ensure_ascii=False) + '\n')

    # 写入js可读的文本文件
    with open('lulu_exp/server/image_map_output_for_js.txt', 'w', encoding='utf-8') as f:
        f.write('const imageMap = ' + json.dumps(image_map_output["imageMap"], ensure_ascii=False) + ';\n')
        f.write('const audioMap = ' + json.dumps(image_map_output["audioMap"], ensure_ascii=False) + ';\n')

# 在服务器启动时执行初始化
@app.before_first_request
def before_first_request():
    init_map()

# 路由，用于提供文件
@app.route('/<file_type>/<name>')
def get_file(file_type, name):
    # print(file_type, name)
    if file_type not in ['cardImage', 'audio']:
        return "Invalid file type", 404

    file_extension = '.png' if file_type == 'cardImage' else '.mp3'
    file_path = os.path.join('images', name + file_extension)
    # print(file_path)

    # 使用 send_from_directory 提供文件
    if os.path.exists(file_path):
        # print("found")
        return send_from_directory('../../images', name + file_extension)
    else:
        return "File not found", 404

if __name__ == '__main__':
    app.run(debug=True)
