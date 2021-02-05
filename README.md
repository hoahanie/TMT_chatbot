# TMT Chatbot

## 1. How to run
### 1.1. Run chatbot (recommended)
This section uses **Docker compose**, so install it beforehand.

For Unix-based, run the following:
> bash launcher.sh

File `launcher.sh` contains all necessary commands. Please visit it for more information.

For Windows, run the following:
> docker-compose up

### 1.2. Run Frontend and/or Backend independently

#### With Backend
From root directory, run the following:

> cd backend

> pip install - r requirements.txt

> python api.py

#### With Frontend
From root directory, run the following:

> cd frontend 

> npm i

> npm start

### 1.3. Frontend URL
Please visit: [http://localhost:3000](http://localhost:3000) to open website.

## 2. Components
### 2.1. Backend
Python is used with **Flask** to deploy server. Backend runs in port *5000*.

### 2.2. Frontend
Node runs in port *3000*.