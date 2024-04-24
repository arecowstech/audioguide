# Use an official Python runtime as a parent image
FROM python:3.12-slim

# Set environment varibles
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set work directory
WORKDIR /app

# Install dependencies
RUN pip install --upgrade pip
RUN pip install poetry
COPY ./pyproject.toml /app/pyproject.toml
RUN poetry config virtualenvs.create false &&
    poetry install --no-interaction --no-ansi

# Copy project
COPY . /app/

# Run the application
CMD ["poetry", "run", "develop"]
