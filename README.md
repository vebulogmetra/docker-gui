# Docker GUI

A modern graphical user interface for Docker management with enhanced user experience.

## 🚀 Quick Start

### Running the Application

```bash
# Make the script executable
chmod +x run.sh

# Run the application
./run.sh
```

Or directly via uv:

```bash
uv run main.py
```

### Building AppImage

```bash
# Navigate to appimage directory
cd appimage

# Or full build
./build.sh

# Run the AppImage
chmod +x ../dist/docker-gui-0.1.0-x86_64.AppImage
../dist/docker-gui-0.1.0-x86_64.AppImage
```

## ✨ Features

### 🎨 Modern Interface
- **Card Design**: Visually appealing cards for resource display
- **Dual View Mode**: Cards and lists for each section
- **Responsive Design**: Works on different screen sizes
- **Theme System**: Switch between light and dark themes
- **GTK4 Support**: Modern GTK4 interface for better performance

### 📊 Navigation
- **Dashboard**: System overview with quick actions
- **Images**: Docker image management
- **Containers**: Container management
- **Networks**: Network management
- **Volumes**: Volume management

### 🔍 Search and Filtering
- Search across all resource types
- Filter by status, size, date
- Quick filters with chips

### ⚡ Functionality
- **Complete Management**: All actions from the original application
- **Bulk Operations**: Select and manage multiple resources
- **Notification System**: Informative messages about actions
- **Status Panel**: System statistics display
- **Memory Optimization**: Built-in memory monitoring and cleanup

## 🏗️ Architecture

### Component Structure
```
ui/
├── components/          # UI components
│   ├── card.py         # Resource cards
│   ├── dashboard.py    # Dashboard
│   ├── notifications.py # Notification system
│   ├── search.py       # Search and filtering
│   ├── status_bar.py   # Status panel
│   └── status_card.py  # Status cards
└── themes/             # Theme system
    ├── theme_manager.py # Theme manager
    ├── light_theme.py  # Light theme
    └── dark_theme.py   # Dark theme

core/                   # Core functionality
├── base_operations.py  # Base operations
├── resource_manager.py # Resource management
└── resource_view.py    # Resource views

services/               # Service layer
├── docker_service.py   # Docker service
├── memory_service.py   # Memory management
└── notification_service.py # Notifications

resources/              # Resource managers
├── containers.py       # Container management
├── images.py          # Image management
├── networks.py        # Network management
└── volumes.py         # Volume management
```

### Main Files
- `main.py`: Main application entry point
- `docker_api.py`: Docker API client
- `run.sh`: Application launcher script

## 🎯 Usage

### Navigation
1. **Dashboard**: Click "📊 Dashboard" for system overview
2. **Sections**: Switch between Images, Containers, Networks, Volumes
3. **View Modes**: Use "Cards" and "List" tabs

### Resource Management
1. **Selection**: Check resources with checkboxes in list or select cards
2. **Actions**: Use action buttons (Delete, Stop, Clean)
3. **Search**: Enter text in search bar for filtering
4. **Filters**: Use filter panel to refine results

### Themes
- Click "🌙" or "☀️" button in header to switch themes
- Theme persists between sessions

## 🔧 Development

### Dependencies
```bash
# Install dependencies
uv sync

# Or manually
uv add docker pygobject pillow psutil
```

### Testing
```bash
# Run all tests
uv run pytest tests/ -v

# Run with coverage
uv run pytest tests/ --cov=. --cov-report=html
```

### Test Structure
- `tests/unit/`: Unit tests for API and dependencies
- `tests/integration/`: Integration tests for GUI components
- `tests/e2e/`: End-to-end tests for user scenarios

## 📋 Requirements

### System Requirements
- Python 3.10+
- GTK4
- Docker
- uv (package manager)

### Installing Dependencies
```bash
# Ubuntu/Debian
sudo apt-get install python3-gi python3-gi-cairo gir1.2-gtk-4.0

# CentOS/RHEL/Fedora
sudo dnf install python3-gobject gtk4-devel

# Arch Linux
sudo pacman -S python-gobject gtk4

# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh
```

## 🎨 Design

### Design Principles
- **Minimalism**: Clean and intuitive interface
- **Consistency**: Uniform elements and behavior
- **Accessibility**: Support for various users
- **Performance**: Fast operation with large data volumes

### Color Scheme
- **Light Theme**: White background with gray accents
- **Dark Theme**: Dark background with contrasting elements
- **Accents**: Blue for primary actions, red for deletion

## 🚀 Performance

### Optimizations
- **Lazy Loading**: Data loads on demand
- **Virtual Lists**: Efficient handling of large lists
- **Async Operations**: Non-blocking interface
- **Caching**: Storage of frequently used data
- **Memory Monitoring**: Built-in memory management

### Monitoring
- Status panel shows current state
- Progress indicators for long operations
- Notifications about operation completion

## 🔒 Security

### Docker API
- Secure connection to Docker daemon
- Permission checking
- Connection error handling

### User Data
- Local settings storage
- Secure data transmission
- Operation logging

## 📦 AppImage

### Features
- **Self-contained**: Includes Python runtime and all dependencies
- **GTK4 Support**: Modern GTK4 libraries included
- **Portable**: Works on most Linux distributions
- **No Installation**: Run directly without system installation

### Building AppImage
```bash
cd appimage
./build.sh
```

### AppImage Structure
```
appimage/
├── AppRun              # Application launcher
├── build.sh            # Build script
├── create_icon.py      # Icon generator
├── icon.png            # Application icon
├── docker-gui.desktop  # Desktop integration
└── README.md           # AppImage documentation
```

### AppImage Requirements
- **Docker**: Must be installed and running
- **Memory**: 512MB RAM minimum
- **Storage**: 200MB for AppImage
- **Architecture**: x86_64

## 📈 Development Plans

### Immediate Improvements
- [x] AppImage packaging
- [ ] Additional filters
- [ ] Data export
- [ ] Keyboard shortcuts

### Long-term Plans
- [ ] Docker Compose support
- [ ] Real-time monitoring
- [ ] CI/CD integration
- [ ] Mobile version

## 🤝 Contributing

### Reporting Issues
1. Check existing issues
2. Create new issue with detailed description
3. Attach logs and screenshots

### Development
1. Fork the repository
2. Create branch for new feature
3. Write tests
4. Create pull request