[app]
title = Rush Runner
package.name = rushrunner
package.domain = com.rushrunner.game
source.dir = .
source.include_exts = py,png,wav,json
source.exclude_dirs = .github,bin,.buildozer,__pycache__,tests
source.exclude_patterns = test_*.py,generate_assets.py,README*
version = 1.0.0
icon.filename = assets/icons/icon.png

# plyer reads the real Android accelerometer (SensorManager) through pyjnius.
requirements = python3==3.11.5,hostpython3==3.11.5,kivy==2.3.0,plyer,pyjnius,android

orientation = portrait
fullscreen = 1

# Fully offline: NO permissions requested (no INTERNET).
android.permissions =
android.api = 33
android.minapi = 21
android.ndk = 25b
android.archs = arm64-v8a, armeabi-v7a
android.accept_sdk_license = True
android.allow_backup = False
android.logcat_filters = *:S python:D

# Pin python-for-android to a release known to work with Python 3.11 + Kivy 2.3.0
p4a.branch = v2024.01.21

[buildozer]
log_level = 2
warn_on_root = 1
