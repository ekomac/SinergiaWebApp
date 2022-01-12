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
echo "Load bulk data"
call C:\Users\jcmac\Projects\eko-software\sinergia\SinergiaDjangoWebApp\src\scripts\cmd\bulk_creation.bat
echo "add_superadmin_to_admins"
call C:\Users\jcmac\Projects\eko-software\sinergia\SinergiaDjangoWebApp\src\scripts\cmd\add_superadmin_to_admins.bat
echo "Runserver with SSL"
call C:\Users\jcmac\Projects\eko-software\sinergia\SinergiaDjangoWebApp\src\scripts\cmd\runserver_ssl.bat
