[app]
title = FallasApp
package.name = fallasapp
package.domain = org.fallas.app
source.dir = .
source.include_exts = py,png,jpg,kv,json
version = 1.0
requirements = python3,kivy,kivymd
orientation = portrait
fullscreen = 1
android.permissions = INTERNET,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE

[buildozer]
log_level = 2
warn_on_root = 1
android.api = 33
android.ndk = 23b
android.arch = armeabi-v7a
android.minapi = 21