# scrum-poker

Welcome!

## Prerequisites before running this project:
1. Python3 (https://www.python.org/downloads/)
2. Docker (https://docs.docker.com/docker-for-mac/install/)

## Steps to run the project
1. Download/Clone the repository
`git clone https://github.com/hamzehd/scrum-poker.git` -> `cd scrum_poker`

2. If you do not have virtualenv package installed ->
`pip3 install virtualenv`

3. Create virtual environment
`virtualenv -p python venv` -> `source venv/bin/activate`

4. Install python packages
`pip install -r pip/requirements.txt`

5. Create DB/Migrations
`python manage.py migrate`

6. Run redis `docker run -p 6379:6379 -d redis:5`

7. To create an admin user: `python manage.py createsuperuser`

## What's included
1. Django 3.1.6 https://docs.djangoproject.com
2. Django Channels 3.0.3 http://channels.readthedocs.io/en/stable/
3. Django Channels Redis 3.2.0
4. Django Crispy Forms 1.11.0 http://django-crispy-forms.readthedocs.io/en/latest/
5. Bootstrap4 https://getbootstrap.com/