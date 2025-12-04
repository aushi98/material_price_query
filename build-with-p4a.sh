#!/bin/bash

# 安装必要的依赖
echo "=== Installing Dependencies ==="
pip install --upgrade python-for-android

# 设置构建参数
echo "\n=== Setting Build Parameters ==="
export P4A_BRANCH=master
export P4A_PYTHON_VERSION=3.10
export P4A_BOOTSTRAP=sdl2
export P4A_REQUIREMENTS="kivy==2.0.0"
export P4A_ANDROID_API=29
export P4A_MINAPI=24
export P4A_NDK=25c
export P4A_NDK_API=24
export P4A_PRIVATE_STORAGE=True
export P4A_PACKAGE_NAME="com.example.materialprice"
export P4A_PACKAGE_VERSION="0.1"
export P4A_NAME="建筑材料价格查询"
export P4A_DEBUG=True
export P4A_ARCH="armeabi-v7a"
export P4A_PRIVATE="src"

# 执行构建
echo "\n=== Building APK ==="
python-for-android create --dist_name materialprice --bootstrap $P4A_BOOTSTRAP --requirements $P4A_REQUIREMENTS --arch $P4A_ARCH --android_api $P4A_ANDROID_API --ndk $P4A_NDK --private $P4A_PRIVATE --package $P4A_PACKAGE_NAME --name "$P4A_NAME" --version $P4A_PACKAGE_VERSION --debug --ndk-api $P4A_NDK_API --private-storage --ignore-setup-py --copy-libs

# 显示构建结果
echo "\n=== Build Result ==="
ls -la ./dist
