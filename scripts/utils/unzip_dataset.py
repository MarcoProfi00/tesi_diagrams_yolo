import argparse
from pathlib import Path
import zipfile

# =========================================================
# CONFIGURAZIONE
# =========================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATASET_ROOT = PROJECT_ROOT / "data" / "datasets" / "dataset_v3"

SRC_ZIP = DATASET_ROOT / "rf_yolo_1024_rgb.zip"
OUT_DIR = DATASET_ROOT / SRC_ZIP.stem
EXPECTED_TOP_LEVEL = {"data.yaml", "train", "valid", "test"}


def validate_members(
    members: list[zipfile.ZipInfo],
    output_directory: Path = OUT_DIR,
) -> Path:
    """Rifiuta path pericolosi e controlla il layout atteso del dataset."""
    output_root = output_directory.resolve()
    normalized_parts: list[tuple[str, ...]] = []
    top_level: set[str] = set()
    for member in members:
        normalized_name = member.filename.replace("\\", "/")
        member_path = Path(normalized_name)
        if member_path.parts:
            top_level.add(member_path.parts[0])
            normalized_parts.append(member_path.parts)
        try:
            (output_directory / member_path).resolve().relative_to(output_root)
        except ValueError as error:
            raise ValueError(f"Path non sicuro nello ZIP: {member.filename!r}") from error

        unix_mode = member.external_attr >> 16
        if unix_mode & 0o170000 == 0o120000:
            raise ValueError(f"Link simbolico non ammesso nello ZIP: {member.filename!r}")

    if EXPECTED_TOP_LEVEL <= top_level:
        return Path()

    if len(top_level) == 1:
        wrapper = next(iter(top_level))
        nested_top_level = {
            parts[1] for parts in normalized_parts if len(parts) >= 2 and parts[0] == wrapper
        }
        if EXPECTED_TOP_LEVEL <= nested_top_level:
            return Path(wrapper)

    raise ValueError(
        "Layout ZIP inatteso: servono data.yaml, train, valid e test alla "
        "radice oppure dentro un'unica cartella."
    )


def resolve_cli_path(raw_path: str | Path) -> Path:
    """Risolve i path CLI relativi alla root del repository."""
    path = Path(raw_path).expanduser()
    if not path.is_absolute():
        path = PROJECT_ROOT / path
    return path.resolve()


def infer_output_directory(archive_path: Path, layout_prefix: Path) -> Path:
    """Evita una doppia cartella quando lo ZIP contiene gia' il proprio wrapper."""
    if layout_prefix.parts:
        return archive_path.parent
    return archive_path.with_suffix("")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Valida ed estrae un dataset YOLO nella cartella attesa dagli script."
    )
    parser.add_argument(
        "--archive",
        default=SRC_ZIP.relative_to(PROJECT_ROOT).as_posix(),
        help="ZIP relativo alla root del repository o path assoluto.",
    )
    parser.add_argument(
        "--output",
        default=None,
        help="Root di estrazione esplicita; per default viene dedotta dal layout ZIP.",
    )
    parser.add_argument(
        "--check-only",
        action="store_true",
        help="Valida archivio e struttura senza estrarre alcun file.",
    )
    return parser


def main(argv: list[str] | None = None) -> None:
    args = build_parser().parse_args(argv)
    source_zip = resolve_cli_path(args.archive)
    if not source_zip.exists():
        raise FileNotFoundError(f"File zip non trovato: {source_zip}")

    with zipfile.ZipFile(source_zip, "r") as zf:
        members = zf.infolist()
        provisional_output = (
            resolve_cli_path(args.output) if args.output else source_zip.parent
        )
        layout_prefix = validate_members(members, provisional_output)
        output_directory = (
            resolve_cli_path(args.output)
            if args.output
            else infer_output_directory(source_zip, layout_prefix)
        )
        validate_members(members, output_directory)

        print(f"Zip sorgente      : {source_zip}")
        print(f"Cartella destinaz.: {output_directory}")
        print(f"Elementi validati: {len(members)}")

        if args.check_only:
            print("Archivio e layout validi; nessun file estratto.")
            return

        output_directory.mkdir(parents=True, exist_ok=True)
        print(f"Elementi da estrarre: {len(members)}\n")

        for i, member in enumerate(members, start=1):
            zf.extract(member, path=output_directory)

            if i % 200 == 0 or i == len(members):
                print(f"Estratti {i}/{len(members)} elementi...")

    print("\nEstrazione completata.")
    print(f"Contenuto estratto in: {output_directory}")


if __name__ == "__main__":
    main()
