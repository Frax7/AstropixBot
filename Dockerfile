FROM python:3.10.0a6-slim-buster

# Make a directory for the bot
WORKDIR /astropixbot

# Install dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy our source code
COPY /bot .

# Run the bot
CMD ["python", "AstropixBot.py"]