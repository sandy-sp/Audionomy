# 🎧 Audionomy: Audio Dataset Management Tool

Audionomy is an intuitive, feature-rich application designed to simplify the creation, management, visualization, and sharing of audio datasets. Built specifically for researchers, data scientists, AI developers, and hobbyists, Audionomy streamlines audio metadata handling, visualization, and distribution.

## 📌 Core Features

- **Customizable Dataset Templates**: Define columns manually or import from existing CSV files.
- **Automatic Audio Metadata Extraction**: Auto-fills duration and file format upon audio upload.
- **Integrated Audio Management**: Easily add, edit, and remove audio entries directly within the GUI.
- **Interactive Visualizations**: Embedded Plotly visualizations to explore your audio data intuitively.
- **Comprehensive Export Options**:
  - CSV
  - JSON
  - Parquet
  - ZIP archive (for audio files)
- **Cloud Integration**:
  - [Hugging Face Datasets](https://huggingface.co/datasets)
  - [GitHub (with Git LFS)](https://git-lfs.com)
  - [Kaggle Dataset Publishing](https://kaggle.com)

## ⚙️ Installation

### Prerequisites

- Python 3.9 or higher
- Poetry package manager

### Setup

1. **Clone the repository:**

```bash
git clone https://github.com/your-username/audionomy.git
cd audionomy
```

2. **Install dependencies using Poetry:**

```bash
poetry install
```

### Run Audionomy

Launch the application via:

```bash
poetry run python gui/app.py
```

## 🗂️ Dataset Structure

Every dataset created with Audionomy follows this clear structure:

```
dataset_name/
├── audio/                # Contains all audio files
├── metadata.csv          # Metadata in CSV format
├── metadata.json         # Metadata in JSON format
├── metadata.parquet      # Metadata in Parquet format
└── dataset_name.template # Dataset template schema
```

## ☁️ Cloud Integrations

### Hugging Face Integration

Easily publish datasets:

- Authenticate with Hugging Face:

```bash
poetry run huggingface-cli login
```

- Use the integrated export option in the GUI to upload your dataset seamlessly.

### GitHub Integration (with Git LFS)

Efficiently manage large audio datasets:

- Install Git LFS and configure:

```bash
sudo apt install git-lfs
git lfs install
git lfs track "datasets/**/*.mp3"
git lfs track "datasets/**/*.wav"
git add .gitattributes
git commit -m "Configure Git LFS for audio files"
git push origin main
```

### Kaggle Integration

Publish your dataset to Kaggle:

- Install and configure Kaggle CLI:

```bash
poetry add kaggle
mkdir -p ~/.kaggle
cp kaggle.json ~/.kaggle/
chmod 600 ~/.kaggle/kaggle.json
```

- Use the integrated GUI option for seamless export to Kaggle.

## 📦 Technology Stack

- **GUI**: PySide6 (Qt)
- **Data Management**: pandas, PyArrow
- **Audio Handling**: pydub
- **Visualization**: Plotly
- **Package Management**: Poetry

## 📜 License

Audionomy is open-source software licensed under the [MIT License](LICENSE).

