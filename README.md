# Audio Vetting Application (AVA)

A comprehensive desktop application for vetting and managing experimental audio files from the WISC Lab. Built with Python and Flet, this application provides an intuitive interface for researchers to review, categorize, and track the status of audio files in longitudinal studies.

## 🎯 Purpose

The Audio Vetting Application (AVA) is designed to streamline the process of reviewing and organizing experimental audio files collected from child language development studies. It provides researchers with tools to:

- **Vet individual audio files** with playback controls and status tracking
- **Manage file assignments** across multiple workers/researchers
- **Track completion status** of audio file reviews
- **Synchronize data** between different storage systems (STOCS, SSS files)
- **Generate reports** on vetting progress and file organization

## ✨ Key Features

### 🎧 Audio Vetting Tab
- **Interactive audio playback** with play/pause controls
- **File status management** (Complete, Incomplete, Needs Review, etc.)
- **Comment system** for detailed file annotations
- **Worker assignment** and progress tracking
- **Visit-based filtering** to focus on specific data collection sessions

### 📁 File Management System
- **Comprehensive file browser** showing all audio files in the database
- **Folder organization** with automatic hierarchy detection
- **File type categorization** (STOCS, SSS, etc.)
- **Real-time status updates** and batch operations

### 👥 Worker Management
- **Multi-user support** with individual worker assignments
- **Progress tracking** per worker and visit
- **Workload distribution** across team members
- **Completion statistics** and reporting

### 🔧 Advanced Utilities
- **Data synchronization** between AVA database and file system
- **Automated directory creation** and organization
- **File validation** and integrity checking
- **Database backup and restore** functionality
- **Batch processing** for large datasets
- **Timestamp tracking** for data updates

## 🏗️ Architecture

### Database Schema
The application uses SQLite with three core tables:

#### Files Table
- `FileID` (Primary Key)
- `WorkerID` (Foreign Key to Workers)
- `FolderID` (Foreign Key to Folders)
- `FileName`, `FilePath`, `FileType`
- `FileStatus`, `Comments`

#### Workers Table  
- `WorkerID` (Primary Key)
- `WorkerName`, `WorkerType`

#### Folders Table
- `FolderID` (Primary Key)
- `FolderName`, `TotalFiles`
- `FolderPath`, `FolderGroup`

### Application Structure
```
audio-vetting/
├── main.py                 # Main application entry point
├── vetting_tab.py         # Audio vetting interface
├── utilities_tab.py       # Data management utilities  
├── db_initialization.py   # Database setup and schema
├── db_updates.py          # Database operations
├── dt_updates.py          # Data table updates
├── icon.png              # Application icon
├── build.txt             # Build configuration
└── README.md             # This file
```

## 🚀 Installation

### Prerequisites
- **Python 3.8+** (tested with Python 3.12)
- **Windows/macOS/Linux** (cross-platform compatible)

### Required Dependencies
Install the required Python packages:

```bash
pip install flet>=0.10.0
pip install pandas>=1.5.0
pip install just-playback>=0.1.0
pip install pytz
```

### Additional Dependencies
The application also requires these packages (install via pip):
- `sqlite3` (included with Python)
- `os`, `sys`, `pathlib` (standard library)
- `shutil`, `re`, `csv` (standard library)
- `datetime` (standard library)

### Installation Steps

1. **Clone the repository:**
   ```bash
   git clone https://github.com/BeckettFrey/audio-vetting.git
   cd audio-vetting
   ```

2. **Install dependencies:**
   ```bash
   pip install flet pandas just-playback pytz
   ```

3. **Run the application:**
   ```bash
   python main.py
   ```

## 📖 Usage Guide

### First-Time Setup
1. **Launch the application** - The database will be automatically initialized
2. **Configure data paths** - Ensure access to the speech data directories
3. **Add workers** - Set up user accounts for your research team
4. **Sync data** - Use the Utilities tab to import existing audio files

### Vetting Workflow

#### 1. Audio Vetting Tab
- **Select worker** from the dropdown to see assigned files
- **Choose a visit** to focus on specific data collection sessions
- **Review files** using the built-in audio player
- **Update status** (Complete, Incomplete, Needs Review, etc.)
- **Add comments** for detailed notes and observations

#### 2. File Management
- **All Files tab** - Browse complete file database
- **All Folders tab** - View folder hierarchy and completion stats
- **All Workers tab** - Monitor team progress and assignments

#### 3. Data Utilities
- **Update AVA Data** - Sync with new STOCS/SSS files
- **Update Vetted Data** - Organize completed files
- **Database maintenance** - Backup and restore operations

### Keyboard Shortcuts & Tips
- Files are automatically filtered by worker and visit selection
- Use the refresh functionality after making database changes
- Comments are saved automatically when moving between files
- Audio playback supports standard media controls

## 🔧 Development

### Setting Up Development Environment
1. **Clone the repository**
2. **Create virtual environment:**
   ```bash
   python -m venv audio-vetting-env
   source audio-vetting-env/bin/activate  # On Windows: audio-vetting-env\Scripts\activate
   ```
3. **Install development dependencies:**
   ```bash
   pip install -r requirements.txt  # If available
   # Or install manually:
   pip install flet pandas just-playback pytz
   ```

### Code Structure
- **main.py** - Application entry point with GUI setup
- **vetting_tab.py** - Core vetting functionality and audio controls
- **utilities_tab.py** - Data management and synchronization tools
- **db_initialization.py** - Database schema and initialization
- **db_updates.py** - Database CRUD operations
- **dt_updates.py** - Data table management and UI updates

### Key Components
- **SQLDataTable class** - Handles database queries and Flet DataTable conversion
- **Playback integration** - Audio file playback using just-playback library
- **Cross-platform paths** - Automatic path resolution for different operating systems
- **Database connection management** - SQLite with optimized settings

## 📦 Building & Distribution

### Creating Standalone Executable
The application can be packaged into a standalone executable using Flet's built-in packaging:

```bash
flet pack main.py --icon icon.png --product-name 'Audio Vetting' --product-version "1.13"
```

This will create a distributable executable in the `dist/` folder that can be run without Python installation.

### Build Configuration
The build settings are stored in `build.txt`:
- **Application name:** Audio Vetting
- **Version:** 1.13  
- **Icon:** icon.png
- **Entry point:** main.py

## 🗃️ Database Management

### Backup Strategy
- Database backups are automatically created in the `utils` folder
- Timestamps track last update times for both AVA and vetted data
- Use the Utilities tab for manual backup and restore operations

### Data Synchronization
The application can sync with external file systems:
- **STOCS files** - Structured Test of Conscious Storytelling audio files
- **SSS files** - Structured storytelling session recordings
- **Directory organization** - Automatic folder creation and file organization

### File Path Management  
The application supports multiple drive configurations:
- Network drives (X:, Y:, Z:, W:, M: drives)
- Local paths (C: drive)
- UNC paths for network storage
- Cross-platform compatibility (Windows, macOS, Linux)

## 🤝 Contributing

### Development Guidelines
1. **Follow Python best practices** and PEP 8 style guide
2. **Test database operations** thoroughly before committing
3. **Maintain cross-platform compatibility**
4. **Document any new features** or API changes
5. **Preserve data integrity** in all database operations

### Reporting Issues
- Provide detailed steps to reproduce the problem
- Include system information (OS, Python version)
- Attach relevant log files or error messages
- Specify which tab/feature is affected

## 📋 System Requirements

### Minimum Requirements
- **Python:** 3.8 or higher
- **RAM:** 2GB minimum (4GB recommended)
- **Storage:** 100MB for application + space for audio files
- **Audio:** Sound card and speakers/headphones for audio playback

### Supported Platforms
- **Windows:** 10/11 (primary development platform)
- **macOS:** 10.14+ (Mojave or later)
- **Linux:** Ubuntu 18.04+, CentOS 7+, or equivalent

### Network Requirements
- Access to research data directories (network drives)
- SQLite database file permissions
- Audio file read permissions

## 📄 License

This project is developed for the WISC Lab research team. Please contact the repository owner for licensing information and usage permissions.

## 📞 Support

For technical support or questions about the Audio Vetting Application:
- **Create an issue** on GitHub for bug reports or feature requests
- **Contact the WISC Lab** for research-specific questions
- **Check the documentation** in code comments for implementation details

---

*Audio Vetting Application v1.13 - Streamlining audio file review for language development research*
