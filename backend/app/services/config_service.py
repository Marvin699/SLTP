"""配置信息保存/加载服务 — 存储到 LLM 文件夹"""
import os
from datetime import datetime

# LLM 文件夹路径
LLM_DIR = os.path.join(os.path.dirname(__file__), '..', '..', 'LLM')
os.makedirs(LLM_DIR, exist_ok=True)


def get_llm_dir():
    return os.path.abspath(LLM_DIR)


def list_configs():
    """列出 LLM 文件夹中所有配置文件"""
    files = []
    for f in sorted(os.listdir(LLM_DIR)):
        if f.endswith('.md'):
            path = os.path.join(LLM_DIR, f)
            stat = os.stat(path)
            files.append({
                'filename': f,
                'size': stat.st_size,
                'modified': datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S'),
            })
    return files


def save_config(filename: str, content: str) -> dict:
    """保存配置文件"""
    if not filename.endswith('.md'):
        filename += '.md'
    # 清理文件名
    filename = filename.replace('/', '_').replace('\\', '_')
    path = os.path.join(LLM_DIR, filename)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    return {'filename': filename, 'size': len(content.encode('utf-8'))}


def load_config(filename: str) -> str:
    """加载配置文件"""
    path = os.path.join(LLM_DIR, filename)
    if not os.path.exists(path):
        raise FileNotFoundError(f'文件不存在: {filename}')
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()


def delete_config(filename: str) -> bool:
    """删除配置文件"""
    path = os.path.join(LLM_DIR, filename)
    if os.path.exists(path):
        os.remove(path)
        return True
    return False
