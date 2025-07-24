#!/bin/bash
# Fix permissions for output directory
# For Kali Linux / Unix systems

echo "Setting full permissions on output directory..."

# Create output directory if it doesn't exist
if [ ! -d "output" ]; then
    echo "Creating output directory..."
    mkdir -p output
fi

# Set permissions to 777 (read, write, execute for owner, group, and others)
chmod 777 output

# Also fix permissions for any existing files in the directory
if [ "$(ls -A output 2>/dev/null)" ]; then
    echo "Setting permissions on existing files..."
    chmod 666 output/*
fi

echo "Permissions updated successfully!"
echo "Directory permissions: $(ls -ld output | cut -d' ' -f1)"
