import os
import subprocess
import sys
import time
from typing import Tuple
from rich.progress import Progress, SpinnerColumn, TextColumn
from cli.core.exceptions import CLIException
from cli.service.interface.base_service import IVenvService

class VenvService(IVenvService):
    """🔧 Service for managing Python virtual environments"""
    
    def __init__(self):
        """Initialize VenvService with Python executable"""
        self.python_exe = sys.executable

    def _validate_path(self, path: str) -> bool:
        """🔍 Validates if path exists and has write permissions"""
        try:
            return os.path.exists(path) and os.access(path, os.W_OK)
        except Exception:
            return False
    
    def _venv_exists(self, path: str) -> bool:
        """📂 Checks if virtual environment already exists"""
        venv_path = os.path.join(path, "venv")
        pyvenv_cfg = os.path.join(venv_path, "pyvenv.cfg")
        return os.path.exists(venv_path) and os.path.isfile(pyvenv_cfg)

    def create_venv(self, path: str) -> Tuple[bool, str]:
        """🏗️ Creates a new Python virtual environment
        
        Args:
            path (str): Directory where venv will be created
            
        Returns:
            Tuple[bool, str]: Success status and message
            
        Raises:
            CLIException: If there's an error creating the venv
        """
        try:
            if not self._validate_path(path):
                raise CLIException(f"❌ Path '{path}' does not exist or has no write permissions")
            
            if self._venv_exists(path):
                raise CLIException("⚠️ Virtual environment already exists")
            
            venv_path = os.path.join(path, "venv")
            
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                transient=True,
            ) as progress:
                progress.add_task(description="🔨 Creating virtual environment...", total=None)
                
                result = subprocess.run(
                    [self.python_exe, "-m", "venv", venv_path],
                    check=True,
                    capture_output=True,
                    text=True
                )
                
                time.sleep(1)
            
            if result.returncode != 0:
                raise CLIException(f"💥 Error creating venv: {result.stderr}")
                
            return True, "✅ Virtual environment created successfully"
            
        except subprocess.CalledProcessError as e:
            raise CLIException(f"💥 Error executing venv command: {e.stderr}")
        except CLIException:
            raise
        except Exception as e:
            raise CLIException(f"💥 Unexpected error creating venv: {str(e)}")