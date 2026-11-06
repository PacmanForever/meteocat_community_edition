# Exemples d'ús - Meteocat (Community Edition)

Aquest directori conté exemples pràctics per utilitzar la integració Meteocat amb Home Assistant.

## 📁 Fitxers disponibles

### `automations.yaml`
Exemples complets d'automatitzacions organitzats en 7 categories:

1. **Notificacions basades en esdeveniments** - Rebre avisos quan s'actualitzen les dades
2. **Alertes meteorològiques** - Avisos de temperatura, pluja
3. **Automatitzacions intel·ligents** - Tancar persianes, activar reg, escalfar casa
4. **Gestió de quotes API** - Monitoritzar i alertar sobre l'ús de l'API
5. **Actualitzacions manuals** - Actualitzacions intel·ligents segons context
6. **Timestamps** - Automatitzacions basades en temps d'actualització
7. **Integracions** - MQTT, InfluxDB, Node-RED

### `lovelace.yaml`
Targetes per al dashboard de Home Assistant organitzades en 10 seccions:

1. **Targeta Weather** - Mode Estació (entitat weather estàndard)
2. **Targetes personalitzades** - Mode Municipal (prediccions en markdown)
3. **Quotes API** - Visualització de consums
4. **Timestamps** - Informació d'actualitzacions
5. **Dashboard complet Mode Estació** - Vista completa amb weather + quotes
6. **Dashboard complet Mode Municipal** - Vista completa amb prediccions
7. **Custom Cards avançades** - Mini Graph Card, Apexcharts, Mushroom Cards
8. **Mapa** - Ubicació de l'estació
9. **Targetes condicionals** - Avisos de temperatura/pluja
10. **Tendències** - Comparativa entre dies

## 🚀 Com utilitzar els exemples

### Automatitzacions

1. Obre el fitxer `automations.yaml`
2. Copia les automatitzacions que necessitis
3. Enganxa-les al fitxer `automations.yaml` de Home Assistant o via UI
4. **IMPORTANT**: Canvia els noms d'entitats per adaptar-los a la teva configuració

Exemple:
```yaml
# Canvia això:
entity_id: sensor.granollers_prediccio_diaria

# Pel teu sensor:
entity_id: sensor.barcelona_prediccio_diaria
```

### Targetes Lovelace

1. Obre el fitxer `lovelace.yaml`
2. Edita el teu dashboard en mode YAML (Edita Dashboard → 3 punts → Raw configuration editor)
3. Copia la targeta que necessitis
4. Enganxa-la a la vista del teu dashboard
5. **IMPORTANT**: Adapta els `entity_id` a les teves entitats

Exemple:
```yaml
# Canvia això:
entity: weather.granollers_ym

# Pel teu entity:
entity: weather.sabadell_x4
```

## 💡 Consells

### Entity IDs de Mode Estació
- Weather: `weather.{estacio}_{codi}`
- Sensors: `sensor.{estacio}_{codi}_*`
- Botó: `button.{estacio}_{codi}_refresh`

Exemple: `weather.granollers_ym`, `sensor.granollers_ym_quota_prediccio`

### Entity IDs de Mode Municipal
- Predicció horària: `sensor.{municipi}_prediccio_horaria`
- Predicció diària: `sensor.{municipi}_prediccio_diaria`
- Sensors: `sensor.{municipi}_*`
- Botó: `button.{municipi}_refresh`

Exemple: `sensor.granollers_prediccio_diaria`, `button.granollers_refresh`

### Targetes personalitzades recomanades

Alguns exemples utilitzen targetes personalitzades. A Home Assistant 2026.11 o posterior, ves a **Configuració** > **Mercat** i cerca cada targeta. Si no hi és, afegeix-ne el repositori des de **Afegeix des d'un enllaç**:

- **Mini Graph Card** - Gràfics compactes
- **Apexcharts Card** - Gràfics avançats
- **Mushroom Cards** - Disseny modern
- **Button Card** - Targetes personalitzades avançades
- **Card Mod** - Estils CSS personalitzats

En Home Assistant 2026.10 o anterior, instal·la-les des de HACS > Frontend.

## 🔍 Trobar els teus Entity IDs

Per trobar els Entity IDs de les teves entitats:

1. Ves a **Configuració** → **Dispositius i Serveis**
2. Cerca **Meteocat (Community Edition)**
3. Fes clic a l'entrada (estació o municipi)
4. Veuràs totes les entitats creades amb els seus Entity IDs

O bé:

1. Ves a **Developer Tools** → **States**
2. Cerca "meteocat" o el nom de la teva estació/municipi
3. Copia l'Entity ID que necessitis

## 📖 Documentació addicional

Per més informació sobre com utilitzar les dades de predicció en templates i automatitzacions, consulta els README principals:

- [README (Català)](../README.md)
- [README (English)](../README.en.md)
- [README (Español)](../README.es.md)

## ❓ Preguntes freqüents

**P: Les automatitzacions no funcionen**
R: Revisa que els Entity IDs coincideixin amb els de la teva configuració. Comprova també els logs de Home Assistant per errors.

**P: Les targetes no es mostren correctament**
R: Assegura't que el mode d'edició del dashboard és YAML. Algunes targetes personalitzades s'han d'instal·lar des del Mercat.

**P: Com puc veure l'estructura de les dades de predicció?**
R: Utilitza **Developer Tools** → **Template** i executa:
```yaml
{{ state_attr('sensor.TU_MUNICIPI_prediccio_horaria', 'forecast') }}
```

**P: Els gràfics de quotes no es mostren**
R: Necessites que passi almenys un dia perquè Home Assistant tingui dades històriques per mostrar en gràfics.

## 🤝 Contribuir

Si tens exemples útils que vulguis compartir, si us plau:

1. Fork del repositori
2. Afegeix el teu exemple amb comentaris
3. Envia un Pull Request

## 📝 Llicència

Aquests exemples estan sota la mateixa llicència GPL-3.0 del projecte principal.

---

**Enllaços útils:**
- [Repositori principal](https://github.com/PacmanForever/meteocat_community_edition)
- [Documentació Home Assistant](https://www.home-assistant.io/docs/)
- [Documentació Lovelace](https://www.home-assistant.io/lovelace/)
- [Mercat (abans HACS)](https://www.home-assistant.io/integrations/marketplace/)
