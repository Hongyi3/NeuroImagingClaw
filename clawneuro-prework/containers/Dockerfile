FROM python:3.11-slim

WORKDIR /workspace
COPY pyproject.toml README.md /workspace/
COPY src /workspace/src
COPY skills /workspace/skills
COPY scripts /workspace/scripts
COPY benchmarks /workspace/benchmarks
COPY tests /workspace/tests
COPY clawneuro.py /workspace/

RUN pip install --no-cache-dir -e .[dev]

CMD ["python", "clawneuro.py", "list"]
