#!/usr/bin/env python3
import os
import sys
import subprocess

# 设置构建参数
print("=== Setting Build Parameters ===")
env = os.environ.copy()
env["P4A_BRANCH"] = "master"
env["P4A_PYTHON_VERSION"] = "3.10"
env["P4A_BOOTSTRAP"] = "sdl2"
env["P4A_REQUIREMENTS"] = "kivy==2.0.0"
env["P4A_ANDROID_API"] = "29"
env["P4A_MINAPI"] = "24"
env["P4A_NDK"] = "25c"
env["P4A_NDK_API"] = "24"
env["P4A_PRIVATE_STORAGE"] = "True"
env["P4A_PACKAGE_NAME"] = "com.example.materialprice"
env["P4A_PACKAGE_VERSION"] = "0.1"
env["P4A_NAME"] = "material_price_query"
env["P4A_DEBUG"] = "True"
env["P4A_ARCH"] = "armeabi-v7a"
env["P4A_PRIVATE"] = "src"

# 执行构建
print("\n=== Building APK ===")

# 创建一个临时的 Python 脚本文件，使用英文名称避免编码问题
temp_script = '''
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import pythonforandroid.entrypoints

# 使用正确的入口点
sys.argv = [
    'python-for-android',
    'create',
    '--dist_name', 'materialprice',
    '--bootstrap', 'sdl2',
    '--requirements', 'kivy==2.0.0',
    '--arch', 'armeabi-v7a',
    '--android_api', '29',
    '--ndk', '25c',
    '--private', 'src',
    '--package', 'com.example.materialprice',
    '--name', 'material_price_query',
    '--version', '0.1',
    '--debug',
    '--ndk-api', '24',
    '--private-storage',
    '--ignore-setup-py',
    '--copy-libs'
]

# 调用主入口点
pythonforandroid.entrypoints.main()
'''

with open('temp_build.py', 'w', encoding='utf-8') as f:
    f.write(temp_script)

# 执行临时脚本
cmd = [sys.executable, 'temp_build.py']
process = subprocess.Popen(cmd, env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)

# 实时显示输出
for line in process.stdout:
    print(line, end="")

process.wait()

# 删除临时脚本
os.remove('temp_build.py')

print(f"\nBuild completed with exit code: {process.returncode}")
sys.exit(process.returncode)
