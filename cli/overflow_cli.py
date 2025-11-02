import click, re
from typing import List
from bitpacking.overflow import BitPackerOverflow
from pathlib import Path

def _read_ints_text(path: str) -> List[int]:
    ints: List[int] = []
   
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
@click.option("--input", "input", required=True)
@click.option("--index", "index", required=True, type=int)
def get(input, index):
    """Renvoie la valeur à l'indice i directement depuis le fichier overflow."""
    from pathlib import Path
    from bitpacking.overflow import BitPackerOverflow

    # Lire le fichier binaire
    blob = Path(input).read_bytes()

    # Créer une instance du packer et lui assigner le blob
    packer = BitPackerOverflow()
    packer.blob = blob  

    
    val = packer.get(index)

    print(val)

if __name__ == "__main__":
    cli()
