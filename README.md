# 💸 PocketFlow
### A Secure, Full-Stack Financial Analytics Platform

![Python](https://img.shields.io/badge/Python-3.10-3776AB?style=flat&logo=python&logoColor=white) ![FastAPI](https://img.shields.io/badge/FastAPI-0.95-009688?style=flat&logo=fastapi&logoColor=white) ![Streamlit](https://img.shields.io/badge/Streamlit-1.22-FF4B4B?style=flat&logo=streamlit&logoColor=white) ![License](https://img.shields.io/badge/License-MIT-grey)

**PocketFlow** is a production-ready personal finance application designed to demonstrate the integration of a high-performance REST API with an interactive data science dashboard.

Unlike simple expense scripts, PocketFlow implements a **secure multi-tenant architecture**. It ensures that financial data is isolated per user using industry-standard **OAuth2 authentication** and **JWT (JSON Web Token)** security protocols.

---

## 🏗️ Architecture Overview

The project follows a decoupled **Client-Server architecture**:

* **Backend (The Engine):** Powered by **FastAPI** & **SQLModel**, offering high-speed API endpoints, Pydantic data validation, and automated Swagger documentation.
* **Frontend (The Interface):** Built with **Streamlit**, leveraging **Pandas** and **Plotly** to transform raw API data into dynamic charts and balance metrics.
* **Security Layer:** Implements **Bcrypt** password hashing and dependency injection to strictly protect sensitive routes.

---

## 🚀 Key Features

* **🔐 Secure Authentication:** User registration and login system using **OAuth2** and **JWT Tokens**.
* **🛡️ Data Isolation:** Multi-user support where each user acts as a separate tenant.
* **📊 Interactive Dashboard:** Dynamic **Plotly** charts and real-time balance calculations.
* **🤖 Automation Support:** Includes a dedicated Python script (`populate.py`) to simulate microservice interactions.
* **📉 Data Freedom:** Built-in CSV export functionality for offline analysis.

---

## 🛠️ Installation & Setup

Run the following commands in your terminal to set up the project:

```bash
# 1. Clone the repository
git clone [https://github.com/ravinandanpatel/pocketflow-api.git](https://github.com/ravinandanpatel/pocketflow-api.git)
cd pocketflow-api

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the Backend (Terminal 1)
# The API will be available at [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
uvicorn main:app --reload

# 4. Run the Dashboard (Terminal 2)
streamlit run dashboard.py
