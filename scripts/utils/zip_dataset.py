from pathlib import Path
import zipfile

# =========================================================
# CONFIGURAZIONE
# =========================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

SRC_DATASET = PROJECT_ROOT / "data" / "dataset_v3" / "rf_yolo_1024_gray"
OUT_ZIP = PROJECT_ROOT / "data" / "dataset_v3" / "rf_yolo_1024_gray.zip"


def main() -> None:
    if not SRC_DATASET.exists():
        raise FileNotFoundError(f"Dataset non trovato: {SRC_DATASET}")

    if OUT_ZIP.exists():
        print(f"Il file zip esiste già e verrà sovrascritto: {OUT_ZIP}")
        OUT_ZIP.unlink()

    files = [p for p in SRC_DATASET.rglob("*") if p.is_file()]
    print(f"Cartella sorgente : {SRC_DATASET}")
    print(f"Zip destinazione  : {OUT_ZIP}")
    print(f"File da comprimere: {len(files)}\n")

    with zipfile.ZipFile(OUT_ZIP, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for i, file_path in enumerate(files, start=1):
            # Mantiene la cartella principale dentro lo zip
            arcname = file_path.relative_to(SRC_DATASET.parent)
            zf.write(file_path, arcname=arcname)

            if i % 200 == 0 or i == len(files):
                print(f"Compressi {i}/{len(files)} file...")

    size_mb = OUT_ZIP.stat().st_size / (1024 * 1024)
    print("\nZip completato.")
    print(f"Creato: {OUT_ZIP}")
    print(f"Dimensione: {size_mb:.2f} MB")


if __name__ == "__main__":
    main()