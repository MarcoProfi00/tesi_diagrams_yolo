# Per ogni immagine nella cartella di input:
#   1. carica il modello YOLO
#   2. legge metadata/class_terminals_v1.yaml
#   3. seleziona le classi da rilevare
#   4. esegue la detection
#   5. salva un JSON per immagine
#   6. salva un'immagine debug con i bounding box

from pathlib import Path
import json
import yaml
import cv2

from ultralytics import YOLO

# =========================================================
# CONFIGURAZIONE
# =========================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

# === MODELLO ===
MODEL_PATH = (
    PROJECT_ROOT
    / "outputs"
    / "yolo11"
    / "exp11b1_yolo11_rgb_aug_strong_v3"
    / "weights"
    / "best.pt"
)

# === METADATI CLASSI ===
CLASS_TERMINALS_PATH = PROJECT_ROOT / "metadata" / "class_terminals_v1.yaml"

# === INPUT ===
INPUT_IMAGES_DIR = PROJECT_ROOT / "data" / "batch_v3.1_mosfet_transistor"

# === OUTPUT ===
OUTPUT_DIR = PROJECT_ROOT / "outputs" / "topology_v3.1_mosfet_transistor" / "01_detect_components"
DEBUG_IMAGES_DIR = OUTPUT_DIR / "debug_images"

# === PARAMETRI INFERENZA ===
IMG_SIZE = 1024
CONF_THRES = 0.55
IOU_THRES = 0.45

# === DEBUG ===
SAVE_DEBUG_IMAGES = True

IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".bmp", ".tif", ".tiff", ".webp"}


def load_yaml(path: Path):
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def load_class_metadata(class_terminals_path: Path):
    """
    Legge metadata/class_terminals_v1.yaml e restituisce:
    - class_meta: dict {class_id: metadata}
    - detect_class_ids: tutte le classi presenti nello yaml
    - terminal_class_ids: classi con use_for_terminals = true
    - masking_class_ids: classi con use_for_masking = true
    """
    data = load_yaml(class_terminals_path)

    class_meta = {}
    for k, v in data.items():
        class_id = int(k)
        class_meta[class_id] = v

    detect_class_ids = sorted(class_meta.keys())
    terminal_class_ids = sorted([
        cid for cid, meta in class_meta.items()
        if meta.get("use_for_terminals", False)
    ])
    masking_class_ids = sorted([
        cid for cid, meta in class_meta.items()
        if meta.get("use_for_masking", False)
    ])

    return class_meta, detect_class_ids, terminal_class_ids, masking_class_ids


def normalize_model_names(model_names):
    if isinstance(model_names, list):
        return {i: name for i, name in enumerate(model_names)}

    if isinstance(model_names, dict):
        return {int(k): v for k, v in model_names.items()}

    raise TypeError("Formato model.names non riconosciuto.")


def get_input_images():
    if not INPUT_IMAGES_DIR.exists():
        raise FileNotFoundError(f"Cartella immagini non trovata: {INPUT_IMAGES_DIR}")

    images = sorted([
        p for p in INPUT_IMAGES_DIR.iterdir()
        if p.is_file() and p.suffix.lower() in IMAGE_EXTS
    ])

    if not images:
        raise FileNotFoundError(f"Nessuna immagine trovata in: {INPUT_IMAGES_DIR}")

    return images


def draw_components(image_bgr, components):
    out = image_bgr.copy()

    for comp in components:
        x1, y1, x2, y2 = comp["bbox"]
        x1, y1, x2, y2 = map(int, [x1, y1, x2, y2])

        class_id = comp["class_id"]
        class_name = comp["class_name"]
        conf = comp["conf"]

        if comp.get("use_for_terminals", False):
            suffix = "T"
        elif comp.get("use_for_masking", False):
            suffix = "M"
        else:
            suffix = "-"

        label = f"{class_id} | {class_name} | {conf:.2f} | {suffix}"

        cv2.rectangle(out, (x1, y1), (x2, y2), (0, 255, 0), 2)
        cv2.putText(
            out,
            label,
            (x1, max(y1 - 8, 0)),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.50,
            (0, 255, 0),
            2,
            cv2.LINE_AA
        )

    return out


def predict_components_on_image(
    image_path: Path,
    model,
    detect_class_ids,
    model_names,
    class_meta
):
    image_bgr = cv2.imread(str(image_path))
    if image_bgr is None:
        raise ValueError(f"Impossibile leggere l'immagine: {image_path}")

    image_h, image_w = image_bgr.shape[:2]

    results = model.predict(
        source=str(image_path),
        imgsz=IMG_SIZE,
        conf=CONF_THRES,
        iou=IOU_THRES,
        classes=detect_class_ids,
        verbose=False
    )

    result = results[0]
    components = []

    if result.boxes is not None and len(result.boxes) > 0:
        xyxy = result.boxes.xyxy.cpu().numpy()
        cls = result.boxes.cls.cpu().numpy()
        confs = result.boxes.conf.cpu().numpy()

        for box, class_id, conf in zip(xyxy, cls, confs):
            x1, y1, x2, y2 = box
            class_id = int(class_id)

            meta = class_meta.get(class_id, {})

            components.append({
                "class_id": class_id,
                "class_name": model_names.get(class_id, f"class_{class_id}"),
                "conf": round(float(conf), 4),
                "bbox": [
                    round(float(x1), 2),
                    round(float(y1), 2),
                    round(float(x2), 2),
                    round(float(y2), 2),
                ],
                "symbol_type": meta.get("symbol_type"),
                "use_for_terminals": meta.get("use_for_terminals", False),
                "use_for_masking": meta.get("use_for_masking", False),
            })

    output_data = {
        "image_id": image_path.stem,
        "image_name": image_path.name,
        "image_path": str(image_path),
        "image_width": image_w,
        "image_height": image_h,
        "detect_class_ids": detect_class_ids,
        "terminal_class_ids": sorted([
            cid for cid, meta in class_meta.items()
            if meta.get("use_for_terminals", False)
        ]),
        "masking_class_ids": sorted([
            cid for cid, meta in class_meta.items()
            if meta.get("use_for_masking", False)
        ]),
        "components": components
    }

    return image_bgr, output_data


def main() -> None:
    if not MODEL_PATH.exists():
        raise FileNotFoundError(f"Modello non trovato: {MODEL_PATH}")

    if not CLASS_TERMINALS_PATH.exists():
        raise FileNotFoundError(f"class_terminals_v1.yaml non trovato: {CLASS_TERMINALS_PATH}")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    DEBUG_IMAGES_DIR.mkdir(parents=True, exist_ok=True)

    class_meta, detect_class_ids, terminal_class_ids, masking_class_ids = load_class_metadata(
        CLASS_TERMINALS_PATH
    )

    print(f"PROJECT_ROOT         : {PROJECT_ROOT}")
    print(f"MODEL_PATH           : {MODEL_PATH}")
    print(f"CLASS_TERMINALS_PATH : {CLASS_TERMINALS_PATH}")
    print(f"INPUT_IMAGES_DIR     : {INPUT_IMAGES_DIR}")
    print(f"OUTPUT_DIR           : {OUTPUT_DIR}")
    print(f"DETECT_CLASS_IDS     : {detect_class_ids}")
    print(f"TERMINAL_CLASS_IDS   : {terminal_class_ids}")
    print(f"MASKING_CLASS_IDS    : {masking_class_ids}\n")

    model = YOLO(str(MODEL_PATH))
    model_names = normalize_model_names(model.names)

    print("Mapping classi selezionate:")
    for class_id in detect_class_ids:
        yaml_name = class_meta[class_id].get("name", "")
        model_name = model_names.get(class_id, "")
        print(
            f"  {class_id}: yaml='{yaml_name}' | model='{model_name}' | "
            f"terminals={class_meta[class_id].get('use_for_terminals', False)} | "
            f"masking={class_meta[class_id].get('use_for_masking', False)}"
        )
    print()

    input_images = get_input_images()
    print(f"Numero immagini da processare: {len(input_images)}\n")

    for idx, image_path in enumerate(input_images, start=1):
        image_bgr, output_data = predict_components_on_image(
            image_path=image_path,
            model=model,
            detect_class_ids=detect_class_ids,
            model_names=model_names,
            class_meta=class_meta
        )

        out_json_path = OUTPUT_DIR / f"{image_path.stem}.json"
        with open(out_json_path, "w", encoding="utf-8") as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)

        if SAVE_DEBUG_IMAGES:
            debug_img = draw_components(image_bgr, output_data["components"])
            debug_img_path = DEBUG_IMAGES_DIR / f"{image_path.stem}_detect.jpg"
            cv2.imwrite(str(debug_img_path), debug_img)

        print(
            f"[{idx}/{len(input_images)}] "
            f"{image_path.name} -> {len(output_data['components'])} componenti"
        )

    print("\nCompletato.")
    print(f"JSON salvati in: {OUTPUT_DIR}")
    if SAVE_DEBUG_IMAGES:
        print(f"Immagini debug salvate in: {DEBUG_IMAGES_DIR}")


if __name__ == "__main__":
    main()