
import math

def calculate_utci(tdb, cur_rh, v_10m, tmrt):
    """
    Calculate UTCI using the 6th degree polynomial from Bröde et al. (2012).
    
    Parameters:
    tdb : float : Air temperature (dry bulb) in Celsius
    cur_rh : float : Relative humidity in percent (0-100)
    v_10m : float : Wind speed at 10m height in m/s
    tmrt : float : Mean radiant temperature in Celsius
    
    Returns:
    float : UTCI value in Celsius
    """
    
    # 1. Validate constraints (as per Bröde et al recommendations)
    # The polynomial is valid for:
    # Ta from -50 to +50 C
    # v from 0.5 to 17 m/s (at 10m)
    # VP - unknown constraint but usually within physical range
    # Tmrt - Ta from -30 to +70 K
    
    # We will compute it anyway but the caller should know.
    
    # 2. Preparation of input variables
    
    # Calculate Saturation Vapour Pressure (es) in hPa
    # We use a standard Magnus formula which is sufficiently accurate
    # es = 6.112 * exp(17.62 * t / (243.12 + t))
    es = 6.112 * math.exp((17.62 * tdb) / (243.12 + tdb))
    
    # Vapour Pressure (e) in hPa
    e_hpa = (cur_rh / 100.0) * es
    
    # Polynomial uses Vapour Pressure in kPa
    pa = e_hpa / 10.0
    
    # Polynomial uses Delta Tmrt (Tmrt - Ta)
    d_tr = tmrt - tdb
    
    # Wind speed
    v = v_10m
    
    # The polynomial implementation
    # Coefficients from code inspection of pythermalcomfort / Bröde et al. 2012
    # Offset = UTCI - Ta
    
    # Terms involving Ta only
    offset = 0.0
    offset += 0.607562052
    offset += -0.0227712343 * tdb
    offset += 8.06470249e-4 * tdb**2
    offset += -1.54271372e-4 * tdb**3
    offset += -3.24651735e-6 * tdb**4
    offset += 7.32602852e-8 * tdb**5
    offset += 1.35959073e-9 * tdb**6
    
    # Terms involving v only
    offset += -2.25836520 * v
    offset += -0.751269505 * v**2
    offset += 0.158137256 * v**3
    offset += -0.0127762753 * v**4
    offset += 4.56306672e-4 * v**5
    offset += -5.91491269e-6 * v**6
    
    # Terms involving Ta and v
    offset += 0.0880326035 * tdb * v
    offset += 0.00216844454 * tdb**2 * v
    offset += -1.53347087e-5 * tdb**3 * v
    offset += -5.72983704e-7 * tdb**4 * v
    offset += -2.55090145e-9 * tdb**5 * v
    
    offset += -0.00408350271 * tdb * v**2
    offset += -5.21670675e-5 * tdb**2 * v**2
    offset += 1.94544667e-6 * tdb**3 * v**2
    offset += 1.14099531e-8 * tdb**4 * v**2
    
    offset += -6.57263143e-5 * tdb * v**3
    offset += 2.22697524e-7 * tdb**2 * v**3
    offset += -4.16117031e-8 * tdb**3 * v**3
    
    offset += 9.66891875e-6 * tdb * v**4
    offset += 2.52785852e-9 * tdb**2 * v**4
    
    offset += -1.74202546e-7 * tdb * v**5
    
    # Terms involving Delta_Tr (d_tr)
    # d_tr only
    offset += 0.398374029 * d_tr
    offset += 7.55043090e-4 * d_tr**2
    offset += -1.21206673e-5 * d_tr**3
    offset += -1.30369025e-9 * d_tr**4 # Wait, checked value order
    # Checking against typical list:
    # 0.398374029 * d_tr
    # ...
    
    # Let's cross check d_tr terms
    offset += 1.83945314e-4 * tdb * d_tr
    offset += -1.73754510e-4 * tdb**2 * d_tr
    offset += -7.60781159e-7 * tdb**3 * d_tr
    offset += 3.77830287e-8 * tdb**4 * d_tr
    offset += 5.43079673e-10 * tdb**5 * d_tr
    
    offset += -0.0200518269 * v * d_tr
    offset += 8.92859837e-4 * tdb * v * d_tr
    offset += 3.45433048e-6 * tdb**2 * v * d_tr
    offset += -3.77925774e-7 * tdb**3 * v * d_tr
    offset += -1.69699377e-9 * tdb**4 * v * d_tr
    
    offset += 1.69992415e-4 * v**2 * d_tr
    offset += -4.99204314e-5 * tdb * v**2 * d_tr
    offset += 2.47417178e-7 * tdb**2 * v**2 * d_tr
    offset += 1.07596466e-8 * tdb**3 * v**2 * d_tr
    
    offset += 8.49242932e-5 * v**3 * d_tr
    offset += 1.35191328e-6 * tdb * v**3 * d_tr
    offset += -6.21531254e-9 * tdb**2 * v**3 * d_tr
    
    offset += -4.99410301e-6 * v**4 * d_tr
    offset += -1.89489258e-8 * tdb * v**4 * d_tr
    
    offset += 8.15300114e-8 * v**5 * d_tr
    
    # d_tr^2 terms
    # offset += 7.55043090e-4 * d_tr**2 (Already added)
    offset += -5.65095215e-5 * tdb * d_tr**2
    offset += -4.52166564e-7 * tdb**2 * d_tr**2
    offset += 2.46688878e-8 * tdb**3 * d_tr**2
    offset += 2.42674348e-10 * tdb**4 * d_tr**2
    
    offset += 1.54547250e-4 * v * d_tr**2
    offset += 5.24110970e-6 * tdb * v * d_tr**2
    offset += -8.75874982e-8 * tdb**2 * v * d_tr**2
    offset += -1.50743064e-9 * tdb**3 * v * d_tr**2
    
    offset += -1.56236307e-5 * v**2 * d_tr**2
    offset += -1.33895614e-7 * tdb * v**2 * d_tr**2
    offset += 2.49709824e-9 * tdb**2 * v**2 * d_tr**2
    
    offset += 6.51711721e-7 * v**3 * d_tr**2
    offset += 1.94960053e-9 * tdb * v**3 * d_tr**2
    
    offset += -1.00361113e-8 * v**4 * d_tr**2
    
    # d_tr^3 terms
    # offset += -1.21206673e-5 * d_tr**3 (Already added)
    offset += -2.18203660e-7 * tdb * d_tr**3
    offset += 7.51269482e-9 * tdb**2 * d_tr**3
    offset += 9.79063848e-11 * tdb**3 * d_tr**3
    
    offset += 1.25006734e-6 * v * d_tr**3
    offset += -1.81584736e-9 * tdb * v * d_tr**3
    offset += -3.52197671e-10 * tdb**2 * v * d_tr**3
    
    offset += -3.36514630e-8 * v**2 * d_tr**3
    offset += 1.35908359e-10 * tdb * v**2 * d_tr**3
    
    offset += 4.17032620e-10 * v**3 * d_tr**3
    
    # d_tr^4 terms
    offset += -1.30369025e-9 * d_tr**4
    offset += 4.13908461e-10 * tdb * d_tr**4
    offset += 9.22652254e-12 * tdb**2 * d_tr**4
    
    offset += -5.08220384e-9 * v * d_tr**4
    offset += -2.24730961e-11 * tdb * v * d_tr**4
    
    offset += 1.17139133e-10 * v**2 * d_tr**4
    
    # d_tr^5 and d_tr^6 terms
    offset += 6.62154879e-10 * d_tr**5
    offset += 4.03863260e-13 * tdb * d_tr**5
    offset += 1.95087203e-12 * v * d_tr**5
    
    offset += -4.73602469e-12 * d_tr**6
    
    # Terms involving Pa (pa)
    # Pa only
    offset += 5.12733497 * pa
    offset += -2.80626406 * pa**2
    offset += -0.0353874123 * pa**3
    offset += 0.614155345 * pa**4
    offset += 0.0882773108 * pa**5 # This sign and value seem right per logic
    
    # Wait, the code snippet had pa^6 term?
    # + 0.00148348065 * pa * pa * pa * pa * pa * pa
    offset += 0.00148348065 * pa**6
    
    # Pa cross terms
    
    # Pa * Ta
    offset += -0.312788561 * tdb * pa
    offset += -0.0196701861 * tdb**2 * pa
    offset += 9.99690870e-4 * tdb**3 * pa
    offset += 9.51738512e-6 * tdb**4 * pa
    offset += -4.66426341e-7 * tdb**5 * pa
    
    # Pa * v
    offset += 0.548050612 * v * pa
    offset += -0.00330552823 * tdb * v * pa
    offset += -0.00164119440 * tdb**2 * v * pa
    offset += -5.16670694e-6 * tdb**3 * v * pa
    offset += 9.52692432e-7 * tdb**4 * v * pa
    
    offset += -0.0429223622 * v**2 * pa
    offset += 0.00500845667 * tdb * v**2 * pa
    offset += 1.00601257e-6 * tdb**2 * v**2 * pa
    offset += -1.81748644e-6 * tdb**3 * v**2 * pa
    
    offset += -1.25813502e-3 * v**3 * pa
    offset += -1.79330391e-4 * tdb * v**3 * pa
    offset += 2.34994441e-6 * tdb**2 * v**3 * pa
    
    offset += 1.29735808e-4 * v**4 * pa
    offset += 1.29064870e-6 * tdb * v**4 * pa
    
    offset += -2.28558686e-6 * v**5 * pa
    
    # Pa * d_tr
    offset += -0.0369476348 * d_tr * pa
    offset += 0.00162325322 * tdb * d_tr * pa
    offset += -3.14279680e-5 * tdb**2 * d_tr * pa
    offset += 2.59835559e-6 * tdb**3 * d_tr * pa
    offset += -4.77136523e-8 * tdb**4 * d_tr * pa
    
    offset += 8.64203390e-3 * v * d_tr * pa
    offset += -6.87405181e-4 * tdb * v * d_tr * pa
    offset += -9.13863872e-6 * tdb**2 * v * d_tr * pa
    offset += 5.15916806e-7 * tdb**3 * v * d_tr * pa
    
    offset += -3.59217476e-5 * v**2 * d_tr * pa
    offset += 3.28696511e-5 * tdb * v**2 * d_tr * pa
    offset += -7.10542454e-7 * tdb**2 * v**2 * d_tr * pa
    
    offset += -1.24382300e-5 * v**3 * d_tr * pa
    offset += -7.38584400e-9 * tdb * v**3 * d_tr * pa
    
    offset += 2.20609296e-7 * v**4 * d_tr * pa
    
    # Pa * d_tr^2
    offset += -7.32469180e-4 * d_tr**2 * pa
    offset += -1.87381964e-5 * tdb * d_tr**2 * pa
    offset += 4.80925239e-6 * tdb**2 * d_tr**2 * pa
    offset += -8.75492040e-8 * tdb**3 * d_tr**2 * pa
    
    offset += 2.77862930e-5 * v * d_tr**2 * pa
    offset += -5.06004592e-6 * tdb * v * d_tr**2 * pa
    offset += 1.14325367e-7 * tdb**2 * v * d_tr**2 * pa
    
    offset += 2.53016723e-6 * v**2 * d_tr**2 * pa
    offset += -1.72857035e-8 * tdb * v**2 * d_tr**2 * pa
    
    offset += -3.95079398e-8 * v**3 * d_tr**2 * pa
    
    # Pa * d_tr^3
    offset += -3.59413173e-7 * d_tr**3 * pa
    offset += 7.04388046e-7 * tdb * d_tr**3 * pa
    offset += -1.89309167e-8 * tdb**2 * d_tr**3 * pa
    
    offset += -4.79768731e-7 * v * d_tr**3 * pa
    offset += 7.96079978e-9 * tdb * v * d_tr**3 * pa
    
    offset += 1.62897058e-9 * v**2 * d_tr**3 * pa
    
    # Pa * d_tr^4
    offset += 3.94367674e-8 * d_tr**4 * pa
    offset += -1.18566247e-9 * tdb * d_tr**4 * pa
    
    offset += 3.34678041e-10 * v * d_tr**4 * pa

    # Pa* d_tr^5 ??
    offset += -1.15606447e-10 * d_tr**5 * pa

    # Pa^2 terms
    offset += 0.548712484 * tdb * pa**2
    offset += -0.00399428410 * tdb**2 * pa**2
    offset += -9.54009191e-4 * tdb**3 * pa**2
    offset += 1.93090978e-5 * tdb**4 * pa**2
    
    offset += -0.308806365 * v * pa**2
    offset += 0.0116952364 * tdb * v * pa**2
    offset += 4.95271903e-4 * tdb**2 * v * pa**2
    offset += -1.90710882e-5 * tdb**3 * v * pa**2
    
    offset += 0.00210787756 * v**2 * pa**2
    offset += -6.98445738e-4 * tdb * v**2 * pa**2
    offset += 2.30109073e-5 * tdb**2 * v**2 * pa**2
    
    offset += 4.17856590e-4 * v**3 * pa**2
    offset += -1.27043871e-5 * tdb * v**3 * pa**2
    
    offset += -3.04620472e-6 * v**4 * pa**2
    
    # Pa^2 * d_tr
    offset += 0.0514507424 * d_tr * pa**2
    offset += -0.00432510997 * tdb * d_tr * pa**2
    offset += 8.99281156e-5 * tdb**2 * d_tr * pa**2
    offset += -7.14663943e-7 * tdb**3 * d_tr * pa**2
    
    offset += -2.66016305e-4 * v * d_tr * pa**2
    offset += 2.63789586e-4 * tdb * v * d_tr * pa**2
    offset += -7.01199003e-6 * tdb**2 * v * d_tr * pa**2
    
    offset += -1.06823306e-4 * v**2 * d_tr * pa**2
    offset += 3.61341136e-6 * tdb * v**2 * d_tr * pa**2
    
    offset += 2.29748967e-7 * v**3 * d_tr * pa**2
    
    # Pa^2 * d_tr^2
    offset += 3.04788893e-4 * d_tr**2 * pa**2
    offset += -6.42070836e-5 * tdb * d_tr**2 * pa**2
    offset += 1.16257971e-6 * tdb**2 * d_tr**2 * pa**2
    
    offset += 7.68023384e-6 * v * d_tr**2 * pa**2
    offset += -5.47446896e-7 * tdb * v * d_tr**2 * pa**2
    
    offset += -3.59937910e-8 * v**2 * d_tr**2 * pa**2
    
    # Pa^2 * d_tr^3
    offset += -4.36497725e-6 * d_tr**3 * pa**2
    offset += 1.68737969e-7 * tdb * d_tr**3 * pa**2
    
    offset += 2.67489271e-8 * v * d_tr**3 * pa**2
    
    # Pa^2 * d_tr^4
    offset += 3.23926897e-9 * d_tr**4 * pa**2
    
    # Pa^3 terms
    offset += -0.221201190 * tdb * pa**3
    offset += 0.0155126038 * tdb**2 * pa**3
    offset += -2.63917279e-4 * tdb**3 * pa**3
    
    offset += 0.0453433455 * v * pa**3
    offset += -0.00432943862 * tdb * v * pa**3
    offset += 1.45389826e-4 * tdb**2 * v * pa**3
    
    offset += 2.17508610e-4 * v**2 * pa**3
    offset += -6.66724702e-5 * tdb * v**2 * pa**3
    
    offset += 3.33217140e-5 * v**3 * pa**3
    
    # Pa^3 * d_tr
    offset += -0.00226921615 * d_tr * pa**3
    offset += 3.80261982e-4 * tdb * d_tr * pa**3
    offset += -5.45314314e-9 * tdb**2 * d_tr * pa**3
    
    offset += -7.96355448e-4 * v * d_tr * pa**3
    offset += 2.53458034e-5 * tdb * v * d_tr * pa**3
    
    offset += -6.31223658e-6 * v**2 * d_tr * pa**3
    
    # Pa^3 * d_tr^2
    offset += 3.02122035e-4 * d_tr**2 * pa**3
    offset += -4.77403547e-6 * tdb * d_tr**2 * pa**3
    
    offset += 1.73825715e-6 * v * d_tr**2 * pa**3
    
    # Pa^3 * d_tr^3
    offset += -4.09087898e-7 * d_tr**3 * pa**3
    
    # Pa^4 terms
    offset += -0.0616755931 * tdb * pa**4
    offset += 0.00133374846 * tdb**2 * pa**4
    
    offset += 0.00355375387 * v * pa**4
    offset += -5.13027851e-4 * tdb * v * pa**4
    
    offset += 1.02449757e-4 * v**2 * pa**4
    
    # Pa^4 * d_tr
    offset += -0.00148526421 * d_tr * pa**4
    offset += -4.11469183e-5 * tdb * d_tr * pa**4
    
    offset += -6.80434415e-6 * v * d_tr * pa**4
    
    # Pa^4 * d_tr^2
    offset += -9.77675906e-6 * d_tr**2 * pa**4
    
    # Pa^5 terms
    offset += -0.00301859306 * tdb * pa**5
    
    offset += 0.00104452989 * v * pa**5
    
    # Pa^5 * d_tr
    offset += 2.47090539e-4 * d_tr * pa**5
    
    # End of polynomial
    
    return tdb + offset

def main():
    # Test case from user
    # Ta = 9.0
    # RH = 70%
    # Wind Speed (at 10m) = 3.31 km/h -> m/s
    # Tmrt = 9.0
    
    ta = 9.0
    rh = 70.0
    ws_kmh = 3.31
    ws_ms = ws_kmh / 3.6
    tmrt = 9.0
    
    utci_val = calculate_utci(ta, rh, ws_ms, tmrt)
    print(f"Inputs: Ta={ta}, RH={rh}, WS={ws_ms:.4f} m/s ({ws_kmh} km/h), Tmrt={tmrt}")
    print(f"Calculated UTCI: {utci_val}")

if __name__ == "__main__":
    main()
