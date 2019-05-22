[![CircleCI](https://circleci.com/gh/landvilleng/landville-backend-web-api.svg?style=svg&circle-token=0b67e7bdea3b38a5b4be3154613c500fb0ba12db)](https://circleci.com/gh/landvilleng/landville-backend-web-api) [![Coverage Status](https://coveralls.io/repos/github/landvilleng/landville-backend-web-api/badge.svg?branch=develop&t=8IKdIj)](https://coveralls.io/github/landvilleng/landville-backend-web-api?branch=develop)

# landville-backend-web-api

Backend Repository for LandVille Project

# Description

* landVille is a simple mobile-enabled solution that helps people access real estate investing with ease and convenience. landVille provides users and investors with an intelligent and most predictive search tool for properties in Nigeria, access to saving models and financing, smart contract and documentation and  Our technology has four basic value proposition: search capability for safe and most trusted trending properties, saving and access to financing, smart contract and documentation, credit rating tool

## Documentation

* List of endpoints exposed by the service


## API Documentation
https://landville-backend-web-api.herokuapp.com/ 

The heroku link redirects direclty to our documentation With these documentation, One can be able to test all endpoint as mentioned above in a browser

## Setup

* Step by step instructions on how to get the code setup locally. This may include:

### Dependencies

* python3
* pip3
* django 2.2.1

### Getting Started

* first clone the project to your local machine using  `git clone https://github.com/landvilleng/landville-backend-web-api.git`
* create a virtual environment and activate your virtual environment using `source (virtualenv name)/bin/activate`
* create a new branch from the develop branch using the command `git checkout -b your_branch_name`
* Install project requirements using `pip install -r requirements.txt`
* To create a dot_env file, populate .env_sample and then run the command `cp .env_sample .env && source .env` so that the .env_sample file can be     copied to .env.  
* Create a Postgres database as described in the sample.env file
* Run command `python manage.py runserver` to start the project


### Run The Service

* List of steps to run the service (e.g. docker commands)

### Microservices

* List out the microservices if any that this repo uses(This will include the payment service we shall be using)

## Testing
* To run tests without coverage run `python manage.py test`
* To run tests with coverage run `coverage run --source='landville/' manage.py test && coverage report`

## Contribute

* For contributions to this project, reach out

## Deployment

* This project has been depolyed on heroku:
link(https://landville-backend-web-api.herokuapp.com/)

