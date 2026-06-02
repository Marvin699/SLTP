import subprocess
import sys
import os
import shutil

def main():
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    # 清理旧的构建目录
    if os.path.exists('dist'):
        shutil.rmtree('dist')
    if os.path.exists('build'):
        shutil.rmtree('build')
    
    # 收集所有需要打包的目录
    add_data_args = []
    
    # 需要打包的目录列表
    dirs_to_include = [
        'app/models',
        'app/api',
        'app/services',
        'app/schemas',
        'app/core',
    ]
    
    # 检查并添加存在的目录
    for dir_path in dirs_to_include:
        if os.path.exists(dir_path):
            if sys.platform == 'win32':
                add_data_args.extend(['--add-data', f'{dir_path};{dir_path}'])
            else:
                add_data_args.extend(['--add-data', f'{dir_path}:{dir_path}'])
        else:
            print(f"Warning: Directory {dir_path} not found, skipping...")
    
    # 构建命令
    cmd = [
        'pyinstaller',
        '--onefile',
        '--name', 'drone-planner',
        *add_data_args,
        'app/main.py'
    ]
    
    print(f"Running command: {' '.join(cmd)}")
    subprocess.run(cmd, check=True)
    print("Backend build completed successfully!")
    
    # 验证输出
    exe_name = 'drone-planner.exe' if sys.platform == 'win32' else 'drone-planner'
    if os.path.exists(f'dist/{exe_name}'):
        print(f"OK: Output file created: dist/{exe_name}")
    else:
        print(f"ERROR: Output file not found: dist/{exe_name}")

if __name__ == '__main__':
    main()
