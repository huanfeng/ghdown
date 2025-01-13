#!/usr/bin/env python3
import json
import sys
import argparse
import os
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError
from urllib.parse import urlparse

def parse_github_url(url):
    """解析GitHub URL获取用户名和仓库名"""
    if not url.startswith('http'):
        # 假设格式为 user/repo 或 user/repo:tag
        parts = url.split(':')
        repo_info = parts[0]
        tag = parts[1] if len(parts) > 1 else 'latest'
        user, repo = repo_info.split('/')
        return user, repo, tag
    
    # 处理完整URL
    path = urlparse(url).path.strip('/')
    parts = path.split('/')
    
    if len(parts) >= 2:
        return parts[0], parts[1], 'latest'
    return None, None, None

def make_request(url, token=None, accept_type=None):
    """发送HTTP请求"""
    headers = {}
    if token:
        headers['Authorization'] = f'Bearer {token}'
    if accept_type:
        headers['Accept'] = accept_type
    
    req = Request(url, headers=headers)
    try:
        with urlopen(req) as response:
            if accept_type == 'application/octet-stream':
                return response.read()
            return json.loads(response.read().decode('utf-8'))
    except HTTPError as e:
        print(f'Error: {e.code} - {e.reason}')
        sys.exit(1)
    except URLError as e:
        print(f'Error: {e.reason}')
        sys.exit(1)

def get_asset_info(user, repo, tag, token=None):
    """获取release资产信息"""
    # 构建API URL
    if tag == 'latest':
        url = f'https://api.github.com/repos/{user}/{repo}/releases/latest'
    else:
        url = f'https://api.github.com/repos/{user}/{repo}/releases/tags/{tag}'
    
    release_data = make_request(url, token, 'application/vnd.github.v3+json')
    
    if not release_data.get('assets'):
        print('Error: No assets found in release')
        sys.exit(1)
    
    # 返回第一个资产的信息
    asset = release_data['assets'][0]
    return {
        'url': asset['url'],
        'id': asset['id'],
        'name': asset['name']
    }

def download_asset(asset_url, token, output_path):
    """下载资产文件"""
    print(f'Downloading to {output_path}...')
    content = make_request(asset_url, token, 'application/octet-stream')
    
    with open(output_path, 'wb') as f:
        f.write(content)

def main():
    parser = argparse.ArgumentParser(description='GitHub Release Download Tool')
    parser.add_argument('target', help='Target repository (format: user/repo[:tag] or URL)')
    parser.add_argument('--tag', '-t', help='Specify release tag')
    parser.add_argument('--output', '-o', help='Output file path')
    parser.add_argument('--token', help='GitHub API token', default=os.environ.get('GITHUB_TOKEN'))
    
    args = parser.parse_args()
    
    try:
        # 解析目标
        user, repo, parsed_tag = parse_github_url(args.target)
        if not all([user, repo]):
            print('Error: Invalid GitHub repository format')
            sys.exit(1)
        
        # 使用命令行参数的tag覆盖URL中的tag
        if args.tag:
            parsed_tag = args.tag
        
        print(f'Fetching release information for {user}/{repo}...')
        asset_info = get_asset_info(user, repo, parsed_tag, args.token)
        
        # 确定输出路径
        output_path = args.output if args.output else asset_info['name']
        
        download_asset(asset_info['url'], args.token, output_path)
        print(f'Download completed: {output_path}')
        
    except Exception as e:
        print(f'Error: {str(e)}')
        sys.exit(1)

if __name__ == '__main__':
    main()
