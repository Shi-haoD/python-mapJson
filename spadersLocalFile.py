import os
import json
import requests
import time
from tqdm import tqdm


# 下载文件的函数（带进度条）
def download_file_with_progress(url, filepath, delay=1):
    try:
        # 启用流模式
        response = requests.get(url, stream=True, timeout=10)
        response.raise_for_status()

        # 获取文件大小
        total_size = int(response.headers.get('content-length', 0))
        chunk_size = 1024  # 每次读取 1KB

        # 打开文件准备写入
        with open(filepath, 'wb') as file:
            with tqdm(total=total_size, unit='B', unit_scale=True, desc=os.path.basename(filepath)) as progress_bar:
                for chunk in response.iter_content(chunk_size=chunk_size):
                    file.write(chunk)
                    progress_bar.update(len(chunk))

        time.sleep(delay)  # 增加下载间隔
        return True
    except Exception as e:
        print(f"Failed to download {os.path.basename(filepath)}: {e}")
        return False


# 第一步：读取本地的 all.json 文件
def first_step():
    local_path = './all.json'
    print('Reading all.json...')
    try:
        with open(local_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
        print('Read all.json successfully')
        return data
    except Exception as e:
        print(f"Failed to read all.json: {e}")
        exit(1)


# 第二步：遍历 JSON 数组，下载每个 adcode 对应的 JSON
def second_step(json_array):
    failed_downloads = []
    skipped_downloads = []

    # 确保 dist 目录存在
    dist_path = os.path.join(os.getcwd(), 'dist')
    os.makedirs(dist_path, exist_ok=True)

    # 逐个下载
    for item in json_array:
        adcode = str(item['adcode'])
        is_special_code = adcode.endswith('00')

        # 构建下载链接和文件名
        normal_file_name = f"{adcode}.json"
        full_file_name = f"{adcode}_full.json"
        normal_file_path = os.path.join(dist_path, normal_file_name)
        full_file_path = os.path.join(dist_path, full_file_name)

        # 检查并下载普通文件
        if not os.path.exists(normal_file_path):
            url = f"https://geo.datav.aliyun.com/areas_v3/bound/{adcode}.json"
            success = download_file_with_progress(url, normal_file_path, delay=1)
            if not success:
                failed_downloads.append(adcode)
        else:
            print(f"Skipped: {normal_file_name}")
            skipped_downloads.append(normal_file_name)

        # 如果是特殊代码，检查并下载 _full 文件
        if is_special_code:
            if not os.path.exists(full_file_path):
                url = f"https://geo.datav.aliyun.com/areas_v3/bound/{adcode}_full.json"
                success = download_file_with_progress(url, full_file_path, delay=1)
                if not success:
                    failed_downloads.append(adcode)
            else:
                print(f"Skipped: {full_file_name}")
                skipped_downloads.append(full_file_name)

    # 返回失败的下载列表和跳过的下载列表
    return failed_downloads, skipped_downloads


# 主函数
def main():
    json_array = first_step()
    failed_downloads, skipped_downloads = second_step(json_array)

    # 输出跳过的下载
    if skipped_downloads:
        print(f"Skipped downloads: {', '.join(skipped_downloads)}")

    # 如果有失败的下载，尝试重新下载
    if failed_downloads:
        print(f"Retrying failed downloads: {', '.join(failed_downloads)}")
        retry_result, _ = second_step([{'adcode': adcode} for adcode in failed_downloads])
        if retry_result:
            print(f"Failed downloads after retry: {', '.join(retry_result)}")
        else:
            print("All failed downloads were successful on retry")
    else:
        print("All downloads completed successfully")


if __name__ == "__main__":
    main()
