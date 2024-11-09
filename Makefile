PROJECT_NAME := mcu_calendar
SOURCE :=  $(wildcard *.py) $(wildcard $(PROJECT_NAME)/*.py) $(wildcard $(PROJECT_NAME)/**/*.py)
TEST_SOURCE := $(wildcard tests/**/*.py) $(wildcard tests/*.py)

all: test lint run

run:
	$(info )
	$(info ************  Running        ************)
	@python main.py

webscrape:
	$(info )
	$(info ************  Running        ************)
	@python get_new_media.py

force:
	$(info )
	$(info ************  Running(force) ************)
	@python main.py --force

dry:
	$(info )
	$(info ************  Running(force) ************)
	@python main.py --dry

test:
	$(info )
	$(info ************  Running Tests  ************)
	@python -m pytest

lint:
	$(info )
	$(info ************  Linting        ************)
	pylint $(SOURCE) --score=no --rcfile ./pyproject.toml
	flake8 $(SOURCE) $(TEST_SOURCE) --config ./setup.cfg

init:
	pip3 install -r requirements.txt

clean:
	rm -rf ./$(PROJECT_NAME)/__pycache__/
	rm -rf ./tests/__pycache__/
	rm -rf ./.pytest_cache/
	rm -rf ./build/
	rm -rf ./*.egg-info/
