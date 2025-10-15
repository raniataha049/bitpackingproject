import click, re
from typing import List
from bitpacking.overflow import BitPackerOverflow

def _read_ints_text(path: str) -> List[int]:
    ints: List[int] = []
    # lecture tolérante (UTF-8 et BOM), séparateurs: espace, virgule, point-virgule
    with open(path, "r", encoding="utf-8-sig", errors="ignore") as f:
        for line in f:
            for tok in re.split(r"[,\s;]+", line.strip()):
                if tok:
                    ints.append(int(tok))
    return ints

def _write_ints_one_line(path: str, vals: List[int]) -> None:
    with open(path, "w", encoding="utf-8") as f:
        f.write(" ".join(str(x) for x in vals))

@click.group()
def cli():
    """Overflow BitPacking CLI (indépendant du CLI existant)."""

@cli.command()
@click.option("--input",  "input_path",  required=True, type=click.Path(exists=True))
@click.option("--output", "output_path", required=True, type=click.Path())
def compress(input_path: str, output_path: str):
    """Compresse en mode OVERFLOW et écrit un binaire."""
    vals = _read_ints_text(input_path)
    packer = BitPackerOverflow()
    blob = packer.compress(vals)
    with open(output_path, "wb") as f:
        f.write(blob)
    click.echo(f"OK: {len(vals)} integers -> overflow binary ({len(blob)} bytes)")

@cli.command()
@click.option("--input",  "input_path",  required=True, type=click.Path(exists=True))
@click.option("--output", "output_path", required=True, type=click.Path())
def decompress(input_path: str, output_path: str):
    """Décompresse un binaire OVERFLOW et écrit un txt (une ligne)."""
    with open(input_path, "rb") as f:
        blob = f.read()
    packer = BitPackerOverflow()
    out = packer.decompress(blob)
    _write_ints_one_line(output_path, out)
    click.echo(f"OK: decompressed {len(out)} integers (overflow)")

@cli.command()
@click.option("--input", "input_path", required=True, type=click.Path(exists=True))
@click.option("--index", "index", required=True, type=int)
def get(input_path: str, index: int):
    """Renvoie la valeur à l'indice i directement depuis le binaire OVERFLOW."""
    with open(input_path, "rb") as f:
        blob = f.read()
    packer = BitPackerOverflow()
    val = packer.get(blob, index)
    click.echo(f"{val}")

if __name__ == "__main__":
    cli()
