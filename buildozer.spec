[app]

title = 建筑材料价格查询
package.name = materialprice
package.domain = com.example
source.dir = src
source.include_exts = py,png,jpg,kv,atlas
version = 0.1

requirements = python3.10,kivy==2.1.0,pandas,numpy,openpyxl,pillow,pygments

# Python for android (p4a) branch to use
p4a.branch = master

# Bootstrap to use for android builds
p4a.bootstrap = sdl2

orientation = portrait

# Android permissions
android.permissions = INTERNET,READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE,MANAGE_EXTERNAL_STORAGE

# Android specific
android.api = 34
android.minapi = 24
android.ndk = 25c
android.ndk_api = 24
android.private_storage = True
android.skip_update = True
android.accept_sdk_license = True
android.entrypoint = org.kivy.android.PythonActivity
android.apptheme = "@android:style/Theme.NoTitleBar.Fullscreen"
android.archs = armeabi-v7a, arm64-v8a
android.release_artifact = aab
android.debug_artifact = apk
android.enable_androidx = True
android.add_compile_options = "sourceCompatibility = 1.8", "targetCompatibility = 1.8"

[buildozer]
log_level = 2
warn_on_root = 0
