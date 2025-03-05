# Audionomy

_A play on “autonomy,” Audionomy is an autonomous audio dataset creator – a powerful tool for managing AI-generated music datasets._

Audionomy is a Django-based application designed to help you log, manage, and export audio files along with their metadata. Built to support AI-generated audio (e.g., from Suno.ai), Audionomy provides an intuitive web interface for uploading audio, automatically computing durations using pydub, and exporting your dataset in multiple formats including CSV, JSON, Parquet, and ZIP archives of audio files.

---

## Table of Contents

- [Project Features](#project-features)
- [Installation](#installation)
- [Usage](#usage)
- [Export Capabilities](#export-capabilities)
- [Project Structure](#project-structure)
- [Development & CI/CD](#development--cicd)
- [Contributing](#contributing)
- [License](#license)

---

## Project Features

- **Dataset Management:** Create and manage multiple audio datasets with a dedicated web UI.
- **Audio Uploads:** Upload one or two audio files per entry with drag-and-drop support.
- **Automatic Duration Calculation:** Uses pydub to automatically compute the duration of each uploaded audio file.
- **Multiple Export Formats:**
  - **CSV & JSON:** Export dataset metadata.
  - **Parquet:** Generate a columnar export for efficient analytics.
  - **ZIP Archive:** Package all audio files into a single ZIP file.
- **Responsive UI:** Built with Bootstrap, providing a user-friendly interface for managing entries.
- **Expandable:** Modular codebase that supports future features such as automated logging, background processing, and more.
- **CI/CD Integration:** Automated testing and linting with GitHub Actions to ensure code quality.

---

## Installation

### Prerequisites
- Python 3.9+
- [Poetry](https://python-poetry.org/docs/)
- MySQL (or adjust the settings for SQLite during development)

### Steps

1. **Clone the Repository:**
   ```bash
   git clone https://github.com/YourUserName/audionomy.git
   cd audionomy
   ```

2. **Install Dependencies:**
   ```bash
   poetry install
   ```

3. **Activate the Virtual Environment:**
   ```bash
   poetry shell
   ```

4. **Configure the Database:**
   - By default, the project uses SQLite. To use MySQL, update the `DATABASES` setting in `audionomy_project/settings.py` accordingly.
   - Ensure your MySQL server is running and the credentials are set in your environment variables (e.g., in a `.env` file).

5. **Apply Migrations:**
   ```bash
   python manage.py migrate
   ```

6. **(Optional) Create an Admin User:**
   ```bash
   python manage.py createsuperuser
   ```

---

## Usage

1. **Run the Development Server:**
   ```bash
   python manage.py runserver
   ```
   Open your browser at [http://127.0.0.1:8000](http://127.0.0.1:8000).

2. **Managing Datasets:**
   - On the home page, create a new dataset by entering a name.
   - Click on a dataset to view, add, edit, or delete audio entries.

3. **Uploading Audio:**
   - Use the “Add Entry” page to enter metadata (e.g., Song Title, Style Prompt, Exclude Style, Model Used, YouTube Link).
   - Upload one or two audio files via the drag-and-drop enabled form.
   - The application automatically computes audio durations upon upload.

---

## Export Capabilities

Audionomy supports multiple export formats to facilitate dataset sharing and publication:

- **CSV Export:** Export all dataset metadata in a CSV file.
- **JSON Export:** Export metadata as a JSON file.
- **Parquet Export:** Generate a Parquet file for efficient storage and analytical processing.
- **ZIP Archive:** Create a ZIP archive containing all audio files for a selected dataset.

Each export option is accessible via dedicated buttons on the dataset management page.

---

## Project Structure

```
audionomy/
├── audionomy_app/
│   ├── admin.py             # Admin interface configuration
│   ├── apps.py              # Django app configuration
│   ├── forms.py             # Forms for audio entry uploads
│   ├── models.py            # Data models (Dataset, AudioEntry)
│   ├── templates/           # HTML templates for UI pages
│   ├── tests.py             # Unit and integration tests
│   ├── urls.py              # URL routing for audionomy_app
│   └── views.py             # Views for handling requests and exports
├── audionomy_project/
│   ├── asgi.py              # ASGI configuration
│   ├── settings.py          # Project settings
│   ├── urls.py              # Global URL routing
│   ├── wsgi.py              # WSGI configuration
│   └── __init__.py
├── db.sqlite3               # Default development database (SQLite)
├── LICENSE                  # Project license (MIT)
├── manage.py                # Django CLI entry point
├── poetry.lock              # Poetry lock file
├── pyproject.toml           # Poetry configuration
└── README.md                # Project documentation (this file)
```

---

## Development & CI/CD

- **Local Development:** Run the development server and test locally. Use Django Admin for quick management.
- **Testing:** A comprehensive suite of unit and integration tests is included in `audionomy_app/tests.py`.
- **CI/CD:** GitHub Actions is set up to run tests and linting on every push and pull request. See the `.github/workflows/ci.yml` file for configuration details.
- **Future Enhancements:** Plans to integrate background processing for heavy tasks and expand automated logging.

---

## Contributing

Contributions are welcome! To contribute:

1. **Fork the Repository** on GitHub.
2. **Create a Feature Branch** for your changes.
3. **Commit Your Changes** with clear, descriptive messages.
4. **Submit a Pull Request** for review.
5. **Follow the Code Style Guidelines** outlined in the [CONTRIBUTING.md](CONTRIBUTING.md) file.

---

## License

Audionomy is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

*Audionomy is designed to be an evolving tool for audio dataset management. Future updates will include more export formats, enhanced UI features, and deeper integration with data platforms such as Hugging Face and Kaggle.*
