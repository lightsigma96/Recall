FROM python:3.12-slim

WORKDIR /recall

COPY main_requirements.txt .

RUN pip install --no-cache-dir -r main_requirements.txt

COPY . .

CMD ["python", "game_loop.py"]

