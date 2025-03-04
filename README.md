# Audionomy
_A play on “autonomy,” implying an autonomous audio library builder_

**Audionomy** is a Django-based project for creating and managing audio datasets (i.e., “autonomous audio library builder”). It helps you store, upload, and analyze audio files in a structured manner, letting you track metadata (title, style prompts, etc.) and automatically compute audio durations. It uses Python’s `pydub` library to detect lengths of uploaded audio. 

## Table of Contents
1. [Project Features](#project-features)
2. [Installation](#installation)
3. [Usage](#usage)
4. [Project Structure](#project-structure)
5. [Models Overview](#models-overview)
6. [Routes & Views](#routes--views)
7. [Contributing](#contributing)
8. [License](#license)

---

## Project Features
- **Dataset Management**: Group audio entries under a named dataset.  
- **Audio Uploads**: Store up to two audio files per entry (optional).  
- **Automatic Duration**: Audio lengths computed automatically after upload.  
- **Relational DB**: Uses Django’s ORM (SQLite by default) for stable data (no more CSV).  
- **User Interface**: Basic HTML pages using Bootstrap for styling (or you can refine further).  
- **Expandable**: You can add logic for advanced features (export, dynamic columns, etc.).

---

## Installation
Below instructions assume you have Python 3.9+ and [Poetry](https://python-poetry.org/docs/) installed.

1. **Clone this repo**:
   ```bash
   git clone https://github.com/YourUserName/audionomy.git
   cd audionomy
   ```
2. **Install dependencies**:
   ```bash
   poetry install
   ```
   This sets up a virtual environment with all required libraries (e.g., Django, pydub).
3. **Activate environment**:
   ```bash
   poetry shell
   ```
4. **Configure DB (optional)**:
   - By default, `audionomy_project/settings.py` uses SQLite (`db.sqlite3`). This is fine for local dev. If you want Postgres or MySQL, adjust `DATABASES` in `settings.py`.

5. **Apply migrations**:
   ```bash
   python manage.py migrate
   ```
6. **(Optional) Create admin user**:
   ```bash
   python manage.py createsuperuser
   ```

---

## Usage
1. **Run development server**:
   ```bash
   python manage.py runserver
   ```
   Then open [http://127.0.0.1:8000](http://127.0.0.1:8000) in your browser.

2. **Create or manage datasets**:
   - On the home page, you can type a new dataset name to create it.
   - Then click a dataset to view or add audio entries.

3. **Uploading Audio**:
   - By default, the project stores files in `media/` (defined by `MEDIA_ROOT`).
   - If you upload `.mp3` or `.wav`, the project uses `pydub` to compute its length.

4. **Admin panel** (optional):
   - Visit [http://127.0.0.1:8000/admin](http://127.0.0.1:8000/admin).
   - Log in with your superuser credentials.
   - You can see and manage `Dataset` and `AudioEntry` records from there.

---

## Project Structure

```
audionomy/
├── audionomy_app/
│   ├── admin.py             # Model registrations for Django admin
│   ├── apps.py              # Django app config
│   ├── models.py            # Our core data models (Dataset, AudioEntry)
│   ├── tests.py             # Python-based tests for the app
│   ├── urls.py              # App-specific URL patterns
│   ├── views.py             # Django views for home, manage_dataset, etc.
│   ├── migrations/          # Auto-generated DB migrations
│   └── templates/           # HTML templates, including base.html
├── audionomy_project/
│   ├── settings.py          # Django project settings
│   ├── urls.py              # Global URL routing (includes app's urls)
│   ├── wsgi.py / asgi.py    # WSGI/ASGI config for deployment
│   └── __init__.py
├── db.sqlite3               # Default SQLite DB (created after migrate)
├── manage.py                # Django CLI commands entry point
├── pyproject.toml           # Poetry config with dependencies
├── poetry.lock              # Lockfile from Poetry
├── LICENSE                  # License for the project
└── README.md                # This file
```

---

## Models Overview
- **`Dataset`**: 
  - Basic fields: `name`, `created_at`.
  - Groups multiple `AudioEntry` objects.
- **`AudioEntry`**:
  - Fields for `title`, plus optional prompts, YouTube link, etc.
  - One or two `FileField`s for audio. Automatic duration stored in `audio1_duration`, `audio2_duration`.
  - `save()` override uses `pydub` to measure length after the file is saved.

---

## Routes & Views
- **`home`**: Lists existing datasets, form to create a new dataset.
- **`manage_dataset`**: Show a dataset’s entries, link to add new, export, etc.
- **`add_entry`**: Displays a form to upload one or two audio files, plus metadata fields. On POST, saves to DB, triggers pydub for durations.
- **`export_dataset`** (placeholder): You can implement logic to zip up or CSV-export your dataset.

**URLs** are defined in:
- `audionomy_app/urls.py` – local route definitions
- `audionomy_project/urls.py` – includes `audionomy_app.urls`

---

## Contributing
1. **Fork** the project on GitHub.
2. **Create** a feature branch.
3. **Commit** your changes with descriptive messages.
4. **Open** a Pull Request.

Feel free to open issues for suggestions or bug reports. For big features, open an issue for discussion first.

---

## License
This repository uses the MIT License (see `LICENSE` file). You’re free to fork, modify, and distribute under the same terms. For more details, see [http://opensource.org/licenses/MIT](http://opensource.org/licenses/MIT).

---