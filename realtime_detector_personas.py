import cv2
import numpy as np
import supervision as sv
from ultralytics import YOLO
import typer
import time
from collections import deque

app = typer.Typer()

PERSON_CLASS_ID = 0


def process_webcam(
    model_name: str,
    camera_index: int,
    confidence: float,
    line_position: float,
    line_orientation: str,
):
    """Proceso principal de deteccion, tracking y conteo por cruce de linea."""
    model = YOLO(model_name)
    cap = cv2.VideoCapture(camera_index)

    if not cap.isOpened():
        print("Error: No se pudo abrir la camara.")
        return

    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    # Definir la linea de conteo segun orientacion y posicion relativa
    if line_orientation == "horizontal":
        line_y = int(frame_height * line_position)
        line_start = sv.Point(0, line_y)
        line_end = sv.Point(frame_width, line_y)
    else:
        line_x = int(frame_width * line_position)
        line_start = sv.Point(line_x, 0)
        line_end = sv.Point(line_x, frame_height)

    # Tracker para asignar IDs unicos a cada persona
    tracker = sv.ByteTrack(
        track_activation_threshold=confidence,
        minimum_matching_threshold=0.8,
        frame_rate=30,
    )

    # Zona de linea para conteo de cruces
    line_zone = sv.LineZone(start=line_start, end=line_end)

    # Anotadores visuales
    box_annotator = sv.BoxAnnotator(thickness=2)
    label_annotator = sv.LabelAnnotator(text_thickness=1, text_scale=0.5)
    trace_annotator = sv.TraceAnnotator(thickness=2, trace_length=60)
    line_annotator = sv.LineZoneAnnotator(thickness=2, text_thickness=2, text_scale=1)

    fps_buffer = deque(maxlen=30)

    print("\n  Controles:")
    print("    q - Salir")
    print("    r - Reiniciar contadores\n")

    while True:
        t_start = time.perf_counter()

        ret, frame = cap.read()
        if not ret:
            break

        # Detectar solo personas con el umbral de confianza
        results = model(
            frame, classes=[PERSON_CLASS_ID], conf=confidence, verbose=False
        )[0]
        detections = sv.Detections.from_ultralytics(results)

        # Asignar IDs con el tracker
        detections = tracker.update_with_detections(detections)

        # Evaluar cruce de linea
        line_zone.trigger(detections=detections)

        # Generar etiquetas con ID de tracking y confianza
        labels = [
            f"#{tid} {conf:.0%}"
            for tid, conf in zip(detections.tracker_id, detections.confidence)
        ]

        # Dibujar anotaciones
        frame = trace_annotator.annotate(scene=frame, detections=detections)
        frame = box_annotator.annotate(scene=frame, detections=detections)
        frame = label_annotator.annotate(
            scene=frame, detections=detections, labels=labels
        )
        frame = line_annotator.annotate(frame=frame, line_counter=line_zone)

        # Calcular FPS promedio
        elapsed = time.perf_counter() - t_start
        fps_buffer.append(1.0 / elapsed if elapsed > 0 else 0)
        avg_fps = sum(fps_buffer) / len(fps_buffer)

        # Panel de informacion
        panel_h = 140
        overlay = frame[:panel_h, :260].copy()
        cv2.rectangle(frame, (0, 0), (260, panel_h), (0, 0, 0), -1)
        cv2.addWeighted(overlay, 0.3, frame[:panel_h, :260], 0.7, 0, frame[:panel_h, :260])

        info_lines = [
            (f"FPS: {avg_fps:.1f}", (0, 255, 0)),
            (f"Entradas: {line_zone.in_count}", (0, 255, 0)),
            (f"Salidas:  {line_zone.out_count}", (0, 100, 255)),
            (f"Personas en cuadro: {len(detections)}", (255, 255, 0)),
        ]
        for i, (text, color) in enumerate(info_lines):
            cv2.putText(
                frame, text, (10, 28 + i * 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.65, color, 2,
            )

        cv2.imshow("Contador de Personas - Stand Feria", frame)

        key = cv2.waitKey(1) & 0xFF
        if key == ord("q"):
            break
        elif key == ord("r"):
            line_zone = sv.LineZone(start=line_start, end=line_end)
            tracker = sv.ByteTrack(
                track_activation_threshold=confidence,
                minimum_matching_threshold=0.8,
                frame_rate=30,
            )
            print("Contadores reiniciados.")

    # Resumen final
    print(f"\n{'='*35}")
    print(f"  RESUMEN FINAL")
    print(f"{'='*35}")
    print(f"  Entradas totales: {line_zone.in_count}")
    print(f"  Salidas totales:  {line_zone.out_count}")
    print(f"{'='*35}\n")

    cap.release()
    cv2.destroyAllWindows()


@app.command()
def webcam(
    model: str = typer.Option(
        "yolov8s.pt", help="Modelo YOLO (yolov8n.pt=rapido, yolov8s.pt=balanceado, yolov8m.pt=preciso)"
    ),
    camera: int = typer.Option(0, help="Indice de la camara"),
    confidence: float = typer.Option(0.3, help="Umbral de confianza (0.0 a 1.0)"),
    line_pos: float = typer.Option(0.7, help="Posicion relativa de la linea de conteo (0.0 a 1.0)"),
    orientation: str = typer.Option(
        "horizontal", help="Orientacion de la linea: horizontal o vertical"
    ),
):
    """Contador de personas en tiempo real para stand de feria.

    Cuenta personas que cruzan una linea configurable usando deteccion YOLO
    y tracking ByteTrack. Ideal para medir el trafico en un stand.
    """
    typer.echo(f"Modelo: {model} | Camara: {camera} | Confianza: {confidence}")
    typer.echo(f"Linea: {orientation} en posicion {line_pos}")
    typer.echo("Iniciando contador de personas...")
    process_webcam(
        model_name=model,
        camera_index=camera,
        confidence=confidence,
        line_position=line_pos,
        line_orientation=orientation,
    )


if __name__ == "__main__":
    app()
