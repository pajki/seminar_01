# Seminar assignment 1

Group Pajki

- Andraž Krašovec
- Luka Podgoršek
- Iztok Ramovš

## Initial setup

Initial setup requires only a few simple steps. To avoid any python packages issues, it
is recommended to setup a fresh virtual environment.

Clone the project.

    # Clone the project
    git clone git@github.com:pajki/seminar_01.git

Firstly we install the postgres database and create a database and user that are defined
in our project:
    
    # Firstly we install postgres itself
    sudo apt update
    sudo apt install postgresql postgresql-contrib
    
    # Then we connect to it 
    sudo su - postgres
    psql
    
    # And create a new database and user
    create database crawldb;
    create user crawldb with password 'crawldb';
    alter user crawldb with superuser;
    grant all privileges on database crawldb to crawldb;
    
    ctrl + d (leave the psql environment)
    
    # Now import the database tables and indices
    export PGPASSWORD=crawldb
    # Don't forget to change the path to the importdb.sql file!
    psql -h localhost -d crawldb -U crawldb -p 5432 -a -w -f /home/andraz/Projects/seminar_01/importdb.sql
    
Secondly we create a virtual environment (optional), install the required
packages and migrate the database to the current state.
    
    # Optionally create a fresh virtual environment (docs: https://virtualenvwrapper.readthedocs.io/en/latest/install.html)
    mkvirtualenv -p /usr/bin/python3 pajki_seminar01
    
    # Move into freshly installed directory
    cd seminar_01
    # Install the required packages
    pip install -r requirements.txt
    # Migrate the database
    python manage.py migrate
    
To run the crawler, there is a custom manage.py command. Optionally we can resume operation with restoring the frontier 
from the database by passing --restore flag. Number of threads must passed.
    
    # Run the crawler
    python manage.py startcrawler 16 
    
If we want to manage data, we can easily achieve this by accessing the Django admin.
    
    # Create super user
    python manage.py createsuperuser
    # Start the development server
    python manage.py runserver 8001
    
    # Go to localhost:8001/admin and enter the credentials you just created. You should be able to access the admin page.