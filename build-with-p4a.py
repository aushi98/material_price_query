#!/usr/bin/env python3
import os
import sys
import subprocess

# 安装必要的依赖
print("=== Installing Dependencies ===")
subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", "python-for-android"], check=True)

# 设置构建参数
print("\n=== Setting Build Parameters ===")
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
env["P4A_NAME"] = "建筑材料价格查询"
env["P4A_DEBUG"] = "True"
env["P4A_ARCH"] = "armeabi-v7a"
env["P4A_PRIVATE"] = "src"

# 执行构建
print("\n=== Building APK ===")
cmd = [
    "python-for-android", "create",
    "--dist_name", "materialprice",
    "--bootstrap", env["P4A_BOOTSTRAP"],
    "--requirements", env["P4A_REQUIREMENTS"],
    "--arch", env["P4A_ARCH"],
    "--android_api", env["P4A_ANDROID_API"],
    "--ndk", env["P4A_NDK"],
    "--private", env["P4A_PRIVATE"],
    "--package", env["P4A_PACKAGE_NAME"],
    "--name", env["P4A_NAME"],
    "--version", env["P4A_PACKAGE_VERSION"],
    "--debug",
    "--ndk-api", env["P4A_NDK_API"],
    "--private-storage",
    "--ignore-setup-py",
    "--copy-libs"
]

print("Running command:", " ".join(cmd))

process = subprocess.Popen(cmd, env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)

# 实时显示输出
for line in process.stdout:
    print(line, end="")

process.wait()

# 显示构建结果
print("\n=== Build Result ===")
if os.path.exists("./dist"):
    subprocess.run(["ls", "-la", "./dist"], check=True)
else:
    print("dist directory does not exist")

# 显示build目录结果
if os.path.exists("./.buildozer"):
    print("\n=== Buildozer Directory ===")
    subprocess.run(["ls", "-la", "./.buildozer"], check=True)

# 显示错误日志（如果存在）
log_path = "./.buildozer/android/app/build/outputs/logs/build.log"
if os.path.exists(log_path):
    print("\n=== Build Log ===")
    subprocess.run(["cat", log_path], check=True)

print(f"\nBuild completed with exit code: {process.returncode}")
sys.exit(process.returncode)
