from pathlib import Path
import zipfile

# =========================================================
# CONFIGURAZIONE
# =========================================================

PROJECT_ROOT = Path(__file__).resolve().parents[1]

SRC_ZIP = PROJECT_ROOT / "data" / "dataset_v3" / "rf_yolo_1024_rgb.zip"
OUT_DIR = PROJECT_ROOT / "data" / "dataset_v3"


def main() -> None:
    if not SRC_ZIP.exists():
        raise FileNotFoundError(f"File zip non trovato: {SRC_ZIP}")

    print(f"Zip sorgente      : {SRC_ZIP}")
    print(f"Cartella destinaz.: {OUT_DIR}")

    with zipfile.ZipFile(SRC_ZIP, "r") as zf:
        members = zf.infolist()
        print(f"Elementi da estrarre: {len(members)}\n")

        for i, member in enumerate(members, start=1):
            zf.extract(member, path=OUT_DIR)

            if i % 200 == 0 or i == len(members):
                print(f"Estratti {i}/{len(members)} elementi...")

    print("\nEstrazione completata.")
    print(f"Contenuto estratto in: {OUT_DIR}")


if __name__ == "__main__":
    main()