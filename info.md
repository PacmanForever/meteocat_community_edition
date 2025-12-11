# 🌦️ Meteocat (Community Edition)

**Integració completa per a Home Assistant del Servei Meteorològic de Catalunya**

---

## ✨ Característiques principals

### 📡 Mode Estació XEMA
Dades meteorològiques **en temps real** de les estacions oficials del Meteocat:
- 🌡️ Temperatura, humitat, pressió
- 💨 Vent (velocitat i direcció)
- 🌧️ Precipitació
- 📊 Prediccions horàries i diàries
- ☁️ Entitat Weather completa

### 🏙️ Mode Municipal
Prediccions meteorològiques sense necessitat d'estació:
- ⏰ **Prediccions horàries** (72 hores)
- 📅 **Prediccions diàries** (8 dies)
- 💡 Ideal si ja tens una estació local

### 📈 Gestió intel·ligent
- 🔄 **2 actualitzacions diàries** (configurables)
- 📊 **Sensors de quotes API** (monitoratge en temps real)
- 🔘 **Botó d'actualització manual**
- ⏱️ **Timestamps** (última i pròxima actualització)
- 🎯 **Events** per automatitzacions avançades
- 🔁 **Retry automàtic** amb exponential backoff
- 🔑 **Re-autenticació** sense reiniciar

### 🌍 Internacionalització
Traduccions completes en **català**, **castellà** i **anglès**

---

## 🚀 Configuració ràpida

### Pas 1: Obtenir clau API
Registra't a [apidocs.meteocat.gencat.cat](https://apidocs.meteocat.gencat.cat/) i segueix el [procés de registre](https://apidocs.meteocat.gencat.cat/documentacio/proces-de-registre/).

### Pas 2: Afegir integració

**Opció A - Mode Estació XEMA** (dades en temps real + prediccions)
1. Configuració → Dispositius i Serveis → **Afegir integració**
2. Cerca **"Meteocat (Community Edition)"**
3. Introdueix la **clau API**
4. Selecciona **"Estació XEMA"**
5. Tria **comarca** i **estació**
6. Configura **hores d'actualització** (opcional)

✅ **Crea**: Entitat Weather + sensors de quotes + botó actualització

**Opció B - Mode Municipal** (només prediccions)
1. Configuració → Dispositius i Serveis → **Afegir integració**
2. Cerca **"Meteocat (Community Edition)"**
3. Introdueix la **clau API**
4. Selecciona **"Prediccions municipals"**
5. Tria **comarca** i **municipi**
6. Configura **hores d'actualització** (opcional)

✅ **Crea**: Sensors predicció horària + diària + quotes + botó

---

## 📊 Sensors creats

### Mode Estació
- `weather.{estacio}_{codi}` - Entitat Weather completa
- `sensor.{estacio}_{codi}_quota_*` - Quotes API (4 plans)
- `sensor.{estacio}_{codi}_last_update` - Darrera actualització
- `sensor.{estacio}_{codi}_next_update` - Pròxima actualització
- `sensor.{estacio}_{codi}_update_time_1/2` - Hores configurades
- `button.{estacio}_{codi}_refresh` - Actualització manual

### Mode Municipal
- `sensor.{municipi}_prediccio_horaria` - Predicció 72h
- `sensor.{municipi}_prediccio_diaria` - Predicció 8 dies
- `sensor.{municipi}_quota_*` - Quotes API (4 plans)
- `sensor.{municipi}_last_update` - Darrera actualització
- `sensor.{municipi}_next_update` - Pròxima actualització
- `sensor.{municipi}_update_time_1/2` - Hores configurades
- `button.{municipi}_refresh` - Actualització manual

---

## 🎯 Automatitzacions

Cada actualització dispara un **esdeveniment**:

```yaml
automation:
  - alias: "Notificació actualització Meteocat"
    trigger:
      - platform: event
        event_type: meteocat_community_edition_data_updated
    action:
      - service: notify.mobile_app
        data:
          message: "Noves dades meteorològiques!"
```

---

## ⚙️ Opcions avançades

Modifica la configuració a **Dispositius i Serveis** → 3 punts → **Opcions**:
- 🕐 **Hores d'actualització** (format 24h: HH:MM)
- 🔗 **Endpoint API personalitzat** (desenvolupament)

---

## 📚 Documentació completa

Consulta el [**README complet**](https://github.com/PacmanForever/meteocat_community_edition) per:
- 📖 Exemples d'automatitzacions avançades
- 🎨 Targetes Lovelace personalitzades
- 🔧 Sensors template
- 💾 Accés a dades de predicció
- ❓ Troubleshooting

---

## ⚡ Optimització de quotes

Aquesta integració està **optimitzada** per no superar els límits del pla gratuït:
- ✅ Només **2 actualitzacions diàries** (6:00 i 14:00)
- ✅ **Quotes consultades després** de les dades
- ✅ **Sensors de monitoratge** en temps real
- 💡 **Consell**: El pla domèstic permet poques consultes al mes. Crea diverses estacions amb API keys diferents per maximitzar l'ús de l'API!

---

## 🧪 Qualitat

- 🏆 **Home Assistant Silver Level** (>95% cobertura)
- ✅ **100+ tests** unitaris comprehensius
- ✅ **Validació HACS** (requisits complerts)
- ✅ **Validació Hassfest** (sense errors)
- ✅ **GitHub Actions CI/CD**
- ✅ **Linting flake8**

---

## ⚠️ Disclaimer

Integració **no oficial** creada per la comunitat. No està afiliada amb el Servei Meteorològic de Catalunya.

---

**Llicència**: GPL-3.0 | **Idiomes**: 🇨🇦 🇪🇸 🇬🇧
