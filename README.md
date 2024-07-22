README.md:

# Life Prescriber

Life Prescriber is a web application designed to help medical patients adhere to their medication schedules through timely email reminders. Clinicians can onboard patients, manage medication schedules, and monitor adherence through a comprehensive backend system.

## Features

- *Patient Onboarding*: Easy onboarding of patients by clinicians.
- *Email Reminders*: Automated email notifications for medication reminders.
- *Medication Tracking*: Track patient medication adherence through the backend.
- *Custom Authentication*: Secure custom authentication backend.
- *Admin Interface*: Enhanced admin interface for managing users and prescriptions.
- *Task Scheduling*: Utilizes Celery for scheduling email reminders.

## Installation

### Prerequisites

- Python 3.10+
- Redis (for Celery) watch video [Redis installation](https://www.youtube.com/watch?v=DLKzd3bvgt8&t=197s)

### Setup

1. *Create and activate a virtual environment:*
   bash
   ```
   python -m venv your_virtual_environment_name
   source venv/bin/activate   # On Windows use `your_virtual_environment_name\Scripts\activate`
   ```

2. *Clone the repository:*
   bash
   ```
   git clone https://github.com/olugbeminiyi2000/MedHack_Life_Prescriber.git
   cd MedHack_Life_Prescriber/
   ```

3. *Install dependencies:*
   bash
   ```
   pip install -r requirements.txt
   ```
   

4. *Set up the Django project:*
   bash
   ```
   cd Life_Prescriber
   python manage.py makemigrations
   python manage.py migrate
   python manage.py createsuperuser --email=your_email --username=your_username
   python manage.py check
   python manage.py runserver
   ```

   

5. *Set up Celery:*
   - open up 2 command line interface at vscode terminal Launch Profile.
   - then change directory to MedHack_Life_Prescriber/Life_Prescriber/ if not there.
   bash
   ```
   celery -A Life_Prescriber worker --pool=solo -l INFO
   celery -A Life_Prescriber beat -l INFO
   ```

## Usage

- Log in to the admin panel at http://127.0.0.1:8000/admin/ using your superuser credentials.
- Onboard patients and manage prescriptions.
- Track patient medication adherence through the backend system.

## Configuration

### Celery Configuration

In Life_Prescriber/celery.py:
python
```
app.conf.beat_schedule = {
    'task-name': {
        'task': 'prescription_ongo.tasks.send_async_email',
        'schedule': crontab(minute='*/10'),
    },
}
# very important do not change
app.conf.task_default_queue = 'default'
```


## Contributing

We welcome contributions! Please see our [CONTRIBUTING.md](CONTRIBUTING.md) file for more details.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

### Additional Included Files

1. *CONTRIBUTING.md*: Guidelines for contributing to the project.
2. *LICENSE*: The licensing information for the project.
3. *requirements.txt*: List of dependencies required to run the project.
4. *.gitignore*: Specifies files and directories to be ignored by Git.