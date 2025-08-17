#!/usr/bin/env python3
"""Script to find reportPrivateUsage entries in vscode-problems.json."""

import json
from pathlib import Path

def find_private_usage_issues(json_file_path: str) -> None:
    """Find all reportPrivateUsage issues in the JSON file."""
    try:
        with open(json_file_path, 'r', encoding='utf-8') as f:
            content = f.read().strip()
        
        if not content:
            print(f"File {json_file_path} is empty.")
            return
            
        data = json.loads(content)
        
        # Handle both list of entries and single entry
        entries = data if isinstance(data, list) else [data]
        
        private_usage_issues = []
        
        for entry in entries:
            # Check if this entry has reportPrivateUsage code
            if (isinstance(entry, dict) and 
                'code' in entry and 
                isinstance(entry['code'], dict) and 
                entry['code'].get('value') == 'reportPrivateUsage'):
                
                private_usage_issues.append(entry)
        
        if not private_usage_issues:
            print("No reportPrivateUsage issues found.")
            return
            
        # Output simple format: file_path:line_number
        for issue in private_usage_issues:
            resource = issue.get('resource', '')
            line = issue.get('startLineNumber', '')
            
            if resource and line:
                print(f"{resource}:{line}")
            elif resource:
                print(f"{resource}:?")
            else:
                print("unknown_file:?")
            
    except FileNotFoundError:
        print(f"Error: File not found: {json_file_path}")
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in file: {e}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    json_file = ".dev/vscode-problems.json"
    find_private_usage_issues(json_file)