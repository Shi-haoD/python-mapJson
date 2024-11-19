import os
import json
import requests
from tqdm import tqdm

# 下载文件的函数
def download_file(url, filepath):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        with open(filepath, 'w', encoding='utf-8') as file:
            json.dump(response.json(), file, ensure_ascii=False, indent=4)
        return True
    except Exception as e:
        print(f"Failed to download {os.path.basename(filepath)}: {e}")
        return False

# 第一步：下载并解析 all.json
def first_step():
    url = 'https://geo.datav.aliyun.com/areas_v3/bound/all.json'
    print('Downloading all.json...')
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        print('Downloaded all.json successfully')
        return response.json()
    except Exception as e:
        print(f"Failed to download all.json: {e}")
        exit(1)

# 第二步：遍历 JSON 数组，下载每个 adcode 对应的 JSON
def second_step(json_array):
    failed_downloads = []
    skipped_downloads = []

    # 确保 dist 目录存在
    dist_path = os.path.join(os.getcwd(), 'dist')
    os.makedirs(dist_path, exist_ok=True)

    # 逐个下载
    for item in tqdm(json_array, desc="Downloading files"):
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
            success = download_file(url, normal_file_path)
            if not success:
                failed_downloads.append(adcode)
        else:
            skipped_downloads.append(normal_file_name)

        # 如果是特殊代码，检查并下载 _full 文件
        if is_special_code:
            if not os.path.exists(full_file_path):
                url = f"https://geo.datav.aliyun.com/areas_v3/bound/{adcode}_full.json"
                success = download_file(url, full_file_path)
                if not success:
                    failed_downloads.append(adcode)
            else:
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
