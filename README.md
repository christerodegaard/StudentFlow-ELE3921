# StudentFlow

StudentFlow is a web application built with Django for organizing courses, assignments, tasks, and notes in one place.

The idea behind the project was to create something that helps students keep track of deadlines and coursework without having to switch between different tools all the time.

This project was developed as part of the **ELE3921 Web Application Development** course.

---

## Main Features

- User registration and login
- Create and manage courses
- Join courses using join codes
- Assignment and task management
- Personal task tracking
- Shared study notes
- Personal notes section
- Dashboard with filtering and progress overview
- Role system for students, TAs, and instructors
- Permission handling for editing/deleting content
- Progress tracking and task status updates

---

## Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python, Django |
| Database | SQLite3 |
| Frontend | Bootstrap 5, HTML/CSS |

---

## Database / Course Related Concepts

The application applies several concepts from the course:

- Relational database design
- Foreign keys and many-to-many relationships
- Database normalization
- Django ORM queries
- Migrations
- Role-based access control
- CRUD operations

---

## Running the Project

**1. Clone the repository**
```bash
git clone https://github.com/christerodegaard/StudentFlow-ELE3921.git
cd StudentFlow-ELE3921
```

**2. Create a virtual environment**
```bash
python -m venv venv
```

**3. Activate the environment**

macOS/Linux:
```bash
source venv/bin/activate
```

Windows:
```bash
venv\Scripts\activate
```

**4. Install dependencies**
```bash
pip install -r requirements.txt
```

**5. Run migrations**
```bash
python manage.py migrate
```

**6. Load sample data**
```bash
python manage.py loaddata db.json
```

**7. Start the server**
```bash
python manage.py runserver
```

**8. Open in browser**
```
http://127.0.0.1:8000/
```

---

## Running Tests

```bash
python manage.py test
```

---

## Notes About the Project

- Tasks are personal to each user, while assignments and courses are shared between enrolled users.
- Study notes connected to tasks are visible to all enrolled users in the course, while personal notes are private to each user.
- Role-based permissions give instructors and TAs more control over course content and moderation.

---

## AI Usage

AI tools were used during parts of the development process for brainstorming, debugging, UI improvements, reviewing code structure, and documentation assistance. All code and database changes were reviewed, tested, and adapted manually. AI-assisted sections are documented in comments where relevant.

---

## Contributors

- [Christer Ødegaard](https://github.com/christerodegaard)
- [Mahdi Shahbazi](https://github.com/Mahdiibazi)
- [Mohid Kashif Hussain](https://github.com/mohidhussain0504)
