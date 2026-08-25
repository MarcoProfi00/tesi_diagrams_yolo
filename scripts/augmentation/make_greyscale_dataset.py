from pathlib import Path
from PIL import Image
import shutil

# =========================================================
# CONFIGURAZIONE
# =========================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATASET_ROOT = PROJECT_ROOT / "data" / "datasets" / "dataset_v3"

SRC_DATASET = DATASET_ROOT / "rf_yolo_1024_rgb"
DST_DATASET = DATASET_ROOT / "rf_yolo_1024_gray"

IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".bmp", ".tif", ".tiff", ".webp"}


def is_image_file(path: Path) -> bool:
    return path.suffix.lower() in IMAGE_EXTS

#Converte un'img in greyscale e la salva mantenendo lo stesso nome
def convert_image_to_grayscale(src_path: Path, dst_path: Path) -> None:
    dst_path.parent.mkdir(parents=True, exist_ok=True)

    with Image.open(src_path) as img:
        gray = img.convert("L")  # grayscale
        gray.save(dst_path)

#Copia il file non immagine senza modificarli
def copy_non_image_file(src_path: Path, dst_path: Path) -> None:
    dst_path.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src_path, dst_path)


def main() -> None:
    if not SRC_DATASET.exists():
        raise FileNotFoundError(f"Dataset sorgente non trovato: {SRC_DATASET}")

    if DST_DATASET.exists():
        raise FileExistsError(
            f"La cartella di destinazione esiste già: {DST_DATASET}\n"
            f"Rinominala o cancellala prima di rilanciare lo script."
        )

    print(f"Dataset sorgente : {SRC_DATASET}")
    print(f"Dataset destinaz.: {DST_DATASET}")
    print("Avvio conversione in grayscale...\n")

    total_files = 0
    converted_images = 0
    copied_files = 0

    for src_path in SRC_DATASET.rglob("*"):
        if src_path.is_dir():
            continue

        rel_path = src_path.relative_to(SRC_DATASET)
        dst_path = DST_DATASET / rel_path
        total_files += 1

        # Converti SOLO le immagini che stanno dentro cartelle "images"
        # Le label e gli altri file vengono copiati uguali.
        if is_image_file(src_path) and "images" in src_path.parts:
            convert_image_to_grayscale(src_path, dst_path)
            converted_images += 1
        else:
            copy_non_image_file(src_path, dst_path)
            copied_files += 1

    print("Conversione completata.\n")
    print(f"File totali elaborati : {total_files}")
    print(f"Immagini convertite   : {converted_images}")
    print(f"File copiati          : {copied_files}")
    print(f"\nNuovo dataset creato in:\n{DST_DATASET}")


if __name__ == "__main__":
    main()
