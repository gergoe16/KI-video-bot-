# KI Video Bot – Windows Starter

Erstellt kostenlose, vertikale Kurzvideos mit einem lokalen Ollama-Modell. Keine kostenpflichtigen KI-APIs.

## Was der Bot macht
- Lässt Ollama ein Thema, ein deutsches Skript und Szenentexte erzeugen
- Erstellt eine deutsche Sprachaufnahme über die Windows-Sprachausgabe (pyttsx3)
- Rendert ein 9:16-MP4 mit gestalteten Textszenen
- Speichert Video, Skript und Metadaten im Ordner `output`

> Hinweis: Diese Starter-Version erzeugt animierte Text-/Grafikkarten mit Sprachaufnahme, keine fotorealistischen KI-Filmszenen. Der Bot lädt Videos nicht automatisch auf TikTok oder YouTube hoch.

## Einmalige Einrichtung
1. Installiere Python 3.11 oder neuer: https://www.python.org/downloads/windows/  
   Beim Setup **Add Python to PATH** aktivieren.
2. Installiere Ollama: https://ollama.com/download/windows
3. Lade dieses Repository über **Code → Download ZIP** herunter und entpacke es, oder klone es mit Git.
4. Öffne den entpackten Ordner im Explorer.
5. Doppelklicke auf `INSTALL.bat`. Das installiert die Python-Pakete und lädt das lokale Modell `llama3.2`. Der Download kann einige Minuten dauern.
6. Doppelklicke auf `START.bat`, um ein Video zu erstellen.

## Wenn etwas nicht klappt
- Prüfe, ob Ollama installiert ist und das Modell heruntergeladen wurde.
- Öffne PowerShell im Bot-Ordner und führe `ollama list` aus.
- Wenn der Bot Ollama nicht erreicht, starte Ollama über das Startmenü. Falls nötig, öffne ein zweites PowerShell-Fenster und führe `ollama serve` aus.
- Wenn Windows meldet, dass Python nicht gefunden wird, installiere Python erneut und aktiviere **Add Python to PATH**.

## Anpassung
In `bot.py` kannst du Themenbereich, Videolänge und Modell ändern. Standardmäßig erstellt jeder Start ein neues Video im Ordner `output`.

## Kosten und Datenschutz
Das KI-Modell läuft lokal. Der erste Modelldownload benötigt Internet und Speicherplatz. Die erzeugten Skripte und Videos bleiben auf deinem PC, sofern du sie nicht selbst teilst.
