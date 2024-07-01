import re

def extract_libraries(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    # Find all import statements
    imports = re.findall(r'^\s*(?:import|from)\s+(\S+)', content, re.MULTILINE)
    # Filter out standard libraries (rough estimate)
    standard_libs = {
        'sys', 'os', 're', 'math', 'json', 'time', 'datetime', 'logging',
        'collections', 'itertools', 'functools', 'random', 'threading', 'subprocess'
    }
    libraries = set()
    for imp in imports:
        lib = imp.split('.')[0]
        if lib not in standard_libs:
            # Replace cv2 with opencv-python
            if lib == 'cv2':
                lib = 'opencv-python'
            libraries.add(lib)
    return libraries

file_paths = [
    'C:\\Users\\yuki\\Documents\\toio_python\\toio_tutorial.py',
    'C:\\Users\\yuki\\Documents\\toio_python\\ar_marker_detection.py'
]
all_libraries = set()
for file_path in file_paths:
    all_libraries.update(extract_libraries(file_path))

# Write to requirements.txt
with open('C:\\Users\\yuki\\Documents\\toio_python\\requirements.txt', 'w', encoding='utf-8') as req_file:
    for lib in sorted(all_libraries):
        req_file.write(f"{lib}\n")

print("requirements.txt has been created with the following libraries:")
print(sorted(all_libraries))
