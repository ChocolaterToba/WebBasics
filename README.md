# WebBasics
Repo for Tachnopark's Basics in Web Development course
Prepare venv:
- $ python3 -m venv venv
- $ source venv/bin/activate
- $ python3 -m pip install -r requirements.txt

To launch website itself:
- $ python manage.py runserver
OR
- $ gunicorn AskAglicheev.wsgi
- $ nginx with additional config provided in AskAglicheev.conf

To launch simple "Hello, World" wsgi script:
- $ gunicorn -c wsgi_hello_world.conf.py wsgi_hello_world:hello_world
It will be accessible with localhost/8080
