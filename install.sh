#!/bin/bash

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to detect the operating system
detect_os() {
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        if command_exists apt-get; then
            if [[ -f /etc/lsb-release && "$(cat /etc/lsb-release | grep DISTRIB_ID)" == "DISTRIB_ID=Ubuntu" ]]; then
                echo "ubuntu"
            else
                echo "debian"
            fi
        elif command_exists dnf; then
            echo "fedora"
        elif command_exists yum; then
            echo "centos"
        else
            echo "unknown_linux"
        fi
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        echo "macos"
    else
        echo "unknown"
    fi
}

# Function to install Python and pip
install_python() {
    local os_type=$(detect_os)
    case $os_type in
        ubuntu|debian)
            sudo apt-get update && sudo apt-get install -y python3 python3-pip
            ;;
        fedora|centos)
            sudo dnf install -y python3 python3-pip
            ;;
        macos)
            if ! command_exists brew; then
                install_homebrew
            fi
            brew install python  # This installs pip3 as well
            ;;
        *)
            echo "Unable to install Python and pip. Please install them manually."
            exit 1
            ;;
    esac
}

# Function to install Git
install_git() {
    local os_type=$(detect_os)
    case $os_type in
        ubuntu|debian)
            sudo apt-get update && sudo apt-get install -y git
            ;;
        fedora)
            sudo dnf install -y git
            ;;
        centos)
            sudo yum install -y git
            ;;
        macos)
            if ! command_exists brew; then
                install_homebrew
            fi
            brew install git
            ;;
        *)
            echo "Unable to install Git. Please install it manually."
            exit 1
            ;;
    esac
}

# Function to ensure pip is installed
ensure_pip() {
    if ! command_exists pip3; then
        echo "pip3 is not installed. Installing pip..."
        local os_type=$(detect_os)
        case $os_type in
            ubuntu|debian)
                sudo apt-get update && sudo apt-get install -y python3-pip
                ;;
            fedora|centos)
                sudo dnf install -y python3-pip
                ;;
            macos)
                if ! command_exists brew; then
                    install_homebrew
                fi
                brew install python  # This installs pip3 as well
                ;;
            *)
                echo "Unable to install pip. Please install it manually."
                exit 1
                ;;
        esac
    else
        echo "pip3 already installed"
    fi
}

# Function to ensure venv is installed
ensure_venv() {
    echo " "
    echo "Installing python3-ven..."
    local os_type=$(detect_os)
    case $os_type in
        ubuntu|debian)
            sudo apt-get update
            sudo apt install -y python3-venv
            ;;
        fedora|centos)
            sudo dnf update -y
            sudo dnf install -y python3-venv
            ;;
        macos)
            echo "venv should be included with Python on macOS. If issues persist, try reinstalling Python."
            ;;
        *)
            echo "Unable to install python3-venv. Please install it manually."
            exit 1
            ;;
    esac
    echo "python3-ven installed"
}


# Function to create virtual environment
create_venv() {
    echo " "
    echo "Creating virtual environment..."
    python3 -m venv n8n-auto-install/env
    echo "Virtual environment 'env' created."
}



# Main execution
echo " "
echo "This script will install Git, Python, and set up a virtual environment for n8n-auto-install."
echo "Do you want to proceed? (y/n): "
read -r REPLY </dev/tty

if [[ ! $REPLY =~ ^[Yy](es)?$ ]]
then
    echo "Installation cancelled."
    exit 1
fi

# Check and install Python if necessary
if ! command_exists python3; then
    echo " "
    echo "Python is not installed. Installing Python..."
    install_python
else
    echo " "
    echo "Python is already installed."
fi

# Check and install pip
ensure_pip

# Check and install python virtual environment
ensure_venv

# Check and install Git if necessary
if ! command_exists git; then
    echo " "
    echo "Git is not installed. Installing Git..."
    install_git
else
    echo " "
    echo "Git is already installed."
fi


# Clone the repository
echo " "
echo "Cloning the repository..."
git clone https://github.com/liamdmcgarrigle/n8n-auto-install.git
echo "Repository successfully cloned"
echo " "



# Create the virtual environment
create_venv
