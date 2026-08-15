PYTHON ?= python
PIP ?= pip
UI_DIR := ui

.PHONY: install test run-daemon run-ui up down

install:
	$(PIP) install fastapi uvicorn pytest httpx

run-daemon:
	$(PYTHON) -m uvicorn daemon.main:app --host 0.0.0.0 --port 8000 --reload

run-ui:
	cd $(UI_DIR) && npm install && npm run dev -- --host 0.0.0.0 --port 3000

up:
	docker-compose up --build

down:
	docker-compose down

test:
	$(PYTHON) -m pytest daemon/tests -q
