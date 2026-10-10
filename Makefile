# Shortcuts. Run `make setup` once, then `make check`.
PY ?= .venv/bin/python

.PHONY: setup test lint check engine bot clean

setup:            ## create .venv and install dependencies
	python3 -m venv .venv
	$(PY) -m pip install -r requirements-dev.txt

test:             ## run the test suite
	$(PY) -m pytest

lint:             ## static checks
	$(PY) -m ruff check src tests

check: lint test  ## everything CI runs

engine:           ## Exercise 3: run the withdrawal decision engine
	$(PY) src/withdrawal_engine.py --output-dir out/ejercicio_3

bot:              ## Exercise 4: interactive ACH bot (SCENARIO=success|r01|r03)
	$(PY) src/ach_bot.py --scenario $(or $(SCENARIO),success)

clean:
	rm -rf out .pytest_cache .ruff_cache
