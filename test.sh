#!/bin/bash

# Define allowed prefixes
allowed_paths=("/var/" "/home/")

# Function to check if path is allowed
is_allowed_path() {
    local path="$1"
    for allowed in "${allowed_paths[@]}"; do
        if [[ "$path" == "$allowed"* ]]; then
            return 0
        fi
    done
    return 1
}

# Process each directory passed as an argument
for dir in "$@"; do
    # 1. Sanitize: Remove "../" to prevent path traversal
    # This is the Bash equivalent of the 'gsub' you had in jq
    clean_dir="${dir//..\//}"

    # 2. Validate
    if is_allowed_path "$clean_dir"; then
        echo "Validating: $clean_dir - [SUCCESS]"
        # Run your command here (e.g., backy or tar)
        # /usr/bin/backy --path "$clean_dir" 
    else
        echo "Error: $clean_dir is NOT allowed."
        exit 1
    fi
done
