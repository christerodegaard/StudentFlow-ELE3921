# StudentFlow

StudentFlow is a web application built with Django for organizing courses, assignments, tasks, and notes in one place.

The idea behind the project was to create something that helps students keep track of deadlines and coursework without having to switch between different tools all the time.

This project was developed as part of the ELE3921 Web Application Development** course.


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



## Contributors

- [Christer Ødegaard](https://github.com/christerodegaard)
- [Mahdi Shahbazi](https://github.com/Mahdiibazi)
- [Mohid Kashif Hussain](https://github.com/mohidhussain0504)

