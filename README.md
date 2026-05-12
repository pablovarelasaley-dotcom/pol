# Massaro Propiedades — Multimedia App

App multimedia para Raspberry Pi 5, pantalla táctil 1024×600.  
Funciona también en Windows para desarrollo.

---

## Instalación en Raspberry Pi

### 1 — Activar SSH en el Pi

En el Pi (con teclado/monitor conectado), abrí una terminal y ejecutá:

```bash
sudo raspi-config
```

Navegá a **Interface Options → SSH → Enable**.  
Anotá la IP del Pi con `hostname -I`.

---

### 2 — Copiar el proyecto desde Windows

En PowerShell de tu PC:

```powershell
scp -r C:\Users\pablo\Documents\rpi-multimedia pi@<IP-DEL-PI>:/home/pi/
```

O copiá la carpeta a un pendrive, enchufalo al Pi y copiala a `/home/pi/`.

---

### 3 — Instalar dependencias en el Pi

En una terminal del Pi:

```bash
cd /home/pi/rpi-multimedia
sudo bash install.sh
```

Esto instala: ffmpeg, GStreamer, SDL2, crea el entorno virtual Python  
y genera el script `start.sh`.  
Tarda unos minutos la primera vez.

---

### 4 — Poner el contenido

Copiá los archivos a las carpetas del proyecto:

```
LOGO/      → imágenes .png / .jpg del logo de la empresa
videos/    → videos (.mp4 .mov .mkv) y fotos (.jpg .png) de propiedades
```

---

### 5 — Probar

```bash
cd /home/pi/rpi-multimedia
bash start.sh
```

La app arranca en pantalla completa con `KIOSK=1`.  
Para salir durante pruebas: `Ctrl+C` en la terminal SSH.

---

### 6 — Autoarranque al encender el Pi (kiosk)

Crear el archivo de autostart:

```bash
mkdir -p ~/.config/autostart
nano ~/.config/autostart/massaro.desktop
```

Contenido:

```ini
[Desktop Entry]
Type=Application
Name=Massaro Propiedades
Exec=bash /home/pi/rpi-multimedia/start.sh
```

Guardá (`Ctrl+O`, `Enter`, `Ctrl+X`) y reiniciá el Pi.  
La app arrancará sola cada vez que el Pi encienda.

---

## Desarrollo en Windows

```powershell
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
pip install ffpyplayer   # backend de video para Windows
python main.py
```

Sin `KIOSK=1` la ventana es redimensionable (cómodo para desarrollar).

---

## Contenido soportado

| Carpeta   | Formatos                        |
|-----------|---------------------------------|
| `LOGO/`   | `.png` `.jpg` `.jpeg`           |
| `videos/` | `.mp4` `.mov` `.mkv` `.jpg` `.png` `.jpeg` |

Los thumbnails se generan automáticamente en `thumbnails/` al abrir la galería.

---

## Gestos en el reproductor

| Gesto              | Acción                  |
|--------------------|-------------------------|
| Swipe ←            | Archivo siguiente       |
| Swipe →            | Archivo anterior        |
| Tap simple         | Play / Pausa (videos)   |
| Doble tap          | Volver a la galería     |
| Long press (1 seg) | Volver al menú principal|
