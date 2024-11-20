import os
import json

# 压缩 JSON 文件的函数
def compress_json_file(input_filepath, output_dir):
    try:
        # 读取 JSON 数据
        with open(input_filepath, 'r', encoding='utf-8') as file:
            data = json.load(file)

        # 确保输出目录存在
        os.makedirs(output_dir, exist_ok=True)

        # 构建输出文件路径
        filename = os.path.basename(input_filepath)
        output_filepath = os.path.join(output_dir, filename)

        # 写入压缩后的 JSON 数据
        with open(output_filepath, 'w', encoding='utf-8') as file:
            json.dump(data, file, ensure_ascii=False, separators=(',', ':'))
        print(f"Compressed: {filename} -> {output_filepath}")
    except Exception as e:
        print(f"Failed to compress {input_filepath}: {e}")

# 遍历 dist 文件夹中的 JSON 文件并压缩
def compress_all_json_files(input_dir, output_dir):
    if not os.path.exists(input_dir):
        print(f"Input directory {input_dir} does not exist.")
        return

    # 遍历 dist 文件夹中的所有 JSON 文件
    for root, _, files in os.walk(input_dir):
        for file in files:
            if file.endswith('.json'):
                input_filepath = os.path.join(root, file)
                compress_json_file(input_filepath, output_dir)

# 主函数
def main():
    input_dir = './dist'  # 原始 JSON 文件所在目录
    output_dir = './compressed'  # 压缩后文件保存目录
    compress_all_json_files(input_dir, output_dir)
    print(f"All JSON files from {input_dir} have been compressed into {output_dir}")

if __name__ == "__main__":
    main()
