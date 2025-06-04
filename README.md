# 🚒 Feuerwehr WebApp

Eine Webanwendung zur Verwaltung und Organisation von Feuerwehraktivitäten.

## 🔧 Funktionen

- Erstellung von Einsatzberichten für Social Media
- Responsive Benutzeroberfläche (Direkt von der Einsatzstelle passende Berichte generieren!)
- ChatGPT anbindung möglich!

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
   ```

2. **Virtuelle Umgebung erstellen und aktivieren:**

   **Unter Linux / macOS:**

   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

   **Unter Windows:**

   ```bash
   python -m venv venv
   venv\Scripts\activate
   ```

3. **Abhängigkeiten installieren:**

   ```bash
   pip install -r requirements.txt
   ```

4. **Konfigurationsdatei erstellen:**

   Erstellen Sie eine `config.json`-Datei basierend auf der Vorlage `config_SAMPLE.json`.

   **Linux/macOS:**

   ```bash
   cp config_SAMPLE.json config.json
   ```

   **Windows (CMD):**

   ```cmd
   copy config_SAMPLE.json config.json
   ```

   Bearbeiten Sie `config.json`, um sie an Ihre Umgebung anzupassen.

5. **Anwendung starten:**

   ```bash
   python app.py
   ```

   Die Anwendung ist anschließend erreichbar unter:

   ```
   http://127.0.0.1:5000
   ```

## 🗂️ Projektstruktur

```plaintext
feuerwehr-webapp/
├── app.py
├── app.wsgi
├── config_SAMPLE.json
├── requirements.txt
├── modules/
├── static/
└── templates/
```

## 📄 Lizenz

Dieses Projekt steht unter der MIT-Lizenz. Weitere Informationen finden Sie in der [LICENSE](LICENSE)-Datei.

## 🤝 Beitrag leisten

Beiträge sind herzlich willkommen! Bitte öffnen Sie ein Issue oder einen Pull Request, um Änderungen vorzuschlagen.
