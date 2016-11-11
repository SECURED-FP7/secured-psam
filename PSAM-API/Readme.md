# PSAM-API Installation

The PSAM-API is in charge of the internal logic making a set of validation and completeness checks, and trigger the communication with the PSAR through the API.

## Preparing Django Server:
Clone the repository into a new directory (i.e. git) and create a django project in another directory
(i.e. psam)

		sudo apt-get install mysql-server libmysqlclient -dev python-virtualenv libffi -dev
		# Choose protocol and credentials for clone , git :// or https ://
		git clone https://gitlab.secured-fp7.eu/secured/psam.git
			virtualenv.env
			source .env/bin/activate
			pip install django djangorestframework MySQL-python django-rest-swagger wrapt bcrypt python-keystoneclient
			cd psam

Create the database (choose your own DATABASE_USER and DATABASE_PASS):

		mysql -u root -p
		mysql> CREATE DATABASE PSAM;
		mysql> GRANT ALL PRIVILEGES ON PSAM.* TO 'DATABASE_USER'@'localhost' IDENTIFIED BY 'DATABASE_PASS';
		mysql> GRANT ALL PRIVILEGES ON PSAM.* TO 'DATABASE_USER'@'%'IDENTIFIED BY 'DATABASE_PASS';
		mysql> exit

Modify the database information on psam/settings.py:

	DATABASES = {
		'default': {
			'ENGINE ': 'django.db.backends.mysql',
			'NAME':' PSAM',
			'USER': 'DATABASE_USER',
			'PASSWORD': 'DATABASE_PASS',
			'HOST': 'localhost', # Or an IP Address that your DB is hosted on
			'PORT': '3306',
			}
		}

Synchronize the database

		export DATABASE_USER=DATABASE_USER
		export DATABASE_PASS=DATABASE_PASS
		python manage .py makemigrations psam
		python manage .py migrate

To show a SECURED-themed documentation page, copy the files in the directory "change_doc" in the corresponding place:

		cp change_doc/base.html .env/lib/python2.7/site-packages/rest_framework_swagger/templates/rest_framework_swagger/base.html
		cp change_doc/logo_small.png .env/lib/python2.7/site-packages/rest_framework_swagger/static/rest_framework_swagger/images/logo_small .png
		cp change_doc/screen.css .env/lib/python2.7/site-packages/rest_framework_swagger/static/rest_framework_swagger/css/screen.css
		cp change_doc/rest_framework_swagger.css .env/lib/python2.7/site-packages/rest_framework_swagger/static/rest_framework_swagger/css/rest_framework_swagger.css

Modify the psar information on psam.conf:

		[general]
		your_ip = YOUR_IP

		[PSAR]
		psar_ip = http://PSAR_IP:8080

Now you can run the server (make sure you have virtualenv active):

		python manage.py runserver YOUR_IP:8083

If you want to run in background use screen application:

		screen -S PSAM
		source .env/bin/activate
		cd $HOME/psam
		python manage.py runserver YOUR_IP:8083
