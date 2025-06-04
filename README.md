# 🚒 Feuerwehr WebApp

Eine Webanwendung zur Verwaltung und Organisation von Feuerwehraktivitäten.

## 🔧 Funktionen

- Verwaltung von Einsatzberichten
- Benutzerverwaltung
- Statistische Auswertungen
- Responsive Benutzeroberfläche

## 📦 Installation

### Voraussetzungen

- Python 3.8 oder höher
- pip (Python-Paketmanager)
- Virtuelle Umgebung (empfohlen)

### Schritte

1. **Repository klonen:**

   ```bash
   git clone https://github.com/MedizinPumPer/feuerwehr-webapp.git
   cd feuerwehr-webapp


2. **Virtuelle Umgebung erstellen und aktivieren:**

      ```bash
    python -m venv venv
    source venv/bin/activate  # Für Unix oder MacOS
    venv\Scripts\activate     # Für Windows

3. **Abhängigkeiten installieren:**

   ```bash
   pip install -r requirements.txt


4. **Konfigurationsdatei erstellen:**

Erstellen Sie eine config.json-Datei basierend auf der bereitgestellten config_SAMPLE.json.

   ```bash
    cp config_SAMPLE.json config.json  # Linux/Mac
    copy config_SAMPLE.json config.json  # Windows

Passen Sie die config.json entsprechend Ihrer Umgebung an.


5. **Anwendung starten:**

   ```bash
    python app.py


## 🗂️ Projektstruktur

    ```bash
    feuerwehr-webapp/
    ├── app.py
    ├── app.wsgi
    ├── config_SAMPLE.json
    ├── requirements.txt
    ├── modules/
    ├── static/
    └── templates/

## 📄 Lizenz

Dieses Projekt steht unter der MIT-Lizenz. Weitere Informationen finden Sie in der LICENSE-Datei.


## 🤝 Beitrag leisten

Beiträge sind herzlich willkommen! Bitte öffnen Sie ein Issue oder einen Pull Request, um Änderungen vorzuschlagen.