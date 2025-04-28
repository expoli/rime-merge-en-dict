import json
import os
import re
import requests
from datetime import datetime
import sys
import io

# 配置文件路径
MERGE_FILE_NAME = 'en_merge'
CONFIG_FILE = 'config.json'
MERGE_FILE = f'{MERGE_FILE_NAME}.dict.yaml'

# 从GitHub获取文件更新时间
def get_github_file_update_time(repo_url, file_path):
    api_url = f'https://api.github.com/repos/{repo_url}/commits?path={file_path}'
    response = requests.get(api_url)
    if response.status_code == 200:
        commits = response.json()
        if commits:
            return datetime.strptime(commits[0]['commit']['committer']['date'], '%Y-%m-%dT%H:%M:%SZ')
    return None

# 加载本地配置文件
def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

# 保存配置文件
def save_config(config):
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2)

# 从GitHub下载文件
def download_github_file(repo_url, file_path):
    # 从URL中提取仓库名
    repo_name = repo_url.split('/')[-1]
    # 创建仓库名对应的子文件夹
    os.makedirs(os.path.join('en_dicts', repo_name), exist_ok=True)
    # 生成新的文件路径
    new_file_path = os.path.join('en_dicts', repo_name, os.path.basename(file_path))
    # https://github.com/iDvel/rime-ice/raw/refs/heads/main/en_dicts/en.dict.yaml
    # 获取默认分支
    branch_api_url = f'https://api.github.com/repos/{repo_url}'
    branch_response = requests.get(branch_api_url)
    if branch_response.status_code == 200:
        default_branch = branch_response.json()['default_branch']
    else:
        default_branch = 'main'

    raw_url = f'https://raw.githubusercontent.com/{repo_url}/{default_branch}/{file_path}'
    response = requests.get(raw_url)
    if response.status_code == 200:
        # 将文件保存到子文件夹
        with open(new_file_path, 'w', encoding='utf-8') as f:
            f.write(response.text)
        return response.text
    return None

def contains_special_characters(s):
    return bool(re.search(r'[^a-zA-Z]', s))

def remove_special_characters(s):
    return re.sub(r'[^a-zA-Z0-9]', '', s)

def contains_non_alpha(s):
    return len(re.findall(r'[^a-zA-Z]', s))

# 提取英文词库
def extract_english_words(content):
    words = {}
    # filtered_lines = []
    for line in content.split('\n'):
        if '\t' in line:
            if line.startswith('#'):
                continue
            # value = line.split('\t')[1]
            # # 过滤掉编码中以数字开头的行
            # if value[0].isdigit():
            #     filtered_lines.append(line)
            #     continue
            # if contains_non_alpha(value) == 0 or contains_non_alpha(value) == 1:
            #     clear_value = remove_special_characters(value)
            #     # 重新组合line数据
            #     parts = line.split('\t')
            #     if len(parts) == 2:
            #         parts[1] = clear_value
            #         line = '\t'.join(parts)
            # else:
            #     filtered_lines.append(line)
            #     continue
            # # 过滤掉编码中以特殊字符开头的行如 .DS_Store和.gitignore等
            # if contains_special_characters(value):
            #     filtered_lines.append(line)
            #     continue
            # 使用去除特殊符号的整行作为key
            key = remove_special_characters(line)
            words[key] = line
    # # 将过滤掉的行写入记录文件
    # if filtered_lines:
    #     with open('filtered_lines.log', 'w', encoding='utf-8') as f:
    #         f.write('\n'.join(filtered_lines) + '\n')
    return words

# 合并词库
def merge_words(existing_words:dict, new_words:dict, from_dict:str, debug_mode=True):
    for key in new_words.keys():
        if key in existing_words:
            if debug_mode:
                print(f'重复词条: {key} (来自词库: {from_dict})')
            continue
        existing_words[key] = new_words[key]
    return existing_words

# 保存合并后的词库
def save_merged_words(words:dict):
    with open(MERGE_FILE, 'w', encoding='utf-8') as f:
        # 写入固定文件头
        f.write('# Rime dictionary\n')
        f.write('# encoding: utf-8\n')
        f.write('# ------- 英文合并词库 -------\n')
        f.write('# https://github.com/expoli/rime-en_dicts\n')
        f.write('---\n')
        f.write(f'name: {MERGE_FILE_NAME}\n')
        f.write(f'version: "{datetime.now().strftime("%Y-%m-%d")}"\n')
        f.write('sort: original\n')
        f.write('use_preset_vocabulary: false\n')
        f.write('...\n\n')
        # 写入词库内容
        for key in sorted(words, key=lambda x: x.split('\t')[0].lower()):
            f.write(words[key].rstrip('\n') + '\n')

# 主函数
def main(debug_mode=True):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    config = load_config()
    
    if 'repositories' not in config:
        print('请先在config.json中配置repositories')
        return
    
    # 加载现有词库
    existing_words = {}
    # if os.path.exists(MERGE_FILE):
    #     with open(MERGE_FILE, 'r', encoding='utf-8') as f:
    #         for line in f:
    #             if '\t' in line:
    #                 key = line.split('\t')[0]
    #                 if key .startswith('#'):
    #                     continue
    #                 existing_words[key] = line
    
    updated = False
    
    for repo_config in config['repositories']:
        if 'repo_url' not in repo_config or 'file_paths' not in repo_config:
            continue
        
        for file_path in repo_config['file_paths']:
            # 获取GitHub文件更新时间
            remote_time = get_github_file_update_time(repo_config['repo_url'], file_path)
            
            if debug_mode:
                print(f'检查文件: {repo_config["repo_url"]}/{file_path}')
                print(f'远程更新时间: {remote_time}')
                print(f'本地更新时间: {repo_config.get("last_update")}')
                process_flag = True
            
            elif remote_time and ('last_update' not in repo_config or 
                              not repo_config['last_update'] or 
                              remote_time > datetime.strptime(repo_config['last_update'], '%Y-%m-%dT%H:%M:%SZ')):
                process_flag = False
            
            if process_flag:
                # 下载新文件
                content = download_github_file(repo_config['repo_url'], file_path)
                if content:
                    # 提取英文单词
                    new_words = extract_english_words(content)
                    
                    # 合并词库
                    existing_words = merge_words(existing_words, new_words, repo_config['repo_url'] + '/' + file_path, debug_mode)
                    
                    # 更新配置
                    if remote_time:
                        repo_config['last_update'] = remote_time.strftime('%Y-%m-%dT%H:%M:%SZ')
                    updated = True
                else:
                    print(f'文件下载失败: {file_path}')
    
    if updated:
        # 保存合并结果
        save_merged_words(existing_words)
        save_config(config)
        print('词库已更新')
    else:
        print('无需更新')

if __name__ == '__main__':
    main()