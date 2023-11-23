# Bibliotheque-E REST API

This is a RESTful service

## Pre-requisites

* Python3

## Steps

### Clone repo

```bash
git clone https://github.com/JosephAyo/bibliotheque-e-backend && cd bibliotheque-e-backend
```

### Create gitignored files

They are:

* .env using the .env.example as a template

### Create virtual environment

```bash
python3 -m venv <venv_name>
```

#### *NB: you may have to use python3 in place of python, if you are using python version 3*

### Activate the virtual environment

```bash
source ./<venv_name>/bin/activate
```

### Install requirements

```bash
pip install -r requirements.txt
```

### Run the application

```bash
python3 run_server.py
```
