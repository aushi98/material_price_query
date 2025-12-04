[app]

title = 建筑材料价格查询
package.name = materialprice
package.domain = com.example
source.dir = src
source.include_exts = py
version = 0.1

# 只包含最基本的依赖
requirements = python3.10,kivy==2.0.0

p4a.branch = master
p4a.bootstrap = sdl2

orientation = portrait

# 只包含最基本的 Android 配置
android.api = 29
android.minapi = 24
android.ndk = 25c
android.private_storage = True
android.skip_update = True
android.accept_sdk_license = True
android.entrypoint = org.kivy.android.PythonActivity
android.archs = armeabi-v7a
android.debug_artifact = apk

[buildozer]
log_level = 2
warn_on_root = 0
