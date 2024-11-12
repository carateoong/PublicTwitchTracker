FROM python:3.11.4
# Or any preferred Python version.
ENV PYTHONUNBUFFERED=1
COPY .. .
RUN pip install SQLAlchemy psycopg2 psycopg2-binary python-dotenv twitchAPI twitchio discord discord.py asyncio requests pytz
CMD ["python", "./bot.py"]
# Or enter the name of your unique directory and parameter set.