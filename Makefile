PROJECT_NAME := mcu_calendar
SOURCE :=  $(wildcard $(PROJECT_NAME)/**/*.py) $(wildcard $(PROJECT_NAME)/*.py)

all: test lint run

run:
	$(info )
	$(info ************  Running        ************)
	@python $(PROJECT_NAME)/main.py

force:
	$(info )
	$(info ************  Running(force) ************)
	@python $(PROJECT_NAME)/main.py --force

dry:
	$(info )
	$(info ************  Running(force) ************)
	@python $(PROJECT_NAME)/main.py --dry

test:
	$(info )
	$(info ************  Running Tests  ************)
	@python -m pytest

lint:
	$(info )
	$(info ************  Linting        ************)
	pylint $(PROJECT_NAME)
	flake8 $(PROJECT_NAME) --config ./setup.cfg

init:
	pip3 install -r requirements.txt

clean:
	rm -rf ./$(PROJECT_NAME)/__pycache__/
	rm -rf ./tests/__pycache__/
	rm -rf ./.pytest_cache/
	rm -rf ./build/
	rm -rf ./*.egg-info/