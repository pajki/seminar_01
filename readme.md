# Seminar assignment 1

Group Pajki

- Andraž Krašovec
- Luka Podgoršek
- Iztok Ramovš

## Initial setup

Initial setup requires only a few simple steps. To avoid any python packages issues, it
is recommended to setup a fresh virtual environment.

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
    grant all privileges on database crawldb to crawldb;
    
Secondly we clone the project, create a virtual environment (optional), install the required
packages and migrate the database to the current state (no extra SQL script needed).

    # Clone the project
    git clone git@github.com:pajki/seminar_01.git
    
    # Optionally create a fresh virtual environment (docs: https://virtualenvwrapper.readthedocs.io/en/latest/install.html)
    mkvirtualenv -p /usr/bin/python3 pajki_seminar01
    
    # Move into fresly installed directory
    cd seminar_01
    # Install the required packages
    pip install -r requirements.txt
    # Migrate the database
    python manage.py migrate