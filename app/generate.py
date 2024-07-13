import os

# Specify the paths to the folders
template_folders = [
    r'C:\Users\User\Downloads\Compressed\lspu-siniloan-library-management-systems-main\app\templates\admin',
    r'C:\Users\User\Downloads\Compressed\lspu-siniloan-library-management-systems-main\app\templates\admin\auth',
    r'C:\Users\User\Downloads\Compressed\lspu-siniloan-library-management-systems-main\app\templates\admin\components'
]

# Function to recursively traverse the folder and its subfolders
def extract_jinja_files(folder_path):
    jinja_files = []
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.endswith('.jinja'):
                file_path = os.path.join(root, file)
                jinja_files.append(file_path)
    return jinja_files

# Get a list of full paths of .jinja files
jinja_files = []
for folder in template_folders:
    jinja_files.extend(extract_jinja_files(folder))

# Convert the file paths to a raw text string
jinja_files_text = '\n'.join(jinja_files)

# Specify the path to the output text file on your desktop
output_file_path = r'C:\Users\User\Desktop\jinja_files.txt'

# Write the raw text of file paths to the text file
with open(output_file_path, 'w') as f:
    f.write(jinja_files_text)
