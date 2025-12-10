# v1.1.2 - Correcció de Reconfiguració i Millores Visuals

## 🐛 Correccions
- **Reconfiguració de Sensors Locals**: Solucionat un error que impedia canviar els sensors seleccionats (temperatura, pluja, etc.) quan es reconfigurava una integració en "Mode Local". Ara apareix correctament la pantalla de selecció.

## 💅 Millores Visuals
- **Icona de Nit**: Millora en la icona mostrada quan l'estat és "Parcialment ennuvolat" durant la nit. Ara es mostrarà una lluna amb un núvol (`mdi:weather-night-partly-cloudy`) en lloc de la icona per defecte, millorant la coherència visual a les llistes d'entitats.

# v1.0.8 - Millora de la Cobertura de Tests i Nous Sensors

## ✨ Novetats
- **Nous Sensors de Diagnòstic**: S'han afegit sensors per monitoritzar l'estat de les actualitzacions de la previsió:
  - `next_forecast_update`: Indica quan es realitzarà la propera actualització de la previsió.
  - `last_forecast_update`: Indica quan es va realitzar l'última actualització exitosa.

## 🛠️ Millores Tècniques
- **Cobertura de Tests**: S'ha augmentat significativament la cobertura de tests (del 82% al 90%), afegint proves per a:
  - Coordinador de previsions (`ForecastCoordinator`).
  - Gestió d'errors de l'API.
  - Plataforma de botons.
  - Atributs dels sensors.
- **Documentació**: Actualització de les claus de traducció per als nous sensors.

> Aquesta versió millora la robustesa del codi i proporciona més visibilitat sobre el funcionament intern de la integració.
