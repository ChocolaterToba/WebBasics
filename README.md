# WebBasics
Repo for Tachnopark's Basics in Web Development course

To launch website itself:
- run python manage.py runserver
OR
- run gunicorn AskAglicheev.wsgi
- run nginx with additional config provided in AskAglicheev.conf

To launch simple "Hello, World" wsgi script:
- run gunicorn -c wsgi_hello_world.conf.py wsgi_hello_world:hello_world
It will be accessible with localhost/8080
