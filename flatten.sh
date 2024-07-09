#!/bin/bash

# Check if a directory is provided as an argument
if [ $# -eq 0 ]; then
    echo "Usage: $0 <target_directory>"
    exit 1
fi

# Set the target directory from the first argument
target_dir="$1"

# Check if the provided directory exists
if [ ! -d "$target_dir" ]; then
    echo "Error: Directory '$target_dir' does not exist."
    exit 1
fi

# Set up logging
log_file="${target_dir%/}_flatten_log.txt"
echo "Starting flattening process for $target_dir at $(date)" > "$log_file"

# Function to generate a unique filename in the target directory
get_unique_filename() {
    local base_name=$(basename "$1")
    local name="${base_name%.*}"
    local ext="${base_name##*.}"
    local counter=1
    local new_name="$base_name"

    while [[ -e "$target_dir/$new_name" ]]; do
        new_name="${name}_${counter}.${ext}"
        ((counter++))
    done

    echo "$new_name"
}

# Count total number of files
total_files=$(find "$target_dir" -type f | wc -l)
echo "Total files to process: $total_files" >> "$log_file"

# Initialize counter
processed=0

# Find all files (not directories) in the target directory and its subdirectories
find "$target_dir" -type f | while read -r file; do
    # Get the relative path of the file
    rel_path="${file#$target_dir/}"
    
    # If the file is already in the root of the target directory, skip it
    if [[ "$rel_path" != */* ]]; then
        echo "Skipping $rel_path (already in root)" >> "$log_file"
        ((processed++))
        continue
    fi
    
    # Generate a unique filename for the destination
    dest_file="$target_dir/$(get_unique_filename "$file")"
    
    # Move the file to the root of the target directory
    mv "$file" "$dest_file"
    
    # Log the action
    echo "Moved $rel_path to $(basename "$dest_file")" >> "$log_file"
    
    # Update and display progress
    ((processed++))
    progress=$((processed * 100 / total_files))
    echo -ne "Progress: $progress% ($processed/$total_files)\r"
done

echo # Move to a new line after progress display

# Remove empty directories
echo "Removing empty directories..." >> "$log_file"
find "$target_dir" -type d -empty -delete

echo "Flattening process completed at $(date)" >> "$log_file"
echo "Flattening process completed. Check $log_file for details."
