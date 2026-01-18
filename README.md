# Lederband

## Installation unter Windows

Zur Nutzung von Lederband muss zuerst das Programm "uv" installiert werden.

1. **Windows Terminal starten**
   - Starte das *Windows Terminal* (z. B. über das Startmenü oder das Windows-Symbol).
   - Sollte Windows Terminal nicht installiert sein, verwende alternativ die *Eingeabeaufforderung*.
  
2. **uv installieren**:
   - Gib folgenden Befehl ein und bestätige mit Enter: `winget install uv`.
   - Sollte `winget` nicht verfügbar sein, folge der offiziellen [Installationsanleitung](https://docs.astral.sh/uv/getting-started/installation/) von *uv*.
3. **Lederband starten**:
   - *Source code (zip)* unter [Releases](https://github.com/LeonRein/Lederband/releases) herunterladen und entpacken.
   - Durch Doppelklick auf die Datei `Lederband.bat` wird das Programm gestartet.

## Ordnerstruktur

Das Programm nutzt folgende Ordner zur Organisation der Dateien:

- **presets**: Ablageort für gespeicherte Voreinstellungen.
- **input/backgrounds**: Ablageort für Hintergrundbilder.
- **input/badges**: Ablageort für Abzeichen.
> Hinweis: Es können Unterordner erstellt werden, um verschiedene Arten von Abzeichen zu sortieren (z. B. ein Ordner für alle Treue-Abzeichen oder einer für sehr kleine Abzeichen).

> Wichtig: Alle Bilder sollen im PNG-Format vorliegen.

## Hinweise zur Nutzung

- **Größe und Hintergrund**: Der gewählte Hintergrund gibt die Größe des gesamten Bildes vor. Es sollte darauf geachtet werden, dass die Abzeichen möglichst die gleiche Breite wie der Hintergrund haben. Andernfalls werden die Abzeichen skaliert, was zu unschönen Ergebnissen führen kann.
- **Zwei Abzeichen nebeneinander**: Es besteht die Möglichkeit, zwei Abzeichen nebeneinander zu platzieren. Wenn zwei Abzeichen nebeneinander platziert werden, sollten diese am besten gleich hoch sein. Die ideale Breite beträgt: (Breite des Hintergrunds / 2) + 1 Pixel (da jeweils 1 Pixel an der Stoßkante in der Mitte entfernt wird). Dies verhindert, dass ein störender schwarzer Strich zwischen den Abzeichen sichtbar bleibt.
- **Exportieren**: Das fertige Lederband wird im Ordner `output` gespeichert. Der Dateiname des Bildes entspricht dabei dem Namen des gewählten Presets plus dem Datum des erstellens der Datei (z.B. `2026-01-05 Fabian Scheel.png`).
