# Crowdfunding Website

## Project Description

This is a Django-based crowdfunding web application where users can explore campaigns and donate to support different causes. The platform allows campaign listing, campaign details viewing, and a basic donation interface.

This project was built as a learning project to understand full-stack web development using Django.

---

## Features

* User Registration
* User Login & Logout
* Campaign Listing Page
* Campaign Detail Page
* Donation Interface
* User Dashboard (basic)
* Responsive UI
* Campaign Images

---

## Tech Stack

**Backend:**

* Python
* Django

**Frontend:**

* HTML
* CSS

**Database:**

* SQLite

**Tools:**

* Git
* GitHub
* VS Code

---

## Project Structure

```
crowdfunding/
│
├── campaigns/          # Main app
├── crowdfunding/       # Project settings
├── static/             # CSS files
├── media/              # Campaign images
├── templates/          # HTML templates
├── manage.py
├── requirements.txt
└── README.md
```

---

## Installation and Setup

### 1 Clone repository

```
git clone https://github.com/martiii-arch/crowdfunding-website.git
```

### 2 Go to project folder

```
cd crowdfunding-website
```

### 3 Create virtual environment

```
python -m venv venv
```

### 4 Activate virtual environment

Windows:

```
venv\Scripts\activate
```

Mac/Linux:

```
source venv/bin/activate
```

### 5 Install dependencies

```
pip install -r requirements.txt
```

### 6 Run migrations

```
python manage.py migrate
```

### 7 Run server

```
python manage.py runserver
```

Open browser:

```
http://127.0.0.1:8000/
```

---

## Future Improvements

* Payment Gateway Integration
* Campaign Categories
* Search functionality
* Campaign progress bar
* User profile management
* Donation history
* Email notifications

---

## Learning Outcomes

Through this project I learned:

* Django project structure
* URL routing
* Models and Views
* Templates
* Static and media handling
* Git and GitHub workflow
* Debugging web applications

---

## Author

**Martin Chacko**

BCA Student
Aspiring Software Developer

---

## License

This project is for educational purposes.
