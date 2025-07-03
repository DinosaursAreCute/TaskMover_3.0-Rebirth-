import subprocess
import sys
from pathlib import Path

project_root = Path('.')
env = {
    'PYTHONPATH': ';'.join([str(project_root.absolute()), str((project_root / 'tests').absolute())])
}

print("Testing individual test file execution...")
print(f"Project root: {project_root.absolute()}")
print(f"PYTHONPATH: {env['PYTHONPATH']}")

# Test running test_app.py
result = subprocess.run(
    [sys.executable, 'tests/test_app.py'],
    capture_output=True,
    text=True,
    env=env,
    cwd=str(project_root.absolute())
)

print(f"\nReturn code: {result.returncode}")
print(f"STDOUT:\n{result.stdout}")
if result.stderr:
    print(f"STDERR:\n{result.stderr}")
