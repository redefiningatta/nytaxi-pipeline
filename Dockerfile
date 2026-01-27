FROM python:3.12-slim

#install dependencies
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx / /bin/

# set workdir
WORKDIR /app

#copy dependencies files 
COPY pyproject.toml uv.lock ./

#install dependencies
RUN uv pip install --system -r pyproject.toml

#copy source code
COPY etl/ ./etl/

#command to run on container start
ENTRYPOINT ["python", "etl/load_nytaxi.py"]