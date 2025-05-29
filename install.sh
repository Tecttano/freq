#!/bin/bash

# freq - Shell History Analyzer Installation Script
# This script installs freq.py to make it available as 'freq' command system-wide

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Script information
SCRIPT_NAME="freq.py"
COMMAND_NAME="freq"
INSTALL_DIR="/usr/local/bin"

# Functions
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

check_requirements() {
    print_info "Checking requirements..."
    
    # Check if Python 3 is installed
    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 is not installed. Please install Python 3 first."
        exit 1
    fi
    
    # Check if freq.py exists
    if [[ ! -f "$SCRIPT_NAME" ]]; then
        print_error "$SCRIPT_NAME not found in current directory."
        print_info "Please run this script from the directory containing $SCRIPT_NAME"
        exit 1
    fi
    
    print_success "Requirements check passed"
}

install_freq() {
    print_info "Installing $COMMAND_NAME to $INSTALL_DIR..."
    
    # Create install directory if it doesn't exist
    if [[ ! -d "$INSTALL_DIR" ]]; then
        print_warning "$INSTALL_DIR doesn't exist, creating it..."
        sudo mkdir -p "$INSTALL_DIR"
    fi
    
    # Copy the script
    sudo cp "$SCRIPT_NAME" "$INSTALL_DIR/$COMMAND_NAME"
    
    # Make it executable
    sudo chmod +x "$INSTALL_DIR/$COMMAND_NAME"
    
    print_success "$COMMAND_NAME installed to $INSTALL_DIR/$COMMAND_NAME"
}

verify_installation() {
    print_info "Verifying installation..."
    
    # Check if the command is available in PATH
    if command -v "$COMMAND_NAME" &> /dev/null; then
        print_success "$COMMAND_NAME is now available in your PATH"
        print_info "You can now use: $COMMAND_NAME"
        
        # Show version/help
        print_info "Testing installation:"
        "$COMMAND_NAME" --help | head -1
    else
        print_warning "$COMMAND_NAME is installed but not in your PATH"
        print_info "You may need to restart your shell or run: source ~/.bashrc"
        print_info "If the issue persists, add $INSTALL_DIR to your PATH manually"
    fi
}

uninstall_freq() {
    print_info "Uninstalling $COMMAND_NAME..."
    
    if [[ -f "$INSTALL_DIR/$COMMAND_NAME" ]]; then
        sudo rm "$INSTALL_DIR/$COMMAND_NAME"
        print_success "$COMMAND_NAME has been uninstalled"
    else
        print_warning "$COMMAND_NAME was not found in $INSTALL_DIR"
    fi
}

show_usage() {
    echo "freq Installation Script"
    echo ""
    echo "Usage: $0 [OPTION]"
    echo ""
    echo "Options:"
    echo "  install     Install freq command (default)"
    echo "  uninstall   Remove freq command"
    echo "  --help      Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0                # Install freq"
    echo "  $0 install        # Install freq"
    echo "  $0 uninstall      # Remove freq"
}

# Main script logic
main() {
    case "${1:-install}" in
        "install")
            echo "=== freq Installation Script ==="
            check_requirements
            install_freq
            verify_installation
            echo ""
            print_success "Installation complete! You can now use 'freq' command."
            print_info "Try: freq --help"
            ;;
        "uninstall")
            echo "=== freq Uninstallation Script ==="
            uninstall_freq
            ;;
        "--help"|"-h"|"help")
            show_usage
            ;;
        *)
            print_error "Unknown option: $1"
            show_usage
            exit 1
            ;;
    esac
}

# Check if running as root for sudo operations
if [[ $EUID -eq 0 ]]; then
    print_warning "Running as root. Installation will proceed without sudo."
fi

# Run main function
main "$@"