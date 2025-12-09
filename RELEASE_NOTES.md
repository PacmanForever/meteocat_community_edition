# v1.0.6 - Hourly Updates for Station Data

## 🚀 Noves Funcionalitats
- **Actualitzacions Horàries per a Estacions**: Les dades de les estacions (temperatura, humitat, etc.) ara s'actualitzen automàticament cada hora.
- **Model d'Actualització Híbrid**: Les prediccions continuen actualitzant-se a les hores programades (ex: 08:00, 20:00), mentre que les mesures de l'estació s'actualitzen cada hora.
- **Gestió de Quota Optimitzada**: La integració gestiona de manera intel·ligent la quota de l'API (~30 crides/dia en mode Estació).

## 📚 Documentació
- Actualitzats els README en Català, Castellà i Anglès per reflectir la nova lògica d'actualització.
- Actualitzat REQUIREMENTS.md amb informació detallada sobre l'ús de l'API.

## 🐛 Correccions
- Corregida la lògica de càlcul de `next_update` per suportar intervals horaris.
