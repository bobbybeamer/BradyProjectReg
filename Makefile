# Makefile for common dev tasks
.PHONY: help install migrate test runserver lint format

help:
	@echo "Available targets: install migrate test runserver format lint"

install:
	python -m venv .venv
	. .venv/bin/activate && pip install -r requirements.txt

migrate:
	. .venv/bin/activate && python manage.py migrate

test:
	. .venv/bin/activate && python manage.py test deals notifications

runserver:
	. .venv/bin/activate && python manage.py runserver

format:
	isort . && black .

lint:
	flake8 .
