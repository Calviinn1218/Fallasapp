[app]
title = FallasApp
package.name = fallasapp
package.domain = org.fallas.app
source.dir = .
source.include_exts = py,png,jpg,kv,json
version = 1.0
requirements = python3,kivy
orientation = portrait
fullscreen = 1
android.permissions = WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE
android.minapi = 21
android.api = 33
android.ndk = 25b
android.arch = armeabi-v7a
# Esto es necesario si usas JSON, datetime o cualquier otra librería adicional
android.requirements = kivy,pyjnius

[buildozer]
log_level = 2
warn_on_root = 1