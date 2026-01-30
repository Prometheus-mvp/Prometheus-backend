# Run from repo root. Install deps first: pip install -r requirements.txt

.PHONY: lint format

lint:
	ruff check .

format:
	ruff format .
	ruff check --fix .
