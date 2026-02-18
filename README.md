# Contador de Personas en Tiempo Real

Sistema de conteo de personas en tiempo real con interfaz grafica (Tkinter). Usa YOLO + ByteTrack para detectar personas por webcam y contar cuantas cruzan una linea configurable.

Pensado para medir el trafico de visitantes en un stand de feria o evento durante sesiones prolongadas (8-10 horas).

## Como funciona

1. **YOLO** detecta personas en cada frame de la webcam
2. **ByteTrack** asigna un ID unico a cada persona y la sigue entre frames
3. **LineZone** detecta cuando una persona cruza la linea de conteo
4. Se registran **entradas** y **salidas** por separado
5. Los datos se guardan automaticamente en **CSV** cada 5 minutos

## Interfaz

```
+----------------------------------------------+
|  Contador de Personas - Stand Feria          |
+---------------------------+------------------+
|                           | ENTRADAS:  42    |
|                           | SALIDAS:   38    |
|    VIDEO FEED             | EN CUADRO:  3    |
|    (640x480)              | FPS: 25.3        |
|    con linea y boxes      |------------------|
|                           | [Iniciar]        |
|                           | [Detener]        |
|                           | [Reiniciar]      |
|                           | [Exportar CSV]   |
|                           |------------------|
|                           | Camara: [0]      |
|                           | Confianza: ===o  |
|                           | Pos. linea: ==o  |
|                           | Orien: (H) (V)  |
|                           |------------------|
|                           | Trafico por hora |
|                           | ## ## #### ##    |
+---------------------------+------------------+
```

## Requisitos

- Python 3.10+
- Webcam
- GPU con CUDA (recomendado, no obligatorio)

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
python realtime_detector_personas.py
```

Se abre la ventana de la aplicacion. Click en **Iniciar** para comenzar la deteccion.

## Controles de la GUI

| Control | Funcion |
|---------|---------|
| Iniciar | Arranca captura de video y deteccion |
| Detener | Pausa la deteccion |
| Reiniciar contadores | Pone conteos en 0, nuevo tracker |
| Exportar CSV | Guarda archivo CSV con dialogo de ubicacion |
| Slider confianza | 0.1 a 0.9, se actualiza en vivo |
| Slider posicion linea | 0.0 a 1.0, se actualiza en vivo |
| Orientacion | Horizontal / Vertical |
| Selector camara | Indices 0-4 para seleccionar camara |

## Datos CSV

Se genera automaticamente un archivo `conteo_YYYY-MM-DD.csv` con las columnas:

| Columna | Descripcion |
|---------|-------------|
| `hora` | Hora del registro (HH:MM) |
| `entradas_intervalo` | Entradas en los ultimos 15 min |
| `salidas_intervalo` | Salidas en los ultimos 15 min |
| `entradas_total` | Entradas acumuladas |
| `salidas_total` | Salidas acumuladas |

- Se registra una fila cada 15 minutos
- Auto-guardado cada 5 minutos
- Guardado automatico al cerrar la aplicacion
- Exportacion manual con el boton "Exportar CSV"

## Estabilidad para uso prolongado

- **Reconexion automatica de camara**: Si la camara se desconecta, reintenta cada 3 segundos y muestra un aviso en pantalla
- **Reset periodico del tracker**: Cada 30 minutos se limpia ByteTrack para evitar acumulacion de memoria (los conteos se preservan)
- **Auto-guardado**: Snapshot CSV cada 5 minutos por si se cierra la app inesperadamente
- **Cierre limpio**: Al cerrar la ventana se guardan los datos automaticamente
- **Logging**: Errores y eventos se registran en `contador.log`

## Modelos disponibles

| Modelo | Velocidad | Precision | Recomendado para |
|--------|-----------|-----------|------------------|
| `yolov8n.pt` | Rapido | Baja | PCs sin GPU dedicada |
| `yolov8s.pt` | Medio | Media | Uso general (default) |
| `yolov8m.pt` | Lento | Alta | Cuando la precision es prioridad |

Para cambiar el modelo, editar la constante en el codigo (`model_name` en `PersonCounter`).

## Recomendaciones para el stand

- Colocar la camara apuntando a la **entrada del stand**
- Usar orientacion **vertical** con la linea en el marco de la entrada
- Ajustar el slider de posicion de linea hasta que coincida con la entrada
- Si hay mucho movimiento y la PC es lenta, editar el modelo a `yolov8n.pt`
- Dejar la aplicacion corriendo todo el dia; el CSV se guarda solo
