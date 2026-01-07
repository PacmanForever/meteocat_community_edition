# Changelog

Tots els canvis notables del projecte es documenten aquí.

El format es basa en [Keep a Changelog](https://keepachangelog.com/ca/1.0.0/),
i el projecte segueix [Semantic Versioning](https://semver.org/lang/ca/).

## [1.2.57] - 2026-01-07

### Qualitat
- **Tests**: Afegits nous tests per garantir la cobertura del codi dels sensors per sobre del 95% (fixat al 97%).

## [1.2.56] - 2026-01-07

### Millores
- **Optimització**: Eliminat l'atribut `forecast` (raw) dels sensors de predicció diària i horària per reduir la mida de l'objecte d'estat a la base de dades i evitar limitacions de Home Assistant (>16KB). Es manté `forecast_ha`.
- **Qualitat**: Incrementada la cobertura de tests al 95%.

### Corregit
- **Config Flow**: Corregida la validació de banderes booleanes en el flux d'opcions per a entrades antigues.
- **Config Flow**: Millora en la gestió de tipus de mapeig invàlids.

## [1.2.55] - 2026-01-07

### Canvis
- **Tipus d'Integració**: Canviat el tipus d'integració de `hub` a `service`. Això canviarà la classificació a la interfície de Home Assistant, mostrant les entrades com a serveis ("Services") o entrades genèriques, evitant la confusió de "Hub" (Concentrador) que no s'adiu amb un servei al núvol.
- **Interfície**: Actualitzat el literal del formulari de mapeig personalitzat per avisar sobre la modificació de valors.

### Corregit
- **Gestió de Quota**: Corregit un error on el consum de quota no s'actualitzava si es realitzava una actualització que incloïa predicció o mesures forçades. Ara sempre que es faci una crida API que consumeixi quota, es refrescarà el comptador de peticions restants.

## [1.2.54] - 2026-01-07

### Corregit
- **Last Measurements Update**: El sensor "Última actualització mesures" en el mode d'estació externa ara només s'actualitza quan realment es descarreguen mesures, no quan s'actualitza només la predicció.
- **Configuració**: Corregit l'ordre del llistat de mapeig de condicions personalitzat a les opcions. Ara es mostra ordenat numèricament (ex: 0, 1, 2, 10...) en lloc d'alfabèticament.

## [1.2.53] - 2026-01-07

### Corregit
- **Arquitectura de Sensors**: Desacoblats completament els sensors de configuració (Municipi, Comarca, Província, Temps d'Actualització) de la classe `CoordinatorEntity`. Ara hereten directament de `SensorEntity` per garantir que el seu estat mai estigui lligat a l'èxit o fracàs de les crides API. Això elimina definitivament el problema de "No disponible" en aquestes entitats estàtiques.
- **Categoria d'Entitat**: Eliminada la categoria `CONFIG` per a aquests sensors. Ara es tracten com a sensors estàndard per evitar problemes de visibilitat o càrrega associats a categories restringides.

## [1.2.52] - 2026-01-07

### Corregit
- **Sensors de Configuració**: Afegida la propietat `available` explícita als sensors de Província per evitar que apareguin com a "No disponibles".
- **Estabilitat**: Reforçada la logica de disponibilitat en tots els sensors que depenen de dades estàtiques (Configuració).

## [1.2.51] - 2026-01-07

### Corregit
- **Error Crític**: Corregit un error `NameError: name 'entity_registry' is not defined` que impedia la càrrega de la integració.

## [1.2.46] - 2026-01-07

### Corregit
- **Entitats de Configuració**: Mogudes les entitats de Latitud, Longitud i Altitud al grup de sensors per evitar que apareguin deshabilitades per defecte.
- **Disponibilitat**: Eliminada la categoria `CONFIG` i els listeners de registre en sensors geogràfics i de temps d'actualització per millorar la compatibilitat i assegurar que les entitats estiguin sempre habilitades.

- **Sensors Geològics**: Revertit el canvi de categoria dels sensors d'altitud, latitud i longitud. Mantenen `EntityCategory.CONFIG` però amb el listener del registre d'entitats que evita que es deshabilten quan es mouen entre grups.

## [1.2.44] - 2025-01-02

### Corregit
- **Disponibilitat dels Sensors de Configuració**: Millorat el mètode `async_added_to_hass` per escoltar esdeveniments del registre d'entitats i re-habilitar automàticament els sensors de configuració quan es deshabilten en moure's entre grups a la interfície d'usuari de Home Assistant.

## [1.2.43] - 2025-01-02

### Corregit
- **Sintaxi JSON**: Eliminada coma final no permesa al manifest.json que impedia la càrrega de la integració a HACS.

## [1.2.42] - 2025-01-02

### Corregit
- **Disponibilitat dels Sensors de Configuració**: Millorat el mètode `async_added_to_hass` per cridar primer al mètode pare i esperar les actualitzacions del registre d'entitats, assegurant una gestió més robusta de l'estat d'habilitació dels sensors de configuració quan es mouen entre grups.

## [1.2.41] - 2025-01-02

### Corregit
- **Disponibilitat dels Sensors de Configuració**: Implementat `async_added_to_hass` en tots els sensors de configuració per gestionar correctament els canvis de categoria d'entitat al registre d'Home Assistant, assegurant que els sensors es mantinguin sempre disponibles i habilitats després de ser moguts entre grups.

## [1.2.40] - 2025-01-02

### Corregit
- **Disponibilitat dels Sensors de Configuració**: Arreglada definitivament la disponibilitat dels sensors de categoria "configuració" configurant `_attr_available = True` abans de la inicialització del coordinador, assegurant que es mostrin sempre com a disponibles a la interfície d'usuari.

## [1.2.39] - 2025-01-02

### Corregit
- **Disponibilitat dels Sensors de Configuració**: Reforçada la disponibilitat dels sensors de categoria "configuració" mitjançant múltiples mecanismes per assegurar que sempre retornin `True` i es mostrin correctament disponibles a la interfície d'usuari.

## [1.2.38] - 2025-01-02

### Millorat
- **Cobertura de Tests**: Afegida cobertura de tests completa per als sensors de configuració, assegurant que la disponibilitat i l'activació per defecte funcionin correctament.

## [1.2.37] - 2025-12-21

### Corregit
- **Disponibilitat dels Sensors de Configuració**: Corregida la disponibilitat dels sensors de categoria "configuració" (Comarca, Municipi, Província, Latitud, Longitud, Altitud) perquè sempre retornin `True`, assegurant que es mostrin correctament a la interfície d'usuari. A més, aquests sensors ara s'activen per defecte per mostrar els seus valors immediatament.

## [1.2.36] - 2025-12-21

### Millorat
- **Organització de Sensors per Categories**: Reorganitzats els sensors d'entitats per millorar la interfície d'usuari. Els sensors geogràfics (Comarca, Municipi, Província, Latitud, Longitud) i de temps d'actualització (Hora d'actualització 1, 2, 3) ara apareixen a la categoria "configuració" en lloc de barrejar-se amb sensors de mesura o diagnòstic, tant per estacions externes com locals.

### Corregit
- **Interfície de Configuració de Prediccions**: Corregida la visualització dels controls de predicció horària i diària per mostrar checkboxes en lloc de selectors True/False, millorant la usabilitat en la creació i edició d'estacions.

## [1.2.35] - 2025-12-15

### Corregit
- **Traduccions del Flux de Configuració**: Afegides traduccions completes per als errors de validació en el context de configuració, assegurant que tots els missatges d'error es mostrin correctament traduïts en la creació d'estacions.

## [1.2.34] - 2025-12-15

### Corregit
- **Traduccions Completes del Flux d'Opcions**: Afegides traduccions completes per als errors de validació en el context d'opcions, assegurant que tots els missatges d'error es mostrin correctament traduïts tant en la creació com en l'edició d'estacions.

### Millorat
- **Tests de Regressió**: Afegits tests integrals per validar el comportament de validació de prediccions en tots els modes d'estacions.
- **Neteja de Codi**: Eliminat fitxer obsolet del sistema d'agents.

## [1.2.33] - 2025-12-15

### Corregit
- **Errors de Validació No Traduïts**: Solucionats els missatges d'error no traduïts ("value must be one of ['custom', 'meteocat']" i "must_select_one_forecast") que apareixien en els fluxos de configuració durant la creació i edició d'estacions.
- **Validació de Tipus Booleans**: Afegida validació defensiva per assegurar que els valors de forecast (enable_daily, enable_hourly) siguin sempre booleans vàlids, prevenint errors de validació.
- **Controls de Validació Explícits**: Canviats els controls de validació de condicions ambigus (`not enable_daily`) a controls explícits (`enable_daily is False`) per evitar problemes amb valors `None`.

### Millorat
- **Robustesa del Flux d'Opcions**: Millorada l'estabilitat dels fluxos de configuració amb validacions més robustes i correcció automàtica de dades corruptes.

## [1.2.31] - 2025-12-14

### Corregit
- **Separació Data/Options**: Corregida la separació entre `data` i `options` en el options flow. Ara les opcions editables es llegeixen i es guarden correctament, solucionant problemes de corrupció en edicions múltiples.
- **Edició Múltiple d'Estacions Locals**: Solucionat el problema de corrupció de dades quan s'edita la mateixa estació local múltiples vegades consecutives.
- **Canvi de Mapping Type**: Corregida la gestió de canvis de mapping type entre edicions, assegurant que les dades custom es preserven/netegen correctament.
- **Validació de Mapping Type**: Millorada la validació i correcció automàtica de valors invàlids de mapping_type en entrades existents.

### Millorat
- **Tests de Seqüències**: Afegits tests integrals per a seqüències d'edició múltiple, incloent canvis de mapping type i edicions consecutives, cobrint escenaris que abans fallaven.
- **Robustesa del Options Flow**: Millorada l'estabilitat general del flux d'opcions amb millor gestió d'estat entre edicions.

## [1.2.30] - 2025-12-14

### Corregit
- **API Key Preservation per Estacions Externes**: Solucionat el problema de pèrdua d'API key durant l'edició d'opcions d'estacions externes. Ara l'API key es valida i migra automàticament des d'opcions a dades durant l'inici del flux d'opcions, independentment dels canvis d'usuari.
- **Robustesa del Flux d'Opcions**: Millorada la lògica de migració d'API key per assegurar que sempre estigui disponible, amb logging detallat per depuració.
- **Tests de Migració**: Afegits tests integrals per verificar la preservació i migració d'API key en estacions externes, amb verificacions intermèdies per assegurar la integritat en cada pas.

### Millorat
- **Separació de Lògica**: Refactoritzada la lògica d'opcions per separar la migració d'API key dels canvis de configuració d'usuari, fent el codi més mantenible i robust.

## [1.2.29] - 2025-12-14

### Corregit
- **Validació de Mapping Type**: Millorada la validació del tipus de mapping amb fallback segur per evitar errors "value must be one of ['custom', 'meteocat']" durant l'edició d'estacions.
- **API Key Preservation**: Reforçada la preservació de l'API key durant tot el flux d'opcions editant, assegurant que es manté en tots els passos del procés.
- **Logging de Debug**: Afegit logging detallat per diagnosticar problemes de validació de mapping_type.
- **Tests Integrals**: Afegits tests integrals que verifiquen la seqüència completa d'edició d'estacions locals, incloent preservació d'API key i validació de mapping types.

### Millorat
- **Robustesa del Flux d'Opcions**: Millorada l'estabilitat del flux d'edició d'opcions amb validacions més robustes i preservació de dades crítica.

## [1.2.28] - 2025-12-14

### Corregit
- **API Key Preservation**: S'ha corregit definitivament el problema de corrupció d'estacions durant l'edició fent l'API key immutable. Ara l'API key només s'emmagatzema a `entry.data` (immutable) i no a `entry.options` (mutable). S'ha afegit lògica de migració automàtica per entrades existents.
- **Tests**: Afegits tests de migració per verificar que l'API key es mou correctament de `options` a `data` quan cal.

## [1.2.27] - 2025-12-14

### Corregit
- **Traduccions**: Afegit el step "condition_mapping_type_local" a strings.json per evitar que es mostri "Opcions" com a títol genèric.
- **Labels**: Corregit el label del camp mapping_type per mostrar el text traduit correctament.
- **API Key Preservation**: S'ha corregit un problema on l'API key es perdia quan s'editaven les opcions d'estacions locals i s'utilitzava mapping personalitzat de condició climàtica.

## [1.2.26] - 2025-12-14

### Corregit
- **Corrupció d'estacions externes**: S'ha corregit un error crític on editar una estació externa o reiniciar Home Assistant provocava que l'estació quedés corrupta amb error d'autenticació 403. Ara es valida que la clau API existeixi abans de guardar els canvis.

## [1.2.25] - 2025-12-14

### Corregit
- **Traduccions d'opcions**: S'han afegit les traduccions faltants per al step `condition_mapping_type_local` a `strings.json`, corregint el títol que apareixia com "Opcions" en comptes de "Condició climàtica" i el label del camp mapping_type.
## [1.2.25] - 2025-12-13

### Corregit
- **Corrupció d'estacions externes**: S'ha corregit un error crític on editar una estació externa o reiniciar Home Assistant provocava que l'estació quedés corrupta amb error d'autenticació 403. Ara es valida que la clau API existeixi abans de guardar els canvis.

## [1.2.24] - 2025-12-13

### Millorat
- **Manteniment**: Versió de manteniment per resoldre problemes de caché de traduccions.

## [1.2.23] - 2025-12-13

### Millorat
- **Manteniment**: Versió de manteniment amb millores internes.
- **Documentació**: S'ha documentat que els títols de les pantalles d'opcions mostren "Configura la predicció de Meteocat" per estacions externes i "Configura l'estació local" per estacions locals, tal com està implementat al codi.

## [1.2.22] - 2025-12-13

### Corregit
- **Flux d'opcions**: S'ha corregit la selecció del tipus de mapping a l'editar estacions locals, eliminant un paràmetre que interferia amb la visualització del valor per defecte.
- **Tests**: S'han actualitzat els tests de traduccions per coincidir amb els fitxers de traduccions actuals.

## [1.2.21] - 2025-12-13

### Millorat
- **Gestió de dades i opcions**: Separades correctament les dades immutables (API key en `data`) de les configuracions editables (temps d'actualització i opcions de forecast en `options`) per prevenir corrupció d'entrades quan s'editen múltiples vegades.

### Corregit
- **Error "already_in_progress"**: Solucionat l'error que apareixia quan es creaven estacions locals, eliminant l'actualització innecessària del context del flow.
- **Flux d'opcions**: Millorada l'estabilitat del flux d'opcions amb logging detallat per diagnosticar problemes.
- **Tests**: Arreglat el test d'opcions flow per verificar correctament la preservació de l'API key.

## [1.2.20] - 2025-12-12

### Notes de la versió
- Versió de manteniment amb millores de validació UI i estabilitat.

## [1.2.19] - 2025-12-12

### Corregit
- **Validació UI**: Els camps de temperatura i humitat requerits en les pantalles de sensors locals ara mostren correctament l'estil d'error (vora vermella) quan es deixen en blanc, tant en creació com en edició d'estacions.
- **Preservació de la clau API**: Millorada la preservació de la clau API en editar configuracions, emmagatzemant-la tant a `data` com a `options` per major seguretat. Afegit logging detallat al coordinador per diagnosticar problemes amb la clau API.

## [1.2.18] - 2025-12-12

### Corregit
- **Preservació de la clau API**: Corregit el problema on la clau API es perdia quan s'editava una estació o configuració local. Ara es garanteix que la clau API es manté en les dades de l'entrada durant tot el flux d'opcions.

## [1.2.17] - 2025-12-12

### Corregit
- **Preservació de la clau API**: Corregit el problema on la clau API es perdia quan s'editava una estació o configuració local. Ara es garanteix que la clau API es manté en les dades de l'entrada durant tot el flux d'opcions.

## [1.2.16] - 2025-12-12

### Millorat
- **Flux de reconfiguració**: Simplificat el flux de reconfiguració per saltar l'entrada de clau API i anar directament a la selecció de mode
- **Camp URL de l'API**: Sempre visible en el pas inicial per a major consistència
- **Traduccions**: Afegit missatge d'advertència a la pantalla de sensors locals sobre les limitacions de les targetes meteorològiques

### Corregit
- **Flux d'opcions locals**: Afegit title_placeholders faltants al pas init_local per evitar errors de traducció

## [1.2.15] - 2025-12-12

### Millorat
- **Flux d'edició d'estacions locals**: Reordenat el flux d'opcions per coincidir amb el de creació (sensors → tipus de mapping)
- **Interfície de reconfiguració**: Ocultat el camp URL de l'API quan es reconfiguren entrades existents
- **Títols de pantalles**: Millorat el títol de l'edició d'estacions locals
- **Traduccions**: Actualitzada la descripció dels sensors locals en tots els idiomes

### Corregit
- **Ordre del flux d'opcions**: Les proves ara reflecteixen correctament l'ordre sensors → mapping type

## [1.2.14] - 2025-12-12

### Millorat
- **Validació de camps obligatoris**: Millorada la validació dels sensors de temperatura i humitat en les pantalles de creació i edició
- **Missatges d'error**: Els camps buits ara es posen vermells i mostren l'etiqueta "obligatori" correctament
- **Experiència d'usuari**: Interfície més robusta amb feedback visual adequat per camps requerits

### Afegit
- **Test de validació**: Afegit test exhaustiu per verificar la validació dels camps de sensors requerits

## [1.2.12] - 2025-12-11

### Millorat
- **Interfície d'usuari simplificada**: Eliminat el text redundant "(obligatori)", "(obligatorio)" i "(required)" dels labels dels camps requerits
- **Validació millorada**: Els camps requerits ara mostren missatges d'error de validació en comptes de text redundant als labels
- **Experiència d'usuari millorada**: Interfície més neta i professional sense text innecessari

### Afegit
- **Test de traduccions d'errors**: Afegit test per verificar que els missatges d'error de camps requerits existeixen en tots els idiomes

## [1.2.11] - 2025-12-11

### Millorat
- **Textos de la interfície d'usuari millorats**: Canviats els títols i etiquetes de les pantalles de configuració per ser més clars i consistents
- **Pantalla d'edició del mapping**: Títol canviat a "Configuració del mapeig de la condició climàtica" i etiquetes dels camps millorades
- **Pantalla de creació d'estacions**: Títol "Actualització de prediccions" canviat a "Configuració de prediccions" i eliminada la descripció redundant

### Afegit
- **Tests de traduccions**: Afegits tests exhaustius per verificar que totes les traduccions estiguin correctes en català, castellà i anglès

## [1.2.10] - 2025-12-11

### Millorat
- **Títols de pantalles d'opcions millorats**: Les pantalles d'edició d'estacions externes mostren "Configuració estació externa [nom estació]" i les locals mostren "Configuració estació local [nom municipi]"
- **Text del camp mapping_type corregit**: Canviat a "Tipus de mapeig per la condició climàtica" per ser més descriptiu
- **Traduccions actualitzades**: Millores en els fitxers de traducció per a millor usabilitat

### Corregit
- **Model del binary sensor corregit**: Canviat "Predicció Municipal" a "Estació Local" per consistència
- **Flux d'opcions locals**: Afegit el mètode `async_step_init_local` per gestionar correctament les opcions d'estacions locals

## [1.2.9] - 2025-12-11

### Afegit
- **Documentació completa del mapping de condicions**: S'afegeix secció detallada al README sobre com configurar i editar el mapping personalitzat de condicions climàtiques
- **Guia d'edició de mapping existent**: Instruccions pas a pas per modificar el mapping d'estacions ja configurades
- **Documentació del comportament "unknown"**: Explicació de quan i per què es mostra "unknown" amb icona genèrica

### Millorat
- **Interfície d'opcions simplificada**: S'elimina text descriptiu redundant de la pantalla d'opcions per a millor usabilitat
- **Títol de pantalla d'opcions**: Canviat a "Configuració" per ser més genèric i clar
- **Flux d'edició optimitzat**: Quan s'edita un mapping personalitzat existent, el flux acaba directament sense tornar als sensors

### Corregit
- **Millores en les traduccions**: Actualitzacions i correccions en els fitxers de traduccions

## [1.2.8] - 2025-12-11

### Afegit
- **Edició de mapping de condicions**: Les estacions locals existents ara poden canviar entre mapping Meteocat i personalitzat directament des de les opcions, sense necessitat de recrear l'entitat
- **Millora de l'experiència d'usuari**: S'elimina el checkbox i s'afegeix un selector directe de tipus de mapping al formulari d'opcions
- **Tests complets**: S'afegeixen tests per verificar el canvi entre tipus de mapping

### Corregit
- **Correcció ortogràfica**: "targes" → "targetes" en les traduccions al català

## [1.2.7] - 2025-12-11

### Corregit
- **Millora del fallback de condició**: Quan no es pot mapar un valor de sensor local a una condició meteorològica vàlida, ara retorna `None` en lloc de "cloudy" per ser més precís

## [1.2.6] - 2025-12-11

### Corregit
- **Correcció d'icones monocromes**: S'arregla que les icones dels estats del temps locals amb mapatge personalitzat apareixien en blanc i negre en lloc de colors
- **Millora de l'atribució**: L'atribució de l'entitat weather local ara inclou el nom del municipi en lloc de text genèric
- **Correcció de sensors locals de condició**: Els sensors locals de condició ara apliquen correctament el mapping configurat (personalitzat o per defecte) als valors numèrics
- S'afegeix gestió correcta dels tipus de claus (integer vs string) per als mapatges de condicions personalitzats
- **Correcció del flow d'opcions**: Les estacions locals existents sense mapping configurat ara passen pels steps de configuració de mapping quan es reconfiguren

### Millorat
- Experiència visual millorada amb icones de colors correctes en mapatges personalitzats
- Informació d'atribució més específica i útil per als usuaris
- Suport complet per sensors locals de condició amb mapping automàtic

## [1.2.5] - 2025-12-11

### Corregit
- **Correcció crítica**: S'arregla error `KeyError: 'municipality_name'` a l'entitat weather local
- L'entitat weather local ara utilitza un nom per defecte quan no hi ha informació de municipi
- S'assegura que la informació de municipi i comarca es guarda sempre als entries del mode local
- S'afegeixen millores de robustesa al config flow per gestionar casos on les dades d'API són incompletes
- **Millora del mode local**: Ara té paritat completa amb el mode extern (sensors disponibles, entitat weather, etc.)
- S'afegeixen logs de debug per ajudar en el diagnòstic de problemes futurs

### Millorat
- Millora de l'experiència d'usuari en mode local amb totes les funcionalitats disponibles
- Config flow més robust per gestionar dades d'API variables

## [1.2.4] - 2025-12-11

### Corregit
- **Correcció crítica**: Millor gestió d'entrades existents sense clau API
- S'afegeixen missatges d'error clars per a entrades antigues que falten la clau API
- S'afegeixen tests de regressió per prevenir que el problema torni a ocórrer
- **Correcció crítica**: S'arregla que les estacions locals es creaven incorrectament com a mode extern
- S'assegura que el camp CONF_MODE s'inclou correctament a totes les entrades de configuració
- S'afegeixen tests de regressió per verificar que el mode es configura correctament

## [1.2.3] - 2025-12-11

### Corregit
- **Correcció crítica**: S'arregla error `KeyError: 'api_key'` que impedia completar la configuració
- S'assegura que l'api_key i api_base_url s'inclouen correctament a les dades d'entrada
- S'afegeixen tests regressius per prevenir que aquest error torni a ocórrer

## [1.2.2] - 2025-12-11

### Millorat
- Millora de l'exemple de mapping personalitzat amb totes les condicions climàtiques de Home Assistant
- Etiquetes de camps obligatoris més clares amb "(obligatori)" als formularis de configuració
- Unificació de la terminologia: canvi d'"Entitat" a "Sensor" per millor consistència
- Experiència d'usuari millorada amb exemples més complets i textos més clars

## [1.2.1] - 2025-12-11

### Millorat
- Millores en les traduccions i textos de la interfície de configuració
- Actualització dels textos de mapeig de condicions climàtiques per millor usabilitat
- Correcció d'icones de botons per utilitzar icones vàlides de Material Design

### Corregit
- Correcció d'errors en la configuració d'estacions externes amb mapeig personalitzat
- Assegurar que les dades d'API es propaguen correctament en totes les configuracions
- Validació de traduccions corregida per complir amb els requisits de Home Assistant

## [1.2.0] - 2025-12-11

### Millorat
- Cobertura de tests significativament millorada (>90%) apropant-se al nivell Silver de Home Assistant
- Tests comprehensius afegits per weather.py, coordinator.py i config_flow.py
- Millores en el tractament d'errors i casos límit en les propietats del temps
- Tests de gestió d'errors d'API i casos de dades faltants

### Corregit
- Correcció de constructors de tests per utilitzar mocks adequats de Home Assistant
- Millores en la gestió de zones horàries en tests de planificació

---

### Afegit
- Millora de la gestió de l'URL de l'API: ara es garanteix que la URL de proves s'utilitza sempre si està configurada.
- Debug logging millorat per traçar totes les crides a l'API i la URL utilitzada.

### Millorat
- Camps requerits (condició, temperatura, humitat) marcats visualment a la UI de configuració.
- Traduccions revisades i errors de JSON corregits.

### Corregit
- Correcció de l'icona del botó "refresh measurements".
- Ordre correcte dels passos del config flow en mode local (mapping després de sensors).
- Cobertura de tests ampliada (302/302 passats).

---
## [1.1.9] - 2025-12-10

### Afegit
- Pantalla de mapping en el config flow per mode local: permet personalitzar la correspondència de condicions meteorològiques.
- Test que verifica que la pantalla de mapping es mostra i que la lògica backend la crida.

### Millorat
- Camps requerits (condició, temperatura, humitat) marcats visualment a la UI de configuració.
- Traduccions revisades i errors de JSON corregits.
- Versió sincronitzada entre manifest i git tag.

### Corregit
- Ordre correcte dels passos del config flow en mode local (mapping després de sensors).
- Cobertura de tests ampliada (302/302 passats).

---
## [1.1.6] - 2025-12-10

### Afegit
- Marcat visual dels camps requerits (condició, temperatura, humitat) a la UI de configuració del temps per plantilla.
- Afegit test de regressió per garantir la correcta serialització de l'ozó.

### Millorat
- Millora de la gestió de l'ozó: ara es mostra com a extra_state_attribute i es serialitza correctament.
- Traduccions i esquema de configuració revisats per compatibilitat amb Home Assistant.

---
## [1.1.5] - 2025-12-10

### Afegit
- Nova pantalla de configuració per a la personalització de la correspondència de condicions meteorològiques (condition mapping) durant el config flow.

### Canviat
- Conversió automàtica de la velocitat del vent a km/h a l'entitat Weather (abans en m/s).

### Corregit
- Millores de robustesa i cobertura de tests per a la lògica de sensors locals i externs, especialment per a la velocitat del vent i la configuració avançada.

---
## [1.0.8] - 2025-12-09

### Corregit
- Afegides claus de traducció faltants per als sensors d'actualització de predicció (`strings.json`).

### Millorat
- Millora significativa de la cobertura de tests (90%).
- Afegits tests per a `api.py`, `button.py`, `coordinator.py` i `sensor.py`.

## [1.0.7] - 2025-12-09

### Afegit
- Sensors separats per al seguiment d'actualitzacions de mesures i prediccions en mode estació
  - 3 sensors per a mesures (horàries): última actualització, pròxima actualització, hora configurada
  - 3 sensors per a predicció (programades): última actualització predicció, pròxima actualització predicció
- Millor visibilitat sobre quan s'actualitzen les dades de l'estació vs les prediccions

### Millorat
- Millora en l'estabilitat dels tests unitaris i de components.
- Correcció de rutes en els fitxers de traducció durant els tests.

## [1.0.6] - 2025-12-09

### Afegit
- Actualitzacions horàries per a les dades de les estacions (temperatura, humitat, etc.).
- Model d'actualització híbrid: prediccions segons horari programat, dades d'estació cada hora.

### Canviat
- En mode estació, les mesures s'actualitzen cada hora mentre que les prediccions segueixen l'horari configurat

## [1.0.5] - 2025-12-09

### Canviat
- Reestructuració del conjunt de tests en carpetes `unit` i `component` per millorar l'organització i l'execució en CI.
- Separació dels workflows de GitHub Actions per a tests unitaris i de components.

## [1.0.4] - 2025-12-08

### Corregit
- Corregit error de traducció en el flux d'opcions on la variable `{measurements_info}` no es proporcionava correctament en mode municipi.
- Corregit problema de visibilitat del camp "Tercera actualització" en el flux de configuració i opcions.

## [1.0.0] - 2025-11-29

Primera versió estable de la integració Meteocat Community Edition per a Home Assistant.

### Afegit

- **Mode Estació (XEMA)**: Integració completa amb estacions meteorològiques XEMA
  - Dades meteorològiques en temps real
  - Entitat Weather amb condicions actuals i prediccions
  - Suport per a múltiples estacions

- **Mode Municipi**: Mode de només prediccions sense estació
  - Sensor de predicció horària (72 hores)
  - Sensor de predicció diària (8 dies)

- **Gestió d'actualitzacions**:
  - Hores d'actualització configurables (per defecte: 06:00 i 14:00)
  - Botó d'actualització manual
  - Sensors de timestamp (última actualització, pròxima actualització)

- **Sistema d'esdeveniments**: Event `meteocat_community_edition_data_updated` en cada actualització
  - Conté mode, codis estació/municipi i timestamp

- **Sensors de quotes API**: Monitoratge en temps real de peticions disponibles
  - Plans suportats: Predicció, Referència, XDDE, XEMA
  - Mostra límit total, peticions utilitzades i data de reset

- **Retry logic amb exponential backoff**:
  - Automàtic en errors de xarxa
  - Màxim 3 retries amb delays creixents (1s, 2s, 4s)
  - Suport per a rate limiting (HTTP 429 amb Retry-After header)

- **Flux de re-autenticació**: Gestió automàtica de claus API expirades
  - ConfigEntryAuthFailed per a casos de credencials invàlides
  - Flux UI per a introduir nova clau sense eliminar la integració

- **Internacionalització**: Traduccions completes en:
  - Català (ca)
  - Castellà (es)
  - Anglès (en)

- **Suite de tests complet**: 200+ tests amb alta cobertura
  - Proves d'API, sensors, configuració, coordinació i retry logic
  - Proves de grupament de dispositius i triggers

- **CI/CD**:
  - GitHub Actions per a Python 3.11 i 3.12
  - pytest, flake8, HACS i Hassfest checks

- **Documentació complet**:
  - READMEs en 3 idiomes
  - Exemple d'automacions i Lovelace dashboard
  - Guies de qualitat i contribució

### Canviat

- Sensor binari d'estat: nom canviat a "Última actualització correcte" per a major claredat
- Entitat del sensor binari: ja no inclou el nom del dispositiu en el seu nom visual
- Sensor de Província: millora per a no crear-se si la dada no està disponible

### Seguretat

- Claus API emmascarades als logs
- Emmagatzematge segur de credencials via config entries de Home Assistant

---

## Plantilla per a futures versions

```
## [X.Y.Z] - YYYY-MM-DD

### Afegit
- Noves funcionalitats

### Canviat
- Canvis en funcionalitats existents

### Deprecat
- Funcionalitats que s'eliminaran aviat

### Eliminat
- Funcionalitats eliminades

### Corregit
- Correccions de bugs

### Seguretat
- Correccions de seguretat
```

