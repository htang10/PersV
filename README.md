<div align="center">
    <i>Right insights lead right actions 🎯</i>
</div>

<br>

[![Python 3.14](https://img.shields.io/badge/python-3.14-%23FFD43B?logo=python&logoColor=%234B8BBE)](https://docs.python.org/3/)

## What is PersV? 🤔

A tool that enables users to ask plain-English questions to retrieve data from a relational database and get back truthful insights, without SQL knowledge. It utilizes the power of a [Large Language Model](https://www.ibm.com/think/topics/large-language-models) (LLM) to interpret users' questions, translate them into database queries, and return answers based on available data.

## What problems does it solve? 💡

1. **Removes technical barrier.** Non-technical users can retrieve data more efficiently, without waiting on a developer or learning SQL.

2. **Safe, hands-on SQL learning.** Non-technical users can experiment directly against their own database and learn/improve their SQL skill, without risk of accidental DML/DDL changes.

3. **Benefits technical users too.** SQL experts utilize this to sanity-check queries and discover more efficient alternatives.

4. **One language, any database.** Instead of learning a new query dialect for every database management system (DBMS), users just ask their question the same way every time, while the translation is handled underneath.

## Try it 🚀

**[Go to the live demo](https://persv-frontend.persv-dev.workers.dev/connect)**

## How it works ⚙️

1. Connect to a database
- **Demo:** Try out the main features safely without touching your own database. [Chinook database](https://github.com/lerocha/chinook-database) was selected for demo purpose.
- **Custom:** Connect to any supported relational database of your choice, including:
  - PostgreSQL
  - MySQL
  - MariaDB
  - SQLite (in progress)
  - Oracle
  - Microsoft SQL Server

2. Ask questions → Agent generates and executes SQL script against the database → Agent responds with explanatory, insightful language (not raw results).

## Tech Stack 🔍

**Frontend:**

[![TypeScript](https://img.shields.io/badge/typescript-%23007ACC.svg?style=for-the-badge&logo=typescript&logoColor=white)](https://www.typescriptlang.org/)
[![React Router](https://img.shields.io/badge/React_Router-%23CA4245.svg?style=for-the-badge&logo=react-router&logoColor=white)](https://reactrouter.com/)
[![TanStack](https://img.shields.io/badge/tanstack-black?style=for-the-badge&logo=tanstack&logoColor=%23ECE8D1)](https://tanstack.com/)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind_CSS-black?style=for-the-badge&logo=tailwindcss&logoColor=%2306B6D4)](https://tailwindcss.com/)
[![Shadcn/UI](https://img.shields.io/badge/shadcnui-%23000000.svg?style=for-the-badge&logo=shadcnui&logoColor=white)](https://ui.shadcn.com/)
[![Lucide](https://img.shields.io/badge/lucide-black?style=for-the-badge&logo=lucide&logoColor=%23F56565)](https://lucide.dev/)

**Server:**

[![FastAPI](https://img.shields.io/badge/fastapi-%23009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![PostgreSQL](https://img.shields.io/badge/postgresql-%23316192?style=for-the-badge&logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![Redis](https://img.shields.io/badge/redis-black?style=for-the-badge&logo=redis&logoColor=red)](https://redis.io)
[![LangChain Corporate](https://img.shields.io/badge/LangChain-%237FC8FF?style=for-the-badge&logo=langchaincorporate&logoColor=black)](https://www.langchain.com/)
[![Docker](https://img.shields.io/badge/Docker-black?style=for-the-badge&logo=docker&logoColor=%232560FF)](https://www.docker.com/)

**Deployment:**

[![Google Cloud](https://img.shields.io/badge/GoogleCloud-%234285F4.svg?style=for-the-badge&logo=google-cloud&logoColor=white)](https://cloud.google.com/)
[![Cloudflare](https://img.shields.io/badge/Cloudflare-%23F38020.svg?style=for-the-badge&logo=Cloudflare&logoColor=white)](https://www.cloudflare.com/)
[![Neon](https://img.shields.io/badge/neon-black?style=for-the-badge&logo=neon&logoColor=%2334D59A)](https://neon.com/)

## License

Copyright © 2026 Huy Tang. All Rights Reserved.

## Acknowledgements

- [Dataset used for demo purpose](https://github.com/lerocha/chinook-database)
- [A wonderful and easy-to-use README template](https://readme.so/)
