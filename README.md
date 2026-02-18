# Contador de Personas en Tiempo Real

Sistema de conteo de personas en tiempo real usando YOLO + ByteTrack. Detecta personas por webcam y cuenta cuantas cruzan una linea configurable.

Pensado para medir el trafico de visitantes en un stand de feria o evento.

## Como funciona

1. **YOLO** detecta personas en cada frame de la webcam
2. **ByteTrack** asigna un ID unico a cada persona y la sigue entre frames
3. **LineZone** detecta cuando una persona cruza la linea de conteo
4. Se registran **entradas** y **salidas** por separado

## Requisitos

- Python 3.10+
- Webcam

## Instalacion

```bash
# Clonar el repositorio
git clone <url-del-repo>
cd CONTADOR_PERSONAS

# Crear entorno virtual
python -m venv venv

# Activar entorno virtual
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt
```

El modelo YOLO se descarga automaticamente en la primera ejecucion.

## Uso

```bash
# Ejecucion basica (linea horizontal al 50% de la pantalla)
python realtime_detector_personas.py webcam
```

### Opciones

| Opcion           | Default        | Descripcion                                              |
|------------------|----------------|----------------------------------------------------------|
| `--model`        | `yolov8s.pt`   | Modelo YOLO a usar                                       |
| `--camera`       | `0`            | Indice de la camara                                      |
| `--confidence`   | `0.3`          | Umbral de confianza minimo (0.0 a 1.0)                   |
| `--line-pos`     | `0.5`          | Posicion relativa de la linea de conteo (0.0 a 1.0)      |
| `--orientation`  | `horizontal`   | Orientacion de la linea: `horizontal` o `vertical`       |

### Modelos disponibles

| Modelo         | Velocidad | Precision | Recomendado para                |
|----------------|-----------|-----------|----------------------------------|
| `yolov8n.pt`   | Rapido    | Baja      | PCs sin GPU dedicada             |
| `yolov8s.pt`   | Medio     | Media     | Uso general (default)            |
| `yolov8m.pt`   | Lento     | Alta      | Cuando la precision es prioridad |

### Posicion de la linea (`--line-pos`)

Valor entre 0.0 y 1.0 que indica la posicion relativa en la pantalla:

```
Horizontal:  0.0 = arriba     →  1.0 = abajo
Vertical:    0.0 = izquierda  →  1.0 = derecha
```

### Ejemplos

```bash
# Linea horizontal al 70% (mas abajo)
python realtime_detector_personas.py webcam --line-pos 0.7

# Linea vertical para entrada de un stand
python realtime_detector_personas.py webcam --orientation vertical --line-pos 0.4

# Modelo rapido para PC sin GPU + camara externa
python realtime_detector_personas.py webcam --model yolov8n.pt --camera 1

# Mayor confianza para reducir falsos positivos
python realtime_detector_personas.py webcam --confidence 0.5
```

## Controles en vivo

| Tecla | Accion                    |
|-------|---------------------------|
| `q`   | Salir                     |
| `r`   | Reiniciar contadores a 0  |

Al salir se muestra un resumen con el total de entradas y salidas.

## Recomendaciones para el stand

- Colocar la camara apuntando a la **entrada del stand**
- Usar orientacion **vertical** con la linea en el marco de la entrada
- Probar diferentes valores de `--line-pos` hasta que la linea coincida con la entrada
- Si hay mucho movimiento y la PC es lenta, usar `--model yolov8n.pt`
