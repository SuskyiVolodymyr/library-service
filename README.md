# 🏛️📖 Library Service Project 📖🏛️

## Project Description

The Library Service Project is designed to modernize the library system in your city. The current system for tracking books, borrowings, users, and payments is outdated, with all processes being handled manually and recorded on paper. The system lacks the ability to check the inventory of specific books, requires cash payments, and does not effectively track the return of books. This project implements an online management system for book borrowings to optimize the work of library administrators and make the service more user-friendly.



## How to Run the Project with Docker

1. **Clone the repository:**
```bash
git clone <repository-url>
cd library-service
```
2. **Build the Docker image and containers:**
```bash
docker-compose up --build
```
3. **Copy the sample environment file and populate it with the required data**

4. **Create a superuser:**
```bash
docker compose exec -it library python manage.py createsuperuser
```
5. **Access the application:**
* Admin interface: Go to http://127.0.0.1:8000/admin/ and log in with the superuser credentials.
* API endpoints: Access the API at http://127.0.0.1:8000/api/.
6. **Shut down the Docker containers:**
```bash
docker-compose down
```
### Running Tests
* To run tests, execute:
```bash
docker-compose exec web python manage.py test
```

## How to Run the Project with Virtual Environment
1. **Clone the repository:**
```bash
git clone <repository-url>
cd library-service
```
2. **Set up the virtual environment:**
```bash
python -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`
```
3. **Install the dependencies:**
```bash
pip install -r requirements.txt
```
4. **Run migrations:**
```bash
python manage.py migrate
```
5. **Copy the sample environment file and populate it with the required data**
6. **Create a superuser:**
```bash
python manage.py createsuperuser
```
7. **Run Redis Server:**
```bash
docker run -d -p 6379:6379 redis
```
8. **Run celery worker for tasks handling:**
```bash
celery -A library_service worker -l INFO -P solo
```
9. **Run celery beat for tasks handling:**
```bash
celery -A library_service beat -l INFO --scheduler django_celery_beat.schedulers:DatabaseScheduler
```
10. **Run the development server:**
```bash
python manage.py runserver
```
11. **Access the admin interface:**
* Go to http://127.0.0.1:8000/admin/ and log in with the superuser credentials.


### Running Tests
* To run tests, execute:
```bash
python manage.py test
```

## Architecture

### Resources

#### Book
- **Title:** `str`
- **Author:** `str`
- **Cover:** `Enum(HARD, SOFT)`
- **Inventory:** `positive int` (Number of copies available in the library)
- **Daily fee:** `decimal` (in $USD)

#### User (Customer)
- **Email:** `str`
- **First name:** `str`
- **Last name:** `str`
- **Password:** `str`
- **Is staff:** `bool`

#### Borrowing
- **Borrow date:** `date`
- **Expected return date:** `date`
- **Actual return date:** `date`
- **Book id:** `int`
- **User id:** `int`

#### Payment
- **Status:** `Enum(PENDING, PAID)`
- **Type:** `Enum(PAYMENT, FINE)`
- **Borrowing id:** `int`
- **Session url:** `Url` (URL to Stripe payment session)
- **Session id:** `str` (ID of Stripe payment session)
- **Money to pay:** `decimal` (in $USD, calculated borrowing total price)

## Components

### Books Service
Managing books inventory (CRUD for Books)
- **POST:** `/books/` - Add a new book
- **GET:** `/books/` - Get a list of books
- **GET:** `/books/<id>/` - Get book details
- **PUT/PATCH:** `/books/<id>/` - Update a book (also manage inventory)
- **DELETE:** `/books/<id>/` - Delete a book

### Users Service
Managing authentication and user registration
- **POST:** `/users/` - Register a new user
- **POST:** `/users/token/` - Get JWT tokens
- **POST:** `/users/token/refresh/` - Refresh JWT token
- **GET:** `/users/me/` - Get profile information
- **PUT/PATCH:** `/users/me/` - Update profile information

### Borrowings Service
Managing users' borrowings of books
- **POST:** `/borrowings/` - Add a new borrowing (decreases book inventory by 1)
- **GET:** `/borrowings/?user_id=...&is_active=...` - Get borrowings by user ID and active status
- **GET:** `/borrowings/<id>/` - Get specific borrowing
- **POST:** `/borrowings/<id>/return/` - Set actual return date (increases book inventory by 1)

### Notifications Service (Telegram)
- Notifications about new borrowing created, borrowings overdue, and successful payment
- In parallel cluster/process using `Django Q` or `Django Celery`
- Interacts with Telegram API, Telegram Chats & Bots

### Payments Service (Stripe)
- **GET:** `/payment/` - Main payment processing endpoint.
- **GET:** `/payment/<id>` - Get detail information of payment.

## Features
- [X] Implement custom user model
- [X] Implement JWT authentication for user login and token management
- [X] Implement custom permissions for access control (IsAdminOrReadOnly)
- [X] Set up Docker for the development and production environments
- [X] Implement CRUD functionality for Books Service
- [X] Implement CRUD for Users Service
- [X] Implement Borrowing List & Detail endpoint
- [X] Implement Create Borrowing endpoint with inventory validation
- [X] Implement Return Borrowing functionality with inventory update
- [X] Implement the possibility of sending notifications for each borrowing creation
- [X] Set up Telegram chat and bot for notifications
- [X] Implement daily function for checking borrowings overdue
- [X] Implement Stripe Payment Sessions for borrowings
- [X] Add FINE Payment for book overdue
- [X] Send notifications to the Telegram chat on each successful Payment


## Documentation
* API documentation is available at http://127.0.0.1:8000/api/doc/swagger/.

## Group members:
#### Mentor:
- Maksym German

#### Team lead:
- Volodymyr Suskyi

#### Other participant:
- Anton Korinchuk
- Yeva Yepifanova
- Viktor Shveda
- Andrii Romaniuk

#### Curator:
- Valentyna Haichenko
