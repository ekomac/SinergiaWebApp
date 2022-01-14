@echo off
@REM cmd /c "cd /d %SinergiaDjangoWebApp%\env\Scripts"
@REM echo %CD%
@REM @REM cmd /c "cd.. & cd.. & cd src & python manage.py reset_migrations"
cmd /c "cd.. /d C:\Users\jcmac\Projects\eko-software\sinergia\SinergiaDjangoWebApp\env\Scripts & activate & cd /d C:\Users\jcmac\Projects\eko-software\sinergia\SinergiaDjangoWebApp\src & python resetmigrations.py clean --path C:\\Users\\jcmac\\Projects\\eko-software\\sinergia\\SinergiaDjangoWebApp\\src"
pause