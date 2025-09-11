# Audio Vetting Application (AVA)

A comprehensive desktop application for vetting and managing experimental audio files from the WISC Lab. Built with Python and Flet, this application provides an intuitive interface for researchers to review, categorize, and track the status of audio files in longitudinal studies.

## 🎯 Purpose

The Audio Vetting Application (AVA) is designed to streamline the process of reviewing and organizing experimental audio files collected from child language development studies. It provides researchers with tools to:

- **Vet individual audio files** with playback controls and status tracking
- **Manage file assignments** across multiple workers/researchers
- **Track completion status** of audio file reviews
- **Synchronize data** between different storage systems (STOCS, SSS files)
- **Generate reports** on vetting progress and file organization

## High Level Components

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

### Low Level Components
- **SQLDataTable class** - Handles database queries and Flet DataTable conversion
- **Playback integration** - Audio file playback using just-playback library
- **Cross-platform paths** - Automatic path resolution for different operating systems
- **Database connection management** - SQLite with optimized settings

## Architecture

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
├── main.py               # Main application entry point
├── vetting_tab.py        # Audio vetting interface
├── utilities_tab.py      # Data management utilities  
├── db_initialization.py  # Database setup and schema
├── db_updates.py         # Database operations
├── dt_updates.py         # Data table updates
├── icon.png              # Application icon
├── build.txt             # Build command
└── README.md             # This file
```

## 🚀 Installation

TODO (Dependency war in progress)

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
- **Review files** using the referenced audio player
- **Update status** (Complete, Incomplete (default), Flagged)
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

TODO (Dependency war ongoing)

## 📦 Building & Distribution

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

---

*Audio Vetting Application v1.13 - Streamlining audio file review for speech research*
