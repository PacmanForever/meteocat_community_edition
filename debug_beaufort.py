
from custom_components.meteocat_community_edition.utils import get_beaufort_value

# 6.44 km/h should be 2 according to table (6-11)
# Currently predicted to be 1
val = 6.44
b_val = get_beaufort_value(val)
print(f"{val} km/h -> Beaufort {b_val}")
