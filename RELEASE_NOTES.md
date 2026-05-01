# v1.2.90 - Correcció de la Condició Climàtica Externa i Neteja Interna

## 🐛 Correccions
- **Condició climàtica externa**: L'entitat `weather` en mode Estació Externa ara prioritza correctament la predicció horària per calcular la condició actual.
- **Fallback controlat**: La predicció diària només s'utilitza com a fallback si està activada a la configuració de l'estació.
- **Estalvi de quota**: Si la predicció diària està desactivada per reduir consum, ja no es consulta com a font de condició climàtica.
- **Seguretat de logs**: Eliminada l'exposició de dades sensibles i fragments de la clau API als logs del coordinator.
- **Reautenticació**: Eliminat codi mort al flux de reautenticació.
- **Coordinator**: Corregit l'accés a `entry.options` per evitar mutacions directes innecessàries del `ConfigEntry`.
- **Traduccions**: Corregides cadenes en castellà amb cometes sobreres.

## ⚡ Canvis
- **Documentació**: Actualitzada la descripció del comportament de la condició climàtica al README i als docstrings per reflectir el funcionament real en mode extern i local.

## ✅ Validació
- Afegits tests de regressió per a la prioritat entre predicció horària i diària.
- Validació completa del projecte: `545 passed`.

# v1.2.86 - Correcció Inicialització Sensors UTCI/Beaufort

## 🐛 Correccions
- **Inicialització**: Solucionat un problema on els sensors UTCI i Beaufort apareixien com a "Desconeguts" en reiniciar Home Assistant fins a la següent actualització programada (en mode Estació XEMA). Ara s'inicialitzen immediatament si ja hi ha dades disponibles.
- **Mode Local**: Millorada la robustesa del sensor Beaufort en mode local quan només es configura el sensor de vent (sense temperatura/humitat).

# v1.2.85 - Correcció Càlcul Beaufort

## 🐛 Correccions
- **Càlcul Beaufort**: S'ha ajustat la fórmula de càlcul de l'escala Beaufort per coincidir exactament amb els rangs de velocitat (km/h) oficials de Meteocat. Això soluciona casos on velocitats com 6.44 km/h es classificaven incorrectament com a 1 (Ventolina) en lloc de 2 (Vent fluixet).

# v1.2.84 - Neteja Literals Beaufort

## ⚡ Canvis
- **Simplificació**: Eliminats els textos explicatius entre parèntesis de les descripcions Beaufort per fer-les més netes i directes (ex: "Vent fluixet" en comptes de "Vent fluixet (brisa molt feble)").

# v1.2.83 - Correccions i Traduccions Beaufort Oficials

## ⚡ Canvis
- **Traduccions Beaufort (Català)**: Actualitzades les descripcions de l'escala Beaufort per coincidir exactament amb la terminologia oficial del Pla Alfa (Generalitat de Catalunya).
- **Documentació**: Taula Beaufort actualitzada al README amb els nous noms.

# v1.2.82 - Millora UTCI i Nous Sensors de Vent (Beaufort)

## 🆕 Novetats
- **Escala Beaufort**: S'han afegit dos nous sensors per estació/municipi: `beaufort_index` (numèric 0-17) i `beaufort_description` (textual). Aquests sensors es generen automàticament si hi ha dades de vent disponibles (ja sigui via sensor local o via API).
- **Traduccions Beaufort**: Descripcions completes de l'escala de vent en Català, Castellà i Anglès.

## ⚡ Canvis
- **UTCI**: Actualitzat el nom i la descripció dels sensors UTCI per alinear-se amb la terminologia científica (Temperatura UTCI vs Índex UTCI).
- **Documentació**: Actualitzat el README amb taules detallades per UTCI i Beaufort.

# v1.2.67 - Refactorització Config Flow V2 i correccions diverses

## 🆕 Canvis
- **Configuració**: Actualització al sistema Config Flow V2 per millorar l'experiència d'usuari i la validació de dades.
- **Validació**: Validació més estricta en formularis i opcions.
- **Tests**: Reestructuració completa de la suite de tests (>97% cobertura).

## �� Correccions
- **Errors sintaxi**: Correcció error JSON crític en manifest.json.
- **Traduccions**: Textos actualitzats per coincidir amb els nous camps.
- **Opcions**: Solucionats errors en el canvi de tipus de mapeig de condicions.

# v1.2.55 - Millores en lògica de servei i gestió de quota

## 🆕 Canvis
- **Tipus d'Integració**: S'ha canviat la definició de la integració de "Hub" a "Service" per reflectir millor la seva naturalesa al núvol.
- **Interfície**: Nous textos d'avís en la configuració del mapeig personalitzat per evitar errors en modificar literals.

## 🐞 Correccions
- **Gestió de Quota**: Solucionat un problema on el comptador de quota no s'actualitzava correctament en certes condicions.
- **Tests**: Correccions en els tests unitaris per adaptar-se als nous textos.

# v1.2.46 - Millores en la visibilitat de les entitats de configuració

## 🐞 Correccions
- **Millora de visibilitat**: Les entitats de Latitud, Longitud i Altitud s'han mogut al grup principal de sensors per evitar que apareguin deshabilitades per defecte en algunes configuracions.
- **Estabilitat del registre**: S'han eliminat les restriccions de categoria `CONFIG` i els mètodes de forçat d'habilitació que podien entrar en conflicte amb Home Assistant, assegurant que les entitats estiguin sempre disponibles i actives.

# v1.1.10 - Millores en gestió d'API i camps requerits

## 🆕 Novetats
- Ara la URL de proves de l'API s'utilitza sempre si està configurada, evitant consum de quota a la real.
- S'ha afegit debug logging per traçar totes les crides a l'API i la URL utilitzada.

## 🐞 Correccions
- Camps requerits (condició, temperatura, humitat) marcats visualment a la UI.
- Correcció de l'icona del botó "refresh measurements".
- Traduccions revisades i errors de JSON corregits.
- Ordre correcte dels passos del config flow en mode local (mapping després de sensors).
- Cobertura de tests ampliada (302/302 passats).

# v1.1.9 - Pantalla de mapping i camps requerits

## 🆕 Novetats
- S'ha afegit la pantalla de mapping al config flow en mode local, permetent personalitzar la correspondència de condicions meteorològiques.
- Els camps requerits (condició, temperatura, humitat) ara es marquen visualment a la UI.
- S'ha afegit un test que verifica que la pantalla de mapping es mostra i que la lògica backend la crida.

## 🐞 Correccions
- S'ha corregit l'ordre dels passos del config flow en mode local (mapping després de sensors).
- Traduccions revisades i errors de JSON corregits.
- Versió sincronitzada entre manifest i git tag.
- Cobertura de tests ampliada (302/302 passats).

# v1.1.5 - Conversió de la velocitat del vent

## 🐛 Correccions
- **Unitat de velocitat del vent**: Ara la velocitat del vent en l'entitat Weather es mostra en km/h (abans en m/s). El valor es converteix automàticament des de l'API (m/s → km/h) per evitar discrepàncies amb targetes i estacions Meteocat.

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
