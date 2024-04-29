#!/bin/bash

# Define the directory to search for Python files
DIRECTORY="../../DEVOPS"

# Find all Python files in the directory and its subdirectories
PYTHON_FILES=$(find "$DIRECTORY" -name "*.py")

# Flag to track if any files are not formatted correctly
FLAG=false

# Iterate over each Python file found
for FILE in $PYTHON_FILES; do
    # Check if the file is properly formatted with black
    black --check "$FILE" &> /dev/null
    
    # If black returns a non-zero exit code, set the flag to true
    if [ $? -ne 0 ]; then
        echo "File $FILE is not properly formatted with black. Formatting..."
        black "$FILE" &> /dev/null
        # Check again after formatting
        black --check "$FILE" &> /dev/null
        if [ $? -ne 0 ]; then
            echo "Failed to format file $FILE. Please check manually."
        else
            echo "File $FILE has been successfully formatted with black."
        fi
        FLAG=true
    else
        echo "File $FILE is properly formatted with black."
    fi
done

# Check the flag to determine if any files were not properly formatted
if [ "$FLAG" = true ]; then
    echo "Some files were not properly formatted but have been formatted now."
else
    echo "All Python files are properly formatted with black."
fi
