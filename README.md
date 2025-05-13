# TaskMover
TaskMover is a Python-based file organization tool that allows users to define rules for organizing files in a directory. It supports features like pattern matching, file moving, unzipping, and a graphical user interface for managing rules.

## Features
- Define rules for organizing files based on patterns.
- Automatically move files to specified directories.
- Unzip `.zip` files into target directories.
- Enable or disable rules dynamically.
- Graphical user interface (GUI) for managing rules and configurations.
- Customizable themes and colors.

## Requirements
- Python 3.x

### Built-in Python Modules (No Installation Required)
- `os`
- `shutil`
- `fnmatch`
- `logging`
- `zipfile`
- `tkinter`

### External Python Libraries (Require Installation)
### Installing Dependencies on Windows
1. **ttkbootstrap**  
   Install with:
   ```bash
   pip install ttkbootstrap
   ```
2. **PyYAML**  
   Install with:
   ```bash
   pip install PyYAML
   ```
3. **colorlog**  
   Install with:
   ```bash
   pip install colorlog
   ```

Or simply:
```bash
pip install -r requirements.txt
```


### Installing Dependencies on Linux
For Linux users, follow the steps below based on your distribution:

 **Warning:** Linux support is currently limited due to windows specific calls. Will be fixed in a later update.

#### Ubuntu/Debian
```bash
sudo apt update
sudo apt install -y python3 python3-pip
pip install -r requirements.txt
```

#### Fedora
```bash
sudo dnf install -y python3 python3-pip
pip install -r requirements.txt
```

#### Arch Linux
```bash
sudo pacman -Sy python python-pip
pip install -r requirements.txt
```

#### openSUSE
```bash
sudo zypper install -y python3 python3-pip
pip install -r requirements.txt
```

## Getting Started
1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/TaskMover.git
   cd TaskMover
   ```
2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
3. **Run the application:**
   ```powershell
   python -m taskmover
   ```

## Quick Tutorial
### 1. Launch TaskMover
Run the following command in your project directory:
```powershell
python -m taskmover
```

### 2. Set Up Your Base Directory
On first launch, you’ll be prompted to select a base directory. This is where your settings and rules will be stored.

### 3. Add a Rule
- Click the "Add Rule" button in the main window.
- Enter a name, file pattern (e.g., `*.pdf`), and destination path.
- Optionally enable unzipping and toggle the rule’s active status.
- Click "Save" to add the rule.

### 4. Organize Files
- Click the "Organize" button to move files according to your rules.
- Progress and logs will be shown in the application window.

### 5. Customize
- Change the theme or colors from the Settings menu.
- Use developer tools for testing and debugging (see Documentation).

## Documentation
For detailed documentation, refer to:
- [Changelog](./CHANGELOG.md): List of changes in each version.
- [Documentation](./DOCUMENTATION.md): Full usage and API details.
- [Requirements](./requirements.txt): List of dependencies.

## Known Bugs
- [ ] **Browse Button**: The "Browse" button is currently not available in some parts of the application.
- [ ] **Dummy Files**: Creating dummy files does not work as expected in certain scenarios.

## License
This project is licensed under the MIT License. See the LICENSE file for details.
