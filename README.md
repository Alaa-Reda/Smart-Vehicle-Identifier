# Visual Question Answering API

## Description
Backend API for answering questions about images using Qwen3-VL model.

## Installation

Install requirements:

pip install -r requirements.txt

## Run

python -m uvicorn backend.main:app --reload

## API

Open:

http://127.0.0.1:8000/docs

Use POST /predict to upload image and ask question.