echo off
"c:\Program Files (x86)\Google\google_appengine\appcfg.py" delete_version -A lorepocorporate -V %1
"c:\Program Files (x86)\Google\google_appengine\appcfg.py" update src/app.yaml src/backup.yaml src/download.yaml src/localization.yaml