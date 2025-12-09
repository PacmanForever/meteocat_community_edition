
import sys
import os

# Add the custom_components directory to path so we can import
sys.path.append(os.path.join(os.getcwd(), "custom_components"))

# Mock some HA stuff
from unittest.mock import MagicMock
sys.modules["homeassistant"] = MagicMock()
sys.modules["homeassistant.components.sensor"] = MagicMock()
sys.modules["homeassistant.const"] = MagicMock()
sys.modules["homeassistant.helpers.entity"] = MagicMock()
sys.modules["homeassistant.helpers.update_coordinator"] = MagicMock()
sys.modules["homeassistant.config_entries"] = MagicMock()
sys.modules["homeassistant.core"] = MagicMock()
sys.modules["homeassistant.helpers.entity_platform"] = MagicMock()

# Now try to import sensor.py
try:
    from custom_components.meteocat_community_edition import sensor
    print("Successfully imported sensor.py")
    
    # Check the strings in the classes
    print("Checking MeteocatLastUpdateSensor...")
    # We can't easily instantiate without mocks, but we can inspect the source or just rely on the import not failing
    
    with open("custom_components/meteocat_community_edition/sensor.py", "r", encoding="utf-8") as f:
        content = f.read()
        
    print("Searching for LastUpdate string in file content:")
    if "\\u00daltima" in content:
        print("Found literal escape sequence \\u00daltima")
    elif "Última" in content:
        print("Found literal character Última")
    else:
        print("Found neither?")
        
    # Find the line
    for line in content.splitlines():
        if "self._attr_name =" in line and "actualitzaci" in line:
            print(f"Line: {line!r}")

except Exception as e:
    print(f"Error: {e}")
