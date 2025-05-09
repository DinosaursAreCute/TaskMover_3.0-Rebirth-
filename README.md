# TaskMover
TaskMover is a Python-based file organization tool that allows users to define rules for organizing files in a directory. It supports features like pattern matching, file moving, unzipping, and a graphical user interface for managing rules.

## Features
- Define rules for organizing files based on patterns.
- Automatically move files to specified directories.
- Unzip `.zip` files into target directories.
- Enable or disable rules dynamically.
- Graphical user interface (GUI) for managing rules and configurations.
- Customizable themes and colors.
- Developer tools for testing


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

## Getting Started
1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/TaskMover.git
   cd TaskMover
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the application:
   ```bash
   python main.py
   ```

## Documentation
For detailed documentation, refer to the following files:
- [Changelog](./CHANGELOG.md): A detailed list of changes made in each version.
- [Requirements](./requirements.txt): A list of dependencies required for the project.

## Known Bugs
- [ ] **Browse Button**: The "Browse" button is currently not available in some parts of the application.
- [ ] **Dummy Files**: Creating dummy files does not work as expected in certain scenarios.

## Contributing
Currently closed

## License
This project is licensed under the MIT License. See the LICENSE file for details.