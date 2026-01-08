# Variables de Mesura XEMA (Meteocat)

Aquest document llista les variables de l'API XEMA (Xarxa d'Estacions Meteorològiques Automàtiques) que són utilitzades actualment per la integració **Meteocat Community Edition**.

## Variables Utilitzades

| Codi | Nom | Unitat | Acrònim | Tipus | Decimals | Observacions |
|---|---|---|---|---|---|---|
| **30** | Velocitat del vent a 10 m (esc.) | m/s | VV10 | DAT | 1 | |
| **31** | Direcció de vent 10 m (m. 1) | ° | DV10 | DAT | 0 | |
| **32** | Temperatura | °C | T | DAT | 1 | |
| **33** | Humitat relativa | % | HR | DAT | 0 | |
| **34** | Pressió atmosfèrica | hPa | P | DAT | 1 | |
| **35** | Precipitació | mm | PPT | DAT | 1 | Acumulada diària (calculada) |
| **36** | Irradiància solar global | W/m² | RS | DAT | 0 | |

## Detalls Tècnics API

Dades brutes proporcionades per l'API de Meteocat (només variables utilitzades):

```json
[
  {
    "codi": 30,
    "nom": "Velocitat del vent a 10 m (esc.)",
    "unitat": "m/s",
    "acronim": "VV10",
    "tipus": "DAT",
    "decimals": 1
  },
  {
    "codi": 31,
    "nom": "Direcció de vent 10 m (m. 1) ",
    "unitat": "°",
    "acronim": "DV10",
    "tipus": "DAT",
    "decimals": 0
  },
  {
    "codi": 32,
    "nom": "Temperatura",
    "unitat": "°C",
    "acronim": "T",
    "tipus": "DAT",
    "decimals": 1
  },
  {
    "codi": 33,
    "nom": "Humitat relativa",
    "unitat": "%",
    "acronim": "HR",
    "tipus": "DAT",
    "decimals": 0
  },
  {
    "codi": 34,
    "nom": "Pressió atmosfèrica",
    "unitat": "hPa",
    "acronim": "P",
    "tipus": "DAT",
    "decimals": 1
  },
  {
    "codi": 35,
    "nom": "Precipitació",
    "unitat": "mm",
    "acronim": "PPT",
    "tipus": "DAT",
    "decimals": 1
  },
  {
    "codi": 36,
    "nom": "Irradiància solar global",
    "unitat": "W/m²",
    "acronim": "RS",
    "tipus": "DAT",
    "decimals": 0
  }
]
```
