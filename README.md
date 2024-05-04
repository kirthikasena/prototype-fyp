# Prototype-FYP

## Introduction

This document provides instructions on how to set up and run the application locally.

## Prerequisites

- **Node.js**: Ensure Node.js is installed on your machine. You can download it from [nodejs.org](https://nodejs.org/).
- **Python**: Required as the project involves Python scripts. Install it from [python.org](https://www.python.org/).

## install libraries for python scripts

```bash
cd my-backend
pip install -r requirements.txt # Install all required packages
```

## add environment variables-set up Hugging face token(already one-setup here)

Note: if github clone: then this setup is necessary

```bash

# create .env file
touch .env  # Unix/macOS
type nul > .env  # Windows

# Edit the .env File
nano .env  # or vim .env

# Add the hugging face token with the exact variable name
HUGGINGFACE_TOKEN=your_hugging_face_token_here

```

## Getting Started

### Backend Set-up

```bash
cd my-backend
npm install
node index.js
```

### Frontend Set-up

```bash
cd website
npm install
npm start
```

### the sample review file to upload in the application

the csv file of reviews and the format is given with the name :'sample_reviews'

### Reviwing the prompts in the study:

the template.py file in the my-backend folder - consists of the necssary prompts to interact with LLM
