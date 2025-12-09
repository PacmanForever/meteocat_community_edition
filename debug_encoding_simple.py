
import os

file_path = "custom_components/meteocat_community_edition/sensor.py"

print(f"Reading {file_path}...")
try:
    with open(file_path, "rb") as f:
        content_bytes = f.read()
        
    print(f"File size: {len(content_bytes)} bytes")
    
    # Check for specific byte sequences
    # \u00daltima -> 5c 75 30 30 64 61 6c 74 69 6d 61
    # Última (UTF-8) -> c3 9a 6c 74 69 6d 61
    # Ãšltima (UTF-8 for Ãš) -> c3 83 c5 9a ...
    
    target_lines = []
    content_str = content_bytes.decode("utf-8")
    for i, line in enumerate(content_str.splitlines()):
        if "_attr_name =" in line and "actualitzaci" in line:
            target_lines.append((i+1, line))
        if "_attr_name =" in line and "Predicci" in line:
            target_lines.append((i+1, line))

    for lineno, line in target_lines:
        print(f"Line {lineno}: {line!r}")
        # Print hex of the line
        # print(f"Hex: {line.encode('utf-8').hex(' ')}")

except Exception as e:
    print(f"Error: {e}")
