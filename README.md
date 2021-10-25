# WebBasics
Repo for Tachnopark's Basics in Web Development course
Prepare venv:
- $ python3 -m venv venv
- $ source venv/bin/activate
- $ sudo apt-get -y install build-essential
- $ sudo apt-get -y install libpq-dev python-dev python3-dev
- $ python3 -m pip install -r requirements.txt

Prepare database:
- $ python3 manage.py migrate
- $ apt-get install -y pgbouncer
- create file userlist.txt with database's username and password, for example
- "thisismyusername" "this is my password"
- generate ssl key and certificate, change related paths in pgbouncer.ini
- $ pgbouncer -d pgbouncer.ini

To launch website itself:
- $ python manage.py runserver
OR
- $ gunicorn AskAglicheev.wsgi
- $ nginx with additional config provided in AskAglicheev.conf

To launch simple "Hello, World" wsgi script:
- $ gunicorn -c wsgi_hello_world.conf.py wsgi_hello_world:hello_world
It will be accessible with localhost/8080
