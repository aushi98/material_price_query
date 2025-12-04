#!/usr/bin/env python3
import os
import sys
from pythonforandroid.build import main as p4a_main

# 设置构建参数
args = [
    "--dist_name=materialprice",
    "--bootstrap=sdl2",
    "--requirements=python3.10,kivy==2.0.0,pandas,numpy,openpyxl,pillow",
    "--arch=armeabi-v7a",
    "--android_api=31",
    "--ndk=25c",
    "--private=src",
    "--package=com.example.materialprice",
    "--name=建筑材料价格查询",
    "--version=0.1",
    "--debug",
    "--ndk-api=24",
    "--private-storage",
    "--ignore-setup-py",
    "--copy-libs",
    "--depend-dir=./.buildozer/android/platform/build-arm64-v8a_armeabi-v7a/dists/materialprice/",
    "--ndk-version=25c",
    "--sdk-dir=/root/.buildozer/android/platform/android-sdk",
    "--ndk-dir=/root/.buildozer/android/platform/android-ndk",
]

print("Running python-for-android with args:", args)

try:
    p4a_main(args)
    print("Build completed successfully!")
except Exception as e:
    print(f"Build failed with error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
