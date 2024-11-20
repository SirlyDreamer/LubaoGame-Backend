# prompt

我希望实现一个本地的python后台

初始化的时候，扫描images目录下所有的png和mp3文件

对于每个png文件，都生成对应的url(类似127.0.0.1下面的一个地址）。

同时对应在lulu_exp/server/image_map.jsonl中，记录所有数据

分为三个字段 type为 cardImage 或者 audio， 然后url字段，name字段用文件名（去除后缀）

同时生成一个lulu_exp/server/image_map_output_for_js.txt，生成两个js可以读的字典格式
imageMap和audioMap，key为name，value为url