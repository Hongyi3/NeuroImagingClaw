.PHONY: list catalog benchmarks test

list:
	python clawneuro.py list

catalog:
	python scripts/generate_catalog.py

benchmarks:
	python scripts/validate_benchmarks.py

test:
	python -m pytest -q
