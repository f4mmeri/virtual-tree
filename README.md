# Virtual-Tree
Proyecto Estructura asignada: Virtual Tree (Auxiliary Tree)

## Contenido del repositorio

* `virtual_tree.cpp`: implementación instrumentada del Virtual Tree. Cada paso de `build` (orden de las claves, cálculo de LCA, operaciones sobre la pila y aristas virtuales) se registra en un archivo JSON dentro de `logs/`.
* `logs/`: trazas generadas por `virtual_tree.cpp`: `vt_log_main.json` (caso principal) y `vt_log_edge.json` (caso borde: claves en una cadena).
* `animacion/virtual_tree.py`: script de Manim que lee los archivos de `logs/` y genera el video.
* `animacion/audio/`: narración grabada por escena, más `narracion_completa.m4a` (los 8 audios ya unidos).
* `VirtualTreeVideo_final.mp4`: video final con audio, entregado como parte de este proyecto.

## Software requerido

* Un compilador de C++17.
* Python 3.9 o superior.
* Manim Community 0.19.1.
* FFmpeg (lo usa Manim para generar el video).

## Instalación

```
python -m pip install manim==0.19.1
winget install -e --id Gyan.FFmpeg
```

## Pasos para reproducir el video

1. Compilar y correr la implementación en C++ (parado en la raíz del repo):

```
g++ -std=c++17 virtual_tree.cpp -o virtual_tree.exe
.\virtual_tree.exe
```

Esto crea la carpeta `logs/` con los archivos `vt_log_main.json` y `vt_log_edge.json`.

2. Renderizar la animación con Manim (alta calidad), también desde la raíz del repo:

```
python -m manim -pqh animacion/virtual_tree.py VirtualTreeVideo
```

El script agrega automáticamente la narración de `animacion/audio/narracion_completa.m4a`, así que el video renderizado ya incluye audio. Queda en `media/videos/virtual_tree/1080p60/VirtualTreeVideo.mp4`.

`VirtualTreeVideo_final.mp4` es ese mismo video, entregado como parte de este proyecto.

## Integrantes

Fabiana Ameri · Joaquín Justo