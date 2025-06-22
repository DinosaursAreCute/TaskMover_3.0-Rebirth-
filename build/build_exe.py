#!/usr/bin/env python3
"""
TaskMover Build Script
This script builds the TaskMover application using PyInstaller.
"""

import os
import sys
import subprocess
import shutil
import platform
import logging
import datetime
from pathlib import Path

# Configure logging
log_format = '%(asctime)s - %(levelname)s - %(message)s'
logging.basicConfig(
    level=logging.INFO,
    format=log_format,
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(f"taskmover_build_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
    ]
)
logger = logging.getLogger("TaskMoverBuild")

def check_environment():
    """Check Python version and environment"""
    logger.info(f"Python version: {platform.python_version()}")
    logger.info(f"Platform: {platform.platform()}")
    
    # Check Python version
    if sys.version_info < (3, 11):
        logger.error(f"Python 3.11 or higher required. Current version: {platform.python_version()}")
        return False
    
    # Check if we're in the correct directory
    script_dir = Path(__file__).resolve().parent
    repo_root = script_dir.parent
    if not (repo_root / "taskmover_redesign").exists():
        logger.error("Not in the expected build directory structure. Please run from the 'build' directory.")
        return False
        
    return True

def check_prerequisites():
    """Check if PyInstaller is installed"""
    try:
        subprocess.check_call(
            [sys.executable, '-m', 'pip', 'show', 'pyinstaller'], 
            stdout=subprocess.DEVNULL, 
            stderr=subprocess.DEVNULL
        )
        logger.info("PyInstaller is installed")
    except subprocess.CalledProcessError:
        logger.info("Installing PyInstaller...")
        try:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'pyinstaller'])
            logger.info("PyInstaller installed successfully")
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to install PyInstaller: {e}")
            return False

    # Check dependencies
    logger.info("Installing dependencies...")
    try:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', '../requirements-dev.txt'])
        logger.info("Dependencies installed successfully")
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to install dependencies: {e}")
        return False
        
    return True

def validate_spec_file(spec_path):
    """Validate the spec file content"""
    if not spec_path.exists():
        logger.error(f"Spec file not found at {spec_path}")
        return False
        
    with open(spec_path, 'r') as f:
        content = f.read()
        
    # Basic validation of spec file content
    required_elements = [
        "Analysis(", 
        "PYZ(", 
        "EXE(", 
        "name='TaskMover'", 
        "taskmover_redesign"
    ]
    
    for element in required_elements:
        if element not in content:
            logger.error(f"Spec file validation failed: Missing '{element}'")
            return False
            
    logger.info("Spec file validation passed")
    return True

def build_executable():
    """Build the executable using PyInstaller"""
    logger.info("Building TaskMover executable...")
    
    # Get the path to the spec file
    script_dir = Path(__file__).resolve().parent
    repo_root = script_dir.parent
    spec_path = repo_root / '.github' / 'TaskMover.spec'
    
    # Validate the spec file
    if not validate_spec_file(spec_path):
        return False
    
    try:
        # Run PyInstaller with the spec file
        logger.info(f"Running PyInstaller with spec file: {spec_path}")
        result = subprocess.run(
            [sys.executable, '-m', 'PyInstaller', str(spec_path)],
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            logger.error(f"PyInstaller failed with return code {result.returncode}")
            logger.error(f"STDOUT: {result.stdout}")
            logger.error(f"STDERR: {result.stderr}")
            return False
            
        logger.info("Build process completed")
        
        # Check if executable was created
        exe_path = repo_root / 'dist' / 'TaskMover.exe'
        if exe_path.exists():
            exe_size = exe_path.stat().st_size / (1024 * 1024)  # Size in MB
            logger.info(f"Executable created: {exe_path} ({exe_size:.2f} MB)")
            return True
        else:
            logger.error(f"Executable not found at {exe_path}")
            return False
            
    except subprocess.CalledProcessError as e:
        logger.error(f"Error building executable: {e}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error during build: {e}")
        return False

def cleanup_build_artifacts(success):
    """Clean up build artifacts based on build success"""
    script_dir = Path(__file__).resolve().parent
    repo_root = script_dir.parent
    build_dir = repo_root / 'build' / 'TaskMover'
    
    if success:
        # Keep successful build artifacts but clean up temporary files
        logger.info("Cleaning up temporary files...")
        temp_files = list(repo_root.glob('*.spec')) + list(repo_root.glob('*.log'))
        for file in temp_files:
            if file.name != 'TaskMover.spec':  # Don't delete our main spec file
                try:
                    file.unlink()
                    logger.debug(f"Deleted: {file}")
                except Exception as e:
                    logger.warning(f"Could not delete {file}: {e}")
    else:
        # On failure, clean up all build artifacts to prevent issues on next build
        logger.info("Build failed, cleaning up artifacts...")
        try:
            if (repo_root / 'build' / 'TaskMover').exists():
                shutil.rmtree(repo_root / 'build' / 'TaskMover')
                logger.info("Removed build artifacts")
        except Exception as e:
            logger.warning(f"Could not clean up build artifacts: {e}")
    
def main():
    """Main build process"""
    start_time = datetime.datetime.now()
    logger.info("=" * 50)
    logger.info("TaskMover Build Process Started")
    logger.info("=" * 50)
    
    try:
        # Check environment and prerequisites
        if not check_environment():
            logger.error("Environment validation failed")
            sys.exit(1)
            
        if not check_prerequisites():
            logger.error("Prerequisite check failed")
            sys.exit(1)
        
        # Build the executable
        success = build_executable()
        
        # Clean up based on build success
        cleanup_build_artifacts(success)
        
        # Finalize
        end_time = datetime.datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        if success:
            logger.info(f"Build completed successfully in {duration:.2f} seconds!")
            logger.info("The executable can be found in the 'dist' directory.")
        else:
            logger.error(f"Build failed after {duration:.2f} seconds. See error messages above.")
            sys.exit(1)
            
    except KeyboardInterrupt:
        logger.warning("Build process interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"An unexpected error occurred during build: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()
