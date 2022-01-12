@echo off
echo "Hard reset"
echo "Reset migrations"
call C:\Users\jcmac\Projects\eko-software\sinergia\SinergiaDjangoWebApp\src\scripts\cmd\reset_migrations.bat
echo "Reset database"
call C:\Users\jcmac\Projects\eko-software\sinergia\SinergiaDjangoWebApp\src\scripts\cmd\reset_db.bat
echo "Make migrations"
call C:\Users\jcmac\Projects\eko-software\sinergia\SinergiaDjangoWebApp\src\scripts\cmd\make_and_migrate.bat
echo "Create superuser"
call C:\Users\jcmac\Projects\eko-software\sinergia\SinergiaDjangoWebApp\src\scripts\cmd\create_superuser.bat
echo "Create superuser"
call C:\Users\jcmac\Projects\eko-software\sinergia\SinergiaDjangoWebApp\src\scripts\cmd\bulk_creation.bat
echo "add_superadmin_to_admins"
call C:\Users\jcmac\Projects\eko-software\sinergia\SinergiaDjangoWebApp\src\scripts\cmd\add_superadmin_to_admins.bat
echo "Runserver with SSL"
call C:\Users\jcmac\Projects\eko-software\sinergia\SinergiaDjangoWebApp\src\scripts\cmd\runserver_ssl.bat
@REM C:\Users\jcmac\Projects\eko-software\sinergia\SinergiaDjangoWebApp\env\Scripts\activate.bat
@REM START "C:\Users\jcmac\Projects\eko-software\sinergia\SinergiaDjangoWebApp\env\Scripts\python.exe" resetmigrations.py clean --path C:\\Users\\jcmac\\Projects\\eko-software\\sinergia\\SinergiaDjangoWebApp\\src
@REM cmd "cd /d C:\Users\jcmac\Projects\eko-software\sinergia\SinergiaDjangoWebApp\env\Scripts & activate & cd /d C:\Users\jcmac\Projects\eko-software\sinergia\SinergiaDjangoWebApp\src & python manage.py reset_db"
@REM cmd /k "cd /d C:\Users\jcmac\Projects\eko-software\sinergia\SinergiaDjangoWebApp\env\Scripts & activate & cd /d C:\Users\jcmac\Projects\eko-software\sinergia\SinergiaDjangoWebApp\src & python resetmigrations.py clean --path C:\\Users\\jcmac\\Projects\\eko-software\\sinergia\\SinergiaDjangoWebApp\\src & cd /d C:\Users\jcmac\Projects\eko-software\sinergia\SinergiaDjangoWebApp\env\Scripts & activate & cd /d C:\Users\jcmac\Projects\eko-software\sinergia\SinergiaDjangoWebApp\src & python manage.py reset_db & cd /d C:\Users\jcmac\Projects\eko-software\sinergia\SinergiaDjangoWebApp\env\Scripts & activate & cd /d C:\Users\jcmac\Projects\eko-software\sinergia\SinergiaDjangoWebApp\src & python manage.py makemigrations & cd /d C:\Users\jcmac\Projects\eko-software\sinergia\SinergiaDjangoWebApp\env\Scripts & activate & cd /d C:\Users\jcmac\Projects\eko-software\sinergia\SinergiaDjangoWebApp\src & python manage.py migrate & cd /d C:\Users\jcmac\Projects\eko-software\sinergia\SinergiaDjangoWebApp\env\Scripts & activate & cd /d C:\Users\jcmac\Projects\eko-software\sinergia\SinergiaDjangoWebApp\src & python manage.py createsuperuser & cd /d C:\Users\jcmac\Projects\eko-software\sinergia\SinergiaDjangoWebApp\env\Scripts & activate & cd /d C:\Users\jcmac\Projects\eko-software\sinergia\SinergiaDjangoWebApp\src & python manage.py runscript -v 2 bulk_creation cd /d C:\Users\jcmac\Projects\eko-software\sinergia\SinergiaDjangoWebApp\env\Scripts & activate & cd /d C:\Users\jcmac\Projects\eko-software\sinergia\SinergiaDjangoWebApp\src & python manage.py runscript -v 2 add_superadmin_to_admins & cd /d C:\Users\jcmac\Projects\eko-software\sinergia\SinergiaDjangoWebApp\env\Scripts & activate & cd /d C:\Users\jcmac\Projects\eko-software\sinergia\SinergiaDjangoWebApp\src & python manage.py runserver_plus --cert-file cert.crt 0.0.0.0:8060"
pause


@REM cmd /k "
@REM cd /d C:\Users\jcmac\Projects\eko-software\sinergia\SinergiaDjangoWebApp\env\Scripts
@REM activate
@REM cd /d C:\Users\jcmac\Projects\eko-software\sinergia\SinergiaDjangoWebApp\src
@REM python resetmigrations.py clean --path C:\\Users\\jcmac\\Projects\\eko-software\\sinergia\\SinergiaDjangoWebApp\\src
@REM cd /d C:\Users\jcmac\Projects\eko-software\sinergia\SinergiaDjangoWebApp\env\Scripts
@REM activate
@REM cd /d C:\Users\jcmac\Projects\eko-software\sinergia\SinergiaDjangoWebApp\src
@REM python manage.py reset_db
@REM cd /d C:\Users\jcmac\Projects\eko-software\sinergia\SinergiaDjangoWebApp\env\Scripts
@REM activate
@REM cd /d C:\Users\jcmac\Projects\eko-software\sinergia\SinergiaDjangoWebApp\src
@REM python manage.py makemigrations
@REM cd /d C:\Users\jcmac\Projects\eko-software\sinergia\SinergiaDjangoWebApp\env\Scripts 
@REM activate
@REM cd /d C:\Users\jcmac\Projects\eko-software\sinergia\SinergiaDjangoWebApp\src
@REM python manage.py migrate
@REM cd /d C:\Users\jcmac\Projects\eko-software\sinergia\SinergiaDjangoWebApp\env\Scripts
@REM activate
@REM cd /d C:\Users\jcmac\Projects\eko-software\sinergia\SinergiaDjangoWebApp\src
@REM python manage.py createsuperuser
@REM cd /d C:\Users\jcmac\Projects\eko-software\sinergia\SinergiaDjangoWebApp\env\Scripts
@REM activate
@REM cd /d C:\Users\jcmac\Projects\eko-software\sinergia\SinergiaDjangoWebApp\src
@REM python manage.py runscript -v 2 bulk_creation
@REM cd /d C:\Users\jcmac\Projects\eko-software\sinergia\SinergiaDjangoWebApp\env\Scripts
@REM activate
@REM cd /d C:\Users\jcmac\Projects\eko-software\sinergia\SinergiaDjangoWebApp\src
@REM python manage.py runscript -v 2 add_superadmin_to_admins
@REM cd /d C:\Users\jcmac\Projects\eko-software\sinergia\SinergiaDjangoWebApp\env\Scripts
@REM activate
@REM cd /d C:\Users\jcmac\Projects\eko-software\sinergia\SinergiaDjangoWebApp\src
@REM python manage.py runserver_plus --cert-file cert.crt 0.0.0.0:8060