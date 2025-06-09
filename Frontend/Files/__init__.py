"""
Initialization file for Files directory.
This directory is used for storing temporary data files and communication between components.
"""

import os

# Create necessary files if they don't exist
def init():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # List of required files
    required_files = [
        'ImageGeneration.data',
        'Mic.data',
        'Responses.data',
        'Status.data'
    ]
    
    # Create each file if it doesn't exist
    for file in required_files:
        file_path = os.path.join(current_dir, file)
        if not os.path.exists(file_path):
            with open(file_path, 'w') as f:
                if file == 'ImageGeneration.data':
                    f.write('None,False')
                elif file == 'Mic.data':
                    f.write('False')
                elif file == 'Status.data':
                    f.write('Ready')
                else:
                    f.write('')

# Initialize files when module is imported
init() 