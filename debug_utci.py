
import math

def debug_utci(temp_c, humidity_percent, wind_speed_kmh):
    print(f"Debug UTCI for Ta={temp_c}, RH={humidity_percent}, v_kmh={wind_speed_kmh}")
    
    wind_ms = wind_speed_kmh / 3.6
    
    tdb = max(-50.0, min(50.0, temp_c))
    v_10m = max(0.5, min(17.0, wind_ms))
    cur_rh = max(0.0, min(100.0, humidity_percent))
    
    print(f"  Inputs clamped: Ta={tdb}, v_10m={v_10m}, RH={cur_rh}")
    
    tmrt = tdb
    d_tr = tmrt - tdb
    
    es_hpa = 6.112 * math.exp((17.62 * tdb) / (243.12 + tdb))
    e_hpa = (cur_rh / 100.0) * es_hpa
    pa = e_hpa / 10.0
    print(f"  Pa (kPa): {pa}")
    
    offset = 0.0
    
    # Block 1: Ta only
    b1 = 0.0
    b1 += 0.607562052
    b1 += -0.0227712343 * tdb
    b1 += 8.06470249e-4 * tdb**2
    b1 += -1.54271372e-4 * tdb**3
    b1 += -3.24651735e-6 * tdb**4
    b1 += 7.32602852e-8 * tdb**5
    b1 += 1.35959073e-9 * tdb**6
    print(f"  Block 1 (Ta): {b1}")
    offset += b1
    
    # Block 2: v only
    b2 = 0.0
    v = v_10m
    b2 += -2.25836520 * v
    b2 += -0.751269505 * v**2
    b2 += 0.158137256 * v**3
    b2 += -0.0127762753 * v**4
    b2 += 4.56306672e-4 * v**5
    b2 += -5.91491269e-6 * v**6
    print(f"  Block 2 (v): {b2}")
    offset += b2
    
    # Block 3: Ta and v
    b3 = 0.0
    b3 += 0.0880326035 * tdb * v
    b3 += 0.00216844454 * tdb**2 * v
    b3 += -1.53347087e-5 * tdb**3 * v
    b3 += -5.72983704e-7 * tdb**4 * v
    b3 += -2.55090145e-9 * tdb**5 * v
    b3 += -0.00408350271 * tdb * v**2
    b3 += -5.21670675e-5 * tdb**2 * v**2
    b3 += 1.94544667e-6 * tdb**3 * v**2
    b3 += 1.14099531e-8 * tdb**4 * v**2
    b3 += -6.57263143e-5 * tdb * v**3
    b3 += 2.22697524e-7 * tdb**2 * v**3
    b3 += -4.16117031e-8 * tdb**3 * v**3
    b3 += 9.66891875e-6 * tdb * v**4
    b3 += 2.52785852e-9 * tdb**2 * v**4
    b3 += -1.74202546e-7 * tdb * v**5
    print(f"  Block 3 (Ta*v): {b3}")
    offset += b3
    
    # Block 4: Pa only
    b4 = 0.0
    b4 += 5.12733497 * pa
    b4 += -2.80626406 * pa**2
    b4 += -0.0353874123 * pa**3
    b4 += 0.614155345 * pa**4
    b4 += 0.0882773108 * pa**5
    b4 += 0.00148348065 * pa**6
    print(f"  Block 4 (Pa): {b4}")
    offset += b4
    
    # Block 5: Ta * Pa
    b5 = 0.0
    b5 += -0.312788561 * tdb * pa
    b5 += -0.0196701861 * tdb**2 * pa
    b5 += 9.99690870e-4 * tdb**3 * pa
    b5 += 9.51738512e-6 * tdb**4 * pa
    b5 += -4.66426341e-7 * tdb**5 * pa
    print(f"  Block 5 (Ta*Pa): {b5}")
    offset += b5
    
    # Block 6: v * Pa
    b6 = 0.0
    b6 += 0.548050612 * v * pa
    b6 += -0.00330552823 * tdb * v * pa
    b6 += -0.00164119440 * tdb**2 * v * pa
    b6 += -5.16670694e-6 * tdb**3 * v * pa
    b6 += 9.52692432e-7 * tdb**4 * v * pa
    b6 += -0.0429223622 * v**2 * pa
    b6 += 0.00500845667 * tdb * v**2 * pa
    b6 += 1.00601257e-6 * tdb**2 * v**2 * pa
    b6 += -1.81748644e-6 * tdb**3 * v**2 * pa
    b6 += -1.25813502e-3 * v**3 * pa
    b6 += -1.79330391e-4 * tdb * v**3 * pa
    b6 += 2.34994441e-6 * tdb**2 * v**3 * pa
    b6 += 1.29735808e-4 * v**4 * pa
    b6 += 1.29064870e-6 * tdb * v**4 * pa
    b6 += -2.28558686e-6 * v**5 * pa
    print(f"  Block 6 (v*Pa): {b6}")
    offset += b6
    
    # Block 7: Pa^2...
    b7 = 0.0
    b7 += 0.548712484 * tdb * pa**2
    b7 += -0.00399428410 * tdb**2 * pa**2
    b7 += -9.54009191e-4 * tdb**3 * pa**2
    b7 += 1.93090978e-5 * tdb**4 * pa**2
    b7 += -0.308806365 * v * pa**2
    b7 += 0.0116952364 * tdb * v * pa**2
    b7 += 4.95271903e-4 * tdb**2 * v * pa**2
    b7 += -1.90710882e-5 * tdb**3 * v * pa**2
    b7 += 0.00210787756 * v**2 * pa**2
    b7 += -6.98445738e-4 * tdb * v**2 * pa**2
    b7 += 2.30109073e-5 * tdb**2 * v**2 * pa**2
    b7 += 4.17856590e-4 * v**3 * pa**2
    b7 += -1.27043871e-5 * tdb * v**3 * pa**2
    b7 += -3.04620472e-6 * v**4 * pa**2
    print(f"  Block 7 (Pa^2...): {b7}")
    offset += b7
    
    # Block 8: Pa^3...
    b8 = 0.0
    b8 += -0.221201190 * tdb * pa**3
    b8 += 0.0155126038 * tdb**2 * pa**3
    b8 += -2.63917279e-4 * tdb**3 * pa**3
    b8 += 0.0453433455 * v * pa**3
    b8 += -0.00432943862 * tdb * v * pa**3
    b8 += 1.45389826e-4 * tdb**2 * v * pa**3
    b8 += 2.17508610e-4 * v**2 * pa**3
    b8 += -6.66724702e-5 * tdb * v**2 * pa**3
    b8 += 3.33217140e-5 * v**3 * pa**3
    print(f"  Block 8 (Pa^3...): {b8}")
    offset += b8
    
    # Block 9: Pa^4, Pa^5
    b9 = 0.0
    b9 += -0.0616755931 * tdb * pa**4
    b9 += 0.00133374846 * tdb**2 * pa**4
    b9 += 0.00355375387 * v * pa**4
    b9 += -5.13027851e-4 * tdb * v * pa**4
    b9 += 1.02449757e-4 * v**2 * pa**4
    b9 += -0.00301859306 * tdb * pa**5
    b9 += 0.00104452989 * v * pa**5
    print(f"  Block 9 (Pa^4, Pa^5): {b9}")
    offset += b9
    
    print(f"  Total Offset: {offset}")
    print(f"  Calculated UTCI: {tdb + offset}")

# Test with user values
# 0.92 m/s = 3.312 km/h
debug_utci(9.0, 70.0, 3.312)
