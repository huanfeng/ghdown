#!/usr/bin/env python3
import click
import requests
import os
import re
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

def get_asset_info(user, repo, tag, token=None):
    """获取release资产信息"""
    headers = {
        'Accept': 'application/vnd.github.v3+json'
    }
    if token:
        headers['Authorization'] = f'Bearer {token}'
    
    # 构建API URL
    if tag == 'latest':
        url = f'https://api.github.com/repos/{user}/{repo}/releases/latest'
    else:
        url = f'https://api.github.com/repos/{user}/{repo}/releases/tags/{tag}'
    
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    
    release_data = response.json()
    if not release_data.get('assets'):
        raise click.ClickException('No assets found in release')
    
    # 返回第一个资产的信息
    asset = release_data['assets'][0]
    return {
        'url': asset['url'],
        'id': asset['id'],
        'name': asset['name']
    }

def download_asset(asset_url, token, output_path):
    """下载资产文件"""
    headers = {
        'Accept': 'application/octet-stream'
    }
    if token:
        headers['Authorization'] = f'Bearer {token}'
    
    response = requests.get(asset_url, headers=headers, stream=True)
    response.raise_for_status()
    
    with open(output_path, 'wb') as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)

@click.command()
@click.argument('target')
@click.option('--tag', '-t', help='指定release标签')
@click.option('--output', '-o', help='输出文件路径')
@click.option('--token', envvar='GITHUB_TOKEN', help='GitHub API token')
def main(target, tag, output, token):
    """GitHub Release 下载工具"""
    try:
        # 解析目标
        user, repo, parsed_tag = parse_github_url(target)
        if not all([user, repo]):
            raise click.ClickException('Invalid GitHub repository format')
        
        # 使用命令行参数的tag覆盖URL中的tag
        if tag:
            parsed_tag = tag
        
        click.echo(f'正在获取 {user}/{repo} 的release信息...')
        asset_info = get_asset_info(user, repo, parsed_tag, token)
        
        # 确定输出路径
        output_path = output if output else asset_info['name']
        
        click.echo(f'正在下载 {asset_info["name"]}...')
        download_asset(asset_info['url'], token, output_path)
        
        click.echo(f'下载完成: {output_path}')
        
    except requests.exceptions.RequestException as e:
        raise click.ClickException(f'下载失败: {str(e)}')

if __name__ == '__main__':
    main()
