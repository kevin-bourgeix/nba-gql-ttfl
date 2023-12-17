venv:
	python3 -m venv .venv
	chmod +x .venv/bin/activate
	source .venv/bin/activate

install:
	pip install -r requirements.txt

requirements:
	pip freeze > requirements.txt
	
dev:
	uvicorn main:app

run: venv install dev