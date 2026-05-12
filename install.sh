#!/bin/bash
# Dependencias del sistema para Raspberry Pi OS Bookworm (Pi 5)
# Uso: sudo bash install.sh
# Debe correrse desde la carpeta del proyecto

set -e

PROYECTO_DIR="$(cd "$(dirname "$0")" && pwd)"

echo "=== Massaro Propiedades — Instalando dependencias ==="

apt update

# ffmpeg: genera thumbnails de video
apt install -y ffmpeg

# GStreamer: backend de video para kivy.uix.video.Video
apt install -y \
    gstreamer1.0-plugins-base \
    gstreamer1.0-plugins-good \
    gstreamer1.0-plugins-bad \
    gstreamer1.0-plugins-ugly \
    gstreamer1.0-libav \
    gstreamer1.0-tools \
    python3-gst-1.0

# Dependencias de Kivy / SDL2
apt install -y \
    python3-dev \
    python3-venv \
    libsdl2-dev \
    libsdl2-image-dev \
    libsdl2-mixer-dev \
    libsdl2-ttf-dev \
    libmtdev-dev \
    xclip

# unclutter: oculta el cursor del mouse en modo kiosk
apt install -y unclutter

echo ""
echo "=== Creando entorno virtual Python ==="
# --system-site-packages da acceso a python3-gst-1.0 (no instable via pip)
python3 -m venv "$PROYECTO_DIR/venv" --system-site-packages

echo ""
echo "=== Instalando dependencias Python ==="
"$PROYECTO_DIR/venv/bin/pip" install --upgrade pip
"$PROYECTO_DIR/venv/bin/pip" install -r "$PROYECTO_DIR/requirements.txt"

echo ""
echo "=== Creando script de arranque ==="
cat > "$PROYECTO_DIR/start.sh" << 'EOF'
#!/bin/bash
# Ocultar cursor y arrancar la app en modo kiosk
unclutter -idle 0 &
cd "$(dirname "$0")"
source venv/bin/activate
KIOSK=1 python main.py
EOF
chmod +x "$PROYECTO_DIR/start.sh"

echo ""
echo "=================================================="
echo " Instalación completa."
echo ""
echo " Probar ahora:"
echo "   cd $PROYECTO_DIR"
echo "   bash start.sh"
echo ""
echo " Para autoarranque al iniciar el Pi, agregar"
echo " al archivo ~/.config/autostart/massaro.desktop"
echo " (ver README.md)"
echo "=================================================="
