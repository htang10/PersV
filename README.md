![Logo](https://dev-to-uploads.s3.amazonaws.com/uploads/articles/th5xamgrr6se0x5ro4g6.png)

<div align="center">
    <i>Right insights lead right actions 🎯</i>
</div>

<br>

[![Python 3.14](https://img.shields.io/badge/python-3.14-%23FFD43B?logo=python&logoColor=%234B8BBE)](https://docs.python.org/3/)
[![Java 26](https://img.shields.io/badge/java-26-%23E76F00?logo=openjdk&logoColor=white)](https://docs.oracle.com/en/java/javase/26/)

# What is PersV?

A tool that lets user ask plain-English questions to retrieve data from a relational database and get back truthful insights, without SQL knowledge. The system utilizes the power of a [Large Language Model](https://www.ibm.com/think/topics/large-language-models) (LLM) to intepret users' questions, translate them into database queries, and return answers based on available data.
## What problems does it solve?

1. **Removes technical barrier.** Non-technical users can retrieve data more effciently, less dependable on developers or need to learn SQL.

2. **Safe, hands-on SQL learning.** Non-technical users can experiment directly against their own database and learn/improve their SQL skill, without risk of accidental DML/DDL changes.

3. **Benefits technical users too.** SQL experts utilize this to sanity-check queries and discover more efficient alternatives.

4. **One language, any database.** Instead of learning a new query dialect for every database management system (DBMS), users just ask their question the same way every time, while the translation is handled underneath.

## Demo

Insert gif or link to demo

## Core user flow

1. Connect to a database
- **Demo:** Try out the main features with zero setup. [Chinook database](https://github.com/lerocha/chinook-database) was selected for demo purpose.
- **Custom:** Connect to any supported relational database of your choice, including:
  - MariaDB
  - Microsoft SQL Server
  - MySQL
  - Oracle
  - PostgreSQL
  - SQLite

> [!NOTE]
> Custom database connections are available to registered users only.

2. Ask questions in plain English → SQL agent generates SQL → Agent executes query → Agent responds with explanatory, insightful language (not raw results).

3. Register an account (optional) to unlock custom connection and query history, which includes past questions, responses and generated SQL query.

## Features

- Instant demo. Try it with zero setup
- Connect your own database (any major relational DBMS)
- Ask questions in plain English, get clear answers
- **Read-only** by design. Your data is never altered
- Optional account to save and revisit your query history (Planned)
- No database yet? Upload a file and we'll set one up for you (Planned)

## Tech Stack

**Client:**
[![React](https://img.shields.io/badge/react-%2320232a.svg?style=for-the-badge&logo=react&logoColor=%2361DAFB)](https://react.dev/)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind_CSS-black?style=for-the-badge&logo=tailwindcss&logoColor=%2306B6D4)](https://tailwindcss.com/)

**Server:**
[![FastAPI](https://img.shields.io/badge/fastapi-%23009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![PostgreSQL](https://img.shields.io/badge/postgresql-%23316192?style=for-the-badge&logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![Redis](https://img.shields.io/badge/redis-black?style=for-the-badge&logo=redis&logoColor=red)](https://redis.io)
[![LangChain Corporate](https://img.shields.io/badge/LangChain-%237FC8FF?style=for-the-badge&logo=langchaincorporate&logoColor=black)](https://www.langchain.com/)
[![Celery](https://img.shields.io/badge/celery-%2337814A?style=for-the-badge&logo=celery&logoColor=white)](https://docs.celeryq.dev/en/stable/)
[![Docker](https://img.shields.io/badge/Docker-black?style=for-the-badge&logo=docker&logoColor=%232560FF)](https://www.docker.com/)
[![Spring Boot](https://img.shields.io/badge/Spring-%236DB33F?style=for-the-badge&logo=spring&logoColor=white)](https://spring.io/)

## License

Copyright © 2026 Huy Tang. All Rights Reserved.

## Acknowledgements

- [Dataset used for demo purpose](https://github.com/lerocha/chinook-database)
- [A wonderful and easy-to-use README template](hhttps://readme.so/)
