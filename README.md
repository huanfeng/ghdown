# ghdown - GitHub Release 下载工具

一个简单的命令行工具，用于下载 GitHub Release 资产。

## 安装

```bash
pip install -r requirements.txt
```

## 使用方法

1. 基本用法：
```bash
python ghdown.py user/repo
```

2. 指定tag：
```bash
python ghdown.py user/repo:v1.0
# 或
python ghdown.py user/repo --tag v1.0
```

3. 指定输出文件：
```bash
python ghdown.py user/repo -o output.zip
```

4. 使用GitHub URL：
```bash
python ghdown.py https://github.com/user/repo
```

## 环境变量

可以通过设置 `GITHUB_TOKEN` 环境变量来使用GitHub Token：
```bash
set GITHUB_TOKEN=your_token_here
```

## 注意事项

- 如果不指定tag，默认下载最新release
- 如果不指定输出文件名，将使用release资产的原始文件名
- 建议使用GitHub Token以避免API限制
