#!/bin/bash

# Check environment variables
python load_env.py

# Check if PostgreSQL is installed
if ! command -v psql &> /dev/null; then
    echo "PostgreSQL command-line tools not found. Please install PostgreSQL."
    exit 1
fi

# Check if the database exists and create it if it doesn't
if ! psql -lqt | cut -d \| -f 1 | grep -qw erp; then
    echo "Creating ERP database..."
    createdb erp
    psql -d erp -f db_schema.sql
else
    echo "ERP database exists."
    # Ask if user wants to reset the database
    read -p "Do you want to reset the database schema? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "Resetting database schema..."
        psql -d erp -f db_schema.sql
    fi
fi

# Ask which interface to start
echo "Select the interface to start:"
echo "1) Command-line interface"
echo "2) Web-based chat interface"
read -p "Enter choice (1-2): " -n 1 -r
echo

case $REPLY in
    1)
        echo "Starting command-line interface..."
        python erp_system.py
        ;;
    2)
        echo "Starting web-based chat interface..."
        python chat_frontend.py
        ;;
    *)
        echo "Invalid choice. Exiting."
        exit 1
        ;;
esac 