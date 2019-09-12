[![CircleCI](https://circleci.com/gh/landvilleng/landville-backend-web-api.svg?style=svg&circle-token=0b67e7bdea3b38a5b4be3154613c500fb0ba12db)](https://circleci.com/gh/landvilleng/landville-backend-web-api) [![Coverage Status](https://coveralls.io/repos/github/landvilleng/landville-backend-web-api/badge.svg?branch=develop&t=8IKdIj)](https://coveralls.io/github/landvilleng/landville-backend-web-api?branch=develop)
<a href="https://codeclimate.com/github/landvilleng/landville-backend-web-api/maintainability"><img src="https://api.codeclimate.com/v1/badges/6ff3cfebdbf6655c3da0/maintainability" /></a>

# landville-backend-web-api

Backend Repository for LandVille Project

# Description

- landVille is a simple mobile-enabled solution that helps people access real estate investing with ease and convenience. landVille provides users and investors with an intelligent and most predictive search tool for properties in Nigeria, access to saving models and financing, smart contract and documentation and Our technology has four basic value proposition: search capability for safe and most trusted trending properties, saving and access to financing, smart contract and documentation, credit rating tool

## Documentation

- List of endpoints exposed by the service

| Method | Endpoint                                           | Description                                              |
| ------ | -------------------------------------------------- | -------------------------------------------------------- |
| POST   | /landville/adm/                                    | log in Admin                                             |
| POST   | /api/v1/auth/register/                             | registers new users by email                             |
| GET    | /api/v1/auth/verify/                               | activates a users account                                |
| POST   | /api/v1/auth/login/                                | logs in a user by email                                  |
| POST   | /api/v1/auth/google/                               | user signs in through google                             |
| POST   | /api/v1/auth/twitter/                              | user signs in through twitter                            |
| POST   | /api/v1/auth/facebook/                             | user signs in through facebook                           |
| POST   | /api/v1/auth/client/                               | application for client company                           |
| GET    | /api/v1/auth/clients/                              | Fetch all client companies                               |
| POST   | /api/v1/auth/password-reset/                       | user gets a reset password link                          |
| POST   | /api/v1/pay/card-pin/                              | initiate payment with local Nigerian cards, with PIN     |
| POST   | /api/v1/pay/card-foreign/                          | initiate payment with foreign cards                      |
| POST   | /api/v1/pay/validate-card/                         | validate payment with local Nigerian cards, with PIN     |
| PATCH  | /api/v1/auth/password-reset/                       | user resets password                                     |
| POST   | /api/v1/transcations/accounts                      | post account details by Client                           |
| GET    | /api/v1/transcations/accounts                      | Get account details depending on User level              |
| GET    | /api/v1/transcations/account/<account_number>      | Get a single account details entry                       |
| PUT    | /api/v1/transcations/account/<account_number>      | Update a single account detail entry                     |
| DELETE | /api/v1/transcations/account/<account_number>      | Delete a single account detail entry                     |
| POST   | /api/v1/transactions/tokenized-card/<saved_card_id> | Make payment with tokenized card  
| GET   | /api/v1/transactions/saved-cards/                  | Get a user's saved cards  
| DELETE   | /api/v1/transactions/saved-cards/<saved_card_id> | Delete specific saved card |
| GET    | /api/v1/properties/                                | get all property                                         |
| POST   | /api/v1/properties/                                | create a property page                                   |
| GET    | /api/v1/properties/get/<slug>/                     | get specific property                                    |
| DELETE | /api/v1/properties/get/<slug>/                     | delete specific property                                 |
| PATCH  | /api/v1/properties/get/<slug>/                     | update specific property                                 |
| DELETE | /api/v1/properties/buyer-list/<slug>/              | remove property with slug from current user's buyer list |
| POST   | /api/v1/properties/buyer-list/<slug>/              | add property with slug to current user's buyer list      |
| GET    | /api/v1/properties/buyer-list/                     | get properties in current user's buyer list              |
| GET    | /api/v1/properties/trending/?address=City          | get all trending properties in a particular location     |
| PUT    | /api/v1/properties/enquiries/<enquiry_id>/         | Update a property Enquiry                                |
| POST   | api/v1/propertis/enquiries/<property_slug>/create/ | Post a property enquiry                                  |
| DELETE | api/v1/properties/enquiries/<enquiry_id>/          | Delete an enquiry                                        |
| GET    | api/v1/properties/enquiries/all/                   | get all your enquiries                                   |
| GET    | api/v1/properties/enquiries/<enquiry_id>/          | get one enquiry                                          |
| DELETE | api/v1/properties/:slug/resource                   | delete a cloudinary resource                             |
| GET    | api/v1/auth/profile/                               | gets a profile of the loggedin user                      |
| PATCH  | api/v1/auth/profile/                               | edits a profile of the loggedin user                     |
| GET    | api/v1/transactions/                               | get a users transaction details                          |

## API Documentation

https://landville-backend-web-api.herokuapp.com/

The heroku link redirects direclty to our documentation With these documentation, One can be able to test all endpoint as mentioned above in a browser

## Setup

- Step by step instructions on how to get the code setup locally. This may include:

  ### Description:

- *Celery* is a task queue with focus on real-time processing, while also supporting task scheduling.
- *Redis* is a message broker. This means it handles the queue of "messages" between Django and Celery.
- All two work together to make real-time magic.
- This module contains the Celery application instance for this project, we take configuration from Django settings and use autodiscover_tasks to find task modules inside all packages listed in INSTALLED_APPS.

      ### Installing requirements

  The settings file assumes that rabbitmq-server is running on localhost using the default ports.

### Dependencies

    - python3.7
    - python3
    - pip3
    - django 2.2.1
    - celery
    - redis

### Getting Started

- First clone the project to your local machine using `git clone https://github.com/landvilleng/landville-backend-web-api.git`
- Create a virtual environment using the following command : `python3 -m venv /path/to/new/virtual/environment`
- Activate your virtual environment using `source (virtualenv name)/bin/activate`
- Create a new branch from the develop branch using the command `git checkout -b your_branch_name`
- Install project requirements using `pip install -r requirements.txt`
- To create a dot_env file `.env`, run the command `cp .env_sample .env` so that the `.env_sample` file can be copied to `.env`.
- Edit the `.env` file with your own credentials. Eg : database username, password ,etc
- Make sure you have `export REDIS_URL="redis://localhost:6379"` in your .env file.
  (this allows the celery to connect with redis.)
- Set your environement variable by running the following command `source .env`
- Create a Postgres database with the name you put in the `.env` file
- Run the command `python manage.py migrate` to create database tables
- Download Redis
  - Using Homebrew:  `$ brew install redis`
  - Start Redis server  `$ brew services start redis`
- Open & Test Redis:
  `$ redis-server`
- Run worker:
  `` $ celery -A yourproject worker -l info` `` \* example
  `$ celery -A landville worker -l info`
- Run command `python manage.py runserver` to start the project

### Run The Service

- List of steps to run the service (e.g. docker commands)

### Microservices

- List out the microservices if any that this repo uses(This will include the payment service we shall be using)

## Testing

- To run tests without coverage run `python manage.py test`
- To run tests with coverage run `coverage run --source='authentication/,property/,transactions/,pages/,' manage.py test && coverage report`

## Contribute

- For contributions to this project, reach out

## Deployment

- This project has been depolyed on heroku:
  link(https://landville-backend-web-api.herokuapp.com/)
