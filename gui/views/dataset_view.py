# gui/views/dataset_view.py

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTableView,
    QHeaderView, QFileDialog, QMessageBox, QToolBar, QLineEdit, QComboBox
)
from PySide6.QtCore import Qt, QAbstractTableModel, QModelIndex, Signal
from PySide6.QtGui import QAction
import qtawesome as qta
import pandas as pd
import os

from gui.components.audio_player import AudioWaveformWidget
from gui.components.entry_form import EntryForm
from scripts.dataset_manager import DatasetManager


class DatasetTableModel(QAbstractTableModel):
    """Table Model for displaying dataset metadata efficiently."""

    def __init__(self, dataset_manager):
        super().__init__()
        self.dataset_manager = dataset_manager
        self.load_data()

    def load_data(self):
        """Loads dataset metadata into a DataFrame."""
        self.dataframe = self.dataset_manager.get_metadata() or pd.DataFrame()
        self.beginResetModel()
        self.endResetModel()

    def rowCount(self, parent=QModelIndex()):
        return len(self.dataframe)

    def columnCount(self, parent=QModelIndex()):
        return len(self.dataframe.columns)

    def data(self, index, role):
        if not index.isValid() or role != Qt.DisplayRole:
            return None
        return str(self.dataframe.iloc[index.row(), index.column()])

    def setData(self, index, value, role=Qt.EditRole):
        if index.isValid() and role == Qt.EditRole:
            self.dataframe.iloc[index.row(), index.column()] = value
            self.dataset_manager.update_metadata_value(index.row(), self.dataframe.columns[index.column()], value)
            self.dataChanged.emit(index, index)
            return True
        return False

    def headerData(self, section, orientation, role):
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                return self.dataframe.columns[section]
            elif orientation == Qt.Vertical:
                return str(section + 1)
        return None


class DatasetView(QWidget):
    """View for displaying, managing, and editing dataset metadata."""

    datasetUpdated = Signal()

    def __init__(self, dataset_manager: DatasetManager, status_bar, parent=None):
        super().__init__(parent)
        self.dataset_manager = dataset_manager
        self.status_bar = status_bar
        self.setup_ui()

    def setup_ui(self):
        """Set up the UI components for dataset management."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)

        # Header
        header_layout = QHBoxLayout()
        self.dataset_name_label = QLabel(f"Dataset: {os.path.basename(self.dataset_manager.dataset_path)}")
        self.dataset_name_label.setObjectName("page-header")
        header_layout.addWidget(self.dataset_name_label)
        layout.addLayout(header_layout)

        # Toolbar for Actions
        self.toolbar = self.create_toolbar()
        layout.addWidget(self.toolbar)

        # Metadata Table
        self.table_model = DatasetTableModel(self.dataset_manager)
        self.metadata_table = QTableView()
        self.metadata_table.setModel(self.table_model)
        self.metadata_table.setAlternatingRowColors(True)
        self.metadata_table.setSelectionBehavior(QTableView.SelectRows)
        self.metadata_table.setEditTriggers(QTableView.DoubleClicked)
        self.metadata_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.metadata_table)

        # Audio Preview
        self.audio_player = AudioWaveformWidget()
        layout.addWidget(self.audio_player)

        # Load Initial Data
        self.load_dataset()

    def create_toolbar(self):
        """Creates the toolbar with dataset management actions."""
        toolbar = QToolBar()
        toolbar.setIconSize(Qt.QSize(18, 18))

        # Add Audio Entry
        add_entry_action = QAction(qta.icon("fa5s.plus-circle"), "Add Entry", self)
        add_entry_action.triggered.connect(self.add_entry)
        toolbar.addAction(add_entry_action)

        # Remove Selected Entry
        remove_entry_action = QAction(qta.icon("fa5s.trash"), "Remove Entry", self)
        remove_entry_action.triggered.connect(self.remove_entry)
        toolbar.addAction(remove_entry_action)

        # Search Bar
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Search...")
        self.search_input.textChanged.connect(self.filter_table)
        toolbar.addWidget(self.search_input)

        return toolbar

    def load_dataset(self):
        """Loads dataset metadata into the table model."""
        self.table_model.load_data()
        self.status_bar.showMessage(f"Loaded dataset with {self.table_model.rowCount()} entries", 5000)

    def add_entry(self):
        """Opens the entry form to add a new audio entry."""
        self.entry_form = EntryForm(self.dataset_manager, self.status_bar, self.load_dataset)
        self.entry_form.setWindowTitle("Add New Audio Entry")
        self.entry_form.show()

    def remove_entry(self):
        """Removes the selected metadata entry from the dataset."""
        selected_rows = set(index.row() for index in self.metadata_table.selectionModel().selectedRows())
        if not selected_rows:
            QMessageBox.warning(self, "Warning", "Please select an entry to remove.")
            return

        df = self.dataset_manager.get_metadata()
        df = df.drop(index=selected_rows).reset_index(drop=True)
        df.to_csv(self.dataset_manager.metadata_path, index=False)
        self.load_dataset()
        self.status_bar.showMessage("Entry removed successfully.", 5000)

    def filter_table(self):
        """Filters metadata based on search input."""
        search_text = self.search_input.text().strip().lower()
        df = self.dataset_manager.get_metadata()
        if df is not None:
            filtered_df = df[df.apply(lambda row: row.astype(str).str.contains(search_text, case=False, na=False).any(), axis=1)]
            self.table_model.dataframe = filtered_df
            self.table_model.layoutChanged.emit()

    def play_audio(self, row):
        """Loads and plays an audio file from the dataset."""
        df = self.dataset_manager.get_metadata()
        if df is not None and "audio_file" in df.columns:
            audio_path = df.iloc[row]["audio_file"]
            if os.path.exists(audio_path):
                self.audio_player.load_audio(audio_path)
                self.status_bar.showMessage(f"Playing: {os.path.basename(audio_path)}", 3000)
            else:
                self.status_bar.showMessage(f"Audio file not found: {audio_path}", 3000)

