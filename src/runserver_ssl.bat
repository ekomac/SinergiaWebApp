@echo off
cmd /k "cd /d C:\Users\jcmac\Projects\eko-software\sinergia\SinergiaDjangoWebApp\env\Scripts & activate & cd /d    C:\Users\jcmac\Projects\eko-software\sinergia\SinergiaDjangoWebApp\src & python manage.py runserver_plus --cert-file cert.crt 0.0.0.0:8060"
pause