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
requirements = python3,kivy==2.3.0,plyer,pyjnius,android

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

[buildozer]
log_level = 2
warn_on_root = 1
