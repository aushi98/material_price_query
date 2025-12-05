[app]

title = Material Price Query
package.name = materialprice
package.domain = com.example
source.dir = src
source.include_exts = py
version = 0.1

requirements = python3.10,kivy==2.0.0

p4a.branch = master
p4a.bootstrap = sdl2

orientation = portrait

android.permissions = INTERNET,READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE,MANAGE_EXTERNAL_STORAGE

android.api = 31
android.minapi = 24
android.ndk = 25c
android.private_storage = True
android.skip_update = True
android.accept_sdk_license = True
android.entrypoint = org.kivy.android.PythonActivity
android.archs = armeabi-v7a
android.debug_artifact = apk
android.release_artifact = apk
android.build_tools_version = 31.0.0

[buildozer]
log_level = 2
warn_on_root = 0
