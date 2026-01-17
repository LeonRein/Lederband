# Lederband

## Installation

Zur Nutzung von Lederband muss zuerst das Programm "uv" installiert werden.

1. **uv installieren**:
   - Am einfachsten über die Eingabeaufforderung (cmd) mit folgendem Befehl:
     `winget install uv`
   - Alternativ kann uv auch von der offiziellen Website heruntergeladen und installiert werden.

2. **Lederband starten**:
   - Die Zip-Datei unter "Releases" herunterladen und entpacken.
   - Durch Doppelklick auf die Datei `Lederband.bat` wird das Programm gestartet.

## Ordnerstruktur

Das Programm nutzt folgende Ordner zur Organisation der Dateien:

- **presets**: Ablageort für gespeicherte Voreinstellungen (Presets).
- **input/backgrounds**: Ablageort für Hintergrundbilder.
- **input/badges**: Ablageort für Abzeichen.
  - Hinweis: Es können Unterordner erstellt werden, um verschiedene Arten von Abzeichen zu sortieren (z. B. ein Ordner für alle Treue-Abzeichen oder einer für sehr kleine Abzeichen).
  - Wichtig: Alle Bilder sollen im PNG-Format vorliegen. Für jedes Abzeichen muss im Ordner eine eigene PNG-Datei erstellt werden.

## Hinweise zur Nutzung

- **Größe und Hintergrund**: Der gewählte Hintergrund gibt die Größe des gesamten Bildes vor. Es sollte darauf geachtet werden, dass die Abzeichen möglichst die gleiche Breite wie der Hintergrund haben. Andernfalls werden die Abzeichen skaliert, was zu unschönen Ergebnissen führen kann.
- **Zwei Abzeichen nebeneinander**: Es besteht die Möglichkeit, zwei Abzeichen nebeneinander zu platzieren. Wenn zwei Abzeichen nebeneinander platziert werden, sollten diese am besten gleich hoch sein. Die ideale Breite beträgt: (Breite des Hintergrunds / 2) + 1 Pixel (da jeweils 1 Pixel an der Stoßkante in der Mitte entfernt wird). Dies verhindert, dass ein störender schwarzer Strich zwischen den Abzeichen sichtbar bleibt.
- **Exportieren**: Das fertige Lederband im Ordner `output` gespeichert. Der Dateiname des Bildes entspricht dabei exakt dem Namen des gewählten Presets.
