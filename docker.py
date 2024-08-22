"""
Docker and Docker Compose Installation Script

This script automates the installation of Docker and Docker Compose on Linux and macOS systems.
It first checks if Docker is already installed, and only proceeds with installation if it's not present.
It detects the operating system and uses the appropriate installation method:
- For Linux: Uses Docker's official installation script and installs Docker Compose separately.
- For macOS: Installs Docker Desktop (which includes Docker Compose) using Homebrew.

Usage:
    Run this script with appropriate permissions (e.g., using sudo on Linux).
    python3 install_docker.py

Requirements:
    - Python 3.6+
    - Internet connection
    - Sudo privileges (for Linux)

Note:
    On macOS, the script will attempt to install Homebrew if it's not already installed.
"""
from utils import run_command
import platform
import subprocess
import sys
import requests
import time


def _command_exists(cmd):
    return subprocess.call(f"type {cmd}", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE) == 0

def _get_latest_docker_compose_version():
    url = "https://api.github.com/repos/docker/compose/releases/latest"
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()["tag_name"]
    except requests.RequestException as e:
        print(f"Failed to fetch the latest Docker Compose version: {e}")
        sys.exit(1)

def _is_docker_installed():
    print("\nChecking if docker is installed...")
    return _command_exists("docker") and subprocess.call("docker info >/dev/null 2>&1", shell=True) == 0

def _install_docker_linux():
    if _is_docker_installed():
        print("Docker is already installed.")
    else:
        print("Installing Docker...")
        run_command("curl -fsSL https://get.docker.com -o get-docker.sh")
        run_command("sudo sh get-docker.sh")
        run_command("rm get-docker.sh")
    
    if _command_exists("docker-compose"):
        print("Docker Compose is already installed.")
    else:
        _install_docker_compose()

def _install_docker_compose():
    latest_version = _get_latest_docker_compose_version()
    run_command(f"sudo curl -L https://github.com/docker/compose/releases/download/{latest_version}/docker-compose-$(uname -s)-$(uname -m) -o /usr/local/bin/docker-compose")
    run_command("sudo chmod +x /usr/local/bin/docker-compose")
    print(f"Docker Compose {latest_version} has been installed successfully!")

def _install_homebrew():
    print("Homebrew not found. Installing Homebrew...")
    run_command('/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"')
    print("Homebrew installed successfully.")

def _install_docker_mac():
    if _is_docker_installed():
        print("Docker is installed.")
        return

    if not _command_exists("brew"):
        _install_homebrew()
    
    print("Installing Docker via homebrew... (this will take a few minutes and will require a password)")
    run_command("brew install --cask docker")
    print("Docker Desktop has been installed.")
    
    print("Launching Docker Desktop...")
    time.sleep(5)
    run_command("open /Applications/Docker.app")
    
    print("\nIMPORTANT: To complete the setup, please do the following:")
    print("1. If docker desktop does not open automatically, go to your applications folder and OPEN IT MANUALLY.")
    print("2. Wait for Docker Desktop to finish starting up (you'll see the whale icon in the menu bar).")
    print("3. Once Docker Desktop is running, you can use 'docker' and 'docker-compose' commands in the terminal.")
    print("\nNOTE: It may take a minute or two for Docker Desktop to fully start up.")
    print("If you don't see the Docker whale icon in the menu bar, please open Docker Desktop manually from the Applications folder.")
    

def _wait_for_docker_daemon():
    print("Waiting for Docker daemon to start...")
    max_attempts = 60
    for attempt in range(max_attempts):
        if _is_docker_installed():
            print("Docker daemon is now running.")
            return
        if attempt % 10 == 0 and attempt > 0:
            print(f"Still waiting for Docker daemon... (Attempt {attempt}/{max_attempts})")
        time.sleep(5)
    print("Warning: Docker daemon didn't start within the expected time.")
    print("Ensure that docker desktop opened and the engine is running.")
    print("Once it is restart the script.")
    exit()

def install_docker():
    """
    Install Docker and Docker Compose based on the detected operating system.

    This function first checks if Docker is already installed. If it is, it informs
    the user and exits. If Docker is not installed, it determines the current operating 
    system and calls the appropriate installation function. It supports Linux and macOS (Darwin).

    For Linux:
    - Uses Docker's official installation script
    - Installs Docker Compose separately if not already installed

    For macOS:
    - Installs Docker Desktop using Homebrew (which includes Docker Compose)
    - Launches Docker Desktop and waits for the Docker daemon to start

    Raises:
        SystemExit: If an unsupported operating system is detected

    Returns:
        None
    """
    system = platform.system()

    if system == "Linux":
        _install_docker_linux()
    elif system == "Darwin":
        _install_docker_mac()
        _wait_for_docker_daemon()
    else:
        print(f"Unsupported operating system: {system}")
        sys.exit(1)