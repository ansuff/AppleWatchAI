#!/bin/bash

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Install Homebrew if not installed
if ! command_exists brew; then
    echo "Homebrew not found. Installing Homebrew..."
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
else
    echo "Homebrew is already installed."
fi

# Install Poetry using Homebrew
if ! command_exists poetry; then
    echo "Installing Poetry..."
    brew install poetry
else
    echo "Poetry is already installed."
fi

# Install npm using Homebrew
if ! command_exists npm; then
    echo "Installing npm..."
    brew install npm
else
    echo "npm is already installed."
fi

# Install nodemon globally using npm
if ! command_exists nodemon; then
    echo "Installing nodemon globally..."
    npm install -g nodemon
else
    echo "nodemon is already installed."
fi

echo "Setup complete."