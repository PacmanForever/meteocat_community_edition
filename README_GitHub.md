# 🚀 Instruccions per publicar a GitHub

## 1. Preparar el repositori Git

Obre PowerShell a la carpeta del projecte i executa:

```powershell
# Inicialitzar el repositori Git
git init

# Afegir tots els fitxers
git add .

# Primer commit
git commit -m "Initial commit - Meteocat Community Edition v1.0.0"
```

## 2. Crear el repositori a GitHub

1. Ves a https://github.com/new
2. Nom del repositori: `meteocat-community-edition` (o el que prefereixis)
3. Descripció: `Integració de Home Assistant per Meteocat amb suport XEMA i prediccions municipals`
4. Visibilitat: **Public** (necessari per HACS)
5. **NO** marquis "Add a README file" (ja el tens)
6. Crea el repositori

## 3. Connectar i pujar el codi

Copia l'URL del teu repositori i executa (canvia USERNAME pel teu usuari):

```powershell
# Afegir el remote
git remote add origin https://github.com/PacmanForever/meteocat_community_edition.git

# Pujar el codi
git branch -M main
git push -u origin main
```

## 4. Crear la primera release

1. Ves a https://github.com/USERNAME/meteocat-community-edition/releases
2. Clica "Create a new release"
3. Clica "Choose a tag" i escriu: `v1.0.0` (crea el tag)
4. Release title: `v1.0.0 - Initial Release`
5. Descripció (copia del CHANGELOG.md):

```markdown
# 🎉 Primera versió de Meteocat (Community Edition)

## ✨ Característiques principals

### Mode Estació
- Accés a dades d'estacions meteorològiques del XEMA
- Sensors de temperatura, humitat, pressió, precipitació, vent...
- Actualitzacions automàtiques cada 6 hores

### Mode Municipi
- prediccions meteorològiques per municipis de Catalunya
- predicció horària (properament 3 dies)
- predicció diària (6 dies)
- Índex UV màxim

### Gestió de quota API
- 4 sensors per monitorar consums API (Predicció, Referència, XDDE, XEMA)
- Visualització de peticions disponibles en temps real

### Utilitats
- **Botó de refrescament manual** per forçar actualitzacions
- **Sensors de timestamp** (última i pròxima actualització)
- Actualitzacions automàtiques a les 6:00 i 14:00
- Agrupació intel·ligent de totes les entitats per dispositiu

## 📦 Instal·lació

### Via HACS (recomanat)
1. Obre HACS a Home Assistant
2. Ves a "Integrations"
3. Clica els tres punts al canto superior dret
4. Selecciona "Custom repositories"
5. URL: `https://github.com/USERNAME/meteocat-community-edition`
6. Categoria: `Integration`
7. Clica "Add"
8. Cerca "Meteocat" i instal·la

### Manual
1. Descarrega `meteocat-community-edition.zip`
2. Extreu a `config/custom_components/meteocat/`
3. Reinicia Home Assistant

## 📚 Documentació

Consulta el [README complert](https://github.com/USERNAME/meteocat-community-edition#readme) per:
- Instruccions detallades de configuració
- Exemples de templates i automatitzacions
- Estructura de dades dels sensors
- Troubleshooting i FAQ

## 🙏 Agraïments

Gràcies a Meteocat per proporcionar l'API pública amb dades meteorològiques de Catalunya.
```

6. Marca "Set as the latest release"
7. Clica "Publish release"

**Automàticament es crearà un fitxer ZIP** gràcies al workflow `release.yaml`! 🎉

## 5. Afegir a HACS

Després de crear la release:

1. Obre un issue a https://github.com/hacs/default/issues/new?template=integration.yml
2. Completa el formulari:
   - Repository: `https://github.com/USERNAME/meteocat-community-edition`
   - Category: `integration`
   - Completa la resta de camps

O simplement els usuaris poden afegir-lo com a **repositori personalitzat** (pas més ràpid):

1. HACS > Integrations > Three dots menu > Custom repositories
2. URL: `https://github.com/USERNAME/meteocat-community-edition`
3. Category: `Integration`

## 6. Verificar els workflows

Després del push, verifica que els workflows funcionin:

1. Ves a https://github.com/USERNAME/meteocat-community-edition/actions
2. Hauries de veure:
   - ✅ **Validate**: HACS i Hassfest validation
   - ✅ **Tests**: pytest executat (pot fallar si no tens HA instal·lat localment, és normal)
   - ✅ **Release**: ZIP creat (només després de crear la release)

## 7. Configurar GitHub Pages (opcional)

Per tenir una pàgina web del projecte:

1. Settings > Pages
2. Source: Deploy from a branch
3. Branch: `main`, folder: `/ (root)`
4. Save

El README es mostrarà a: `https://USERNAME.github.io/meteocat-community-edition`

## ✅ Checklist final

- [ ] Repositori Git inicialitzat i pujat
- [ ] Primera release v1.0.0 creada
- [ ] ZIP generat automàticament
- [ ] Workflows executats correctament
- [ ] HACS configurat (repositori personalitzat o solicitud enviada)
- [ ] README actualitzat amb l'URL correcta del repositori

## 🎯 Següents passos

1. **Compartir**: Anuncia la integració a la comunitat de Home Assistant
2. **Mantenir**: Respon issues i PRs
3. **Millorar**: Afegeix noves funcionalitats segons feedback
4. **Documentar**: Afegeix més exemples i casos d'ús

---

**Nota important**: Canvia `USERNAME` per el teu nom d'usuari de GitHub a tots els enllaços!

