# buildozer.spec  (APK বানাতে এটি লাগবে)
[app]
title           = FF Panel
package.name    = ffpanel
package.domain  = org.ffpanel
source.dir      = .
source.include_exts = py,png,jpg,kv,atlas
version         = 1.0

requirements    = python3,kivy

orientation     = portrait
fullscreen       = 1

android.permissions = SYSTEM_ALERT_WINDOW,FOREGROUND_SERVICE
android.api         = 31
android.minapi      = 21
android.arch        = arm64-v8a

[buildozer]
log_level = 2
