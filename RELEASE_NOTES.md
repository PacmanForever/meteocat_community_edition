# v1.1.4 - Correccions en Mode Local

## 🐛 Correccions
- **Actualització en Temps Real**: Solucionat un problema on l'entitat de temps no s'actualitzava immediatament quan canviaven els sensors locals (temperatura, vent, etc.), provocant que mostrés `NaN` si els sensors no estaven llestos a l'inici. Ara l'entitat escolta els canvis dels sensors i s'actualitza a l'instant.
- **Persistència URL API**: Solucionat un error on l'URL de l'API es restablia al valor per defecte en reconfigurar una integració en "Mode Local". Ara es conserva l'URL personalitzada correctament.

# v1.1.3 - Millora en l'Atribució i Correccions

## 🐛 Correccions
- **Valors NaN en Sensors Locals**: Solucionat un error crític on els valors de temperatura, pressió i vent apareixien com a `NaN` o `Desconegut` degut a un format incorrecte en la configuració dels sensors. Aquesta versió corregeix automàticament les configuracions afectades.

## 💅 Millores Visuals
- **Atribució de l'Entitat Weather**: S'ha millorat el text d'atribució (el que apareix al peu de la targeta de temps o als detalls):
  - **Mode Estació**: Ara mostra "Estació {Nom} + predicció Meteocat".
  - **Mode Local**: Ara mostra "Estació local + Predicció Meteocat".

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
