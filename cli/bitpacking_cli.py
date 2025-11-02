import click
import re
from typing import List

from bitpacking.factory import (
    CompressorFactory, save_binary, load_binary
)
from bitpacking.crossing import BitPackingCrossing
from bitpacking.noncrossing import BitPackingNonCrossing


def _read_ints_text(path: str) -> List[int]:
    ints: List[int] = []
   
    with open(path, "r", encoding="utf-8-sig") as f:
        for line in f:
            
            tokens = re.split(r"[,\s;]+", line.strip())
            for tok in tokens:
                if tok == "":
                    continue
                ints.append(int(tok))
    return ints


def _write_ints_text(path: str, ints: List[int]) -> None:
    with open(path, "w", encoding="utf-8") as f:
        f.write(" ".join(str(x) for x in ints))


@click.group()
def cli():
    """BitPacking CLI"""
    pass


@cli.command()
@click.option("--input", "-i", required=True, help="Input file (plaintext integers)")
@click.option("--output", "-o", required=True, help="Output binary file (.bin)")
@click.option("--mode", "-m", default="crossing",
              type=click.Choice(["crossing", "non_crossing"]),
              help="Compression mode")
def compress(input, output, mode):
   
    ints = _read_ints_text(input)
    comp = CompressorFactory.create_from_list(mode, ints)
    save_binary(output, mode, comp.k, comp.n, comp.words)
    click.echo(f"OK: {comp.n} integers -> {len(comp.words)} words (k={comp.k}, mode={mode})")


@cli.command()
@click.option("--input", "-i", required=True, help="Input binary file (.bin)")
@click.option("--output", "-o", required=True, help="Output plaintext file")
def decompress(input, output):
    
    mode, k, n, words = load_binary(input)
    if mode == "crossing":
        comp = CompressorFactory.from_packed_crossing(k, n, words)
    elif mode == "non_crossing":
        comp = CompressorFactory.from_packed_noncross(k, n, words)
    else:
        raise click.ClickException(f"Unknown mode in file: {mode}")
    ints = comp.to_list()
    if len(ints) != n:
        raise click.ClickException("Decompressed length mismatch")
    _write_ints_text(output, ints)
    click.echo(f"OK: decompressed {n} integers (reconstructed mode: k={k}, mode={mode})")


@cli.command()
@click.option("--input", "-i", required=True, help="Input binary file (.bin)")
@click.option("--index", "-n", "index", required=True, type=int, help="Index to retrieve (0-based)")
def get(input, index):
    
    mode, k, n, words = load_binary(input)
    if index < 0 or index >= n:
        raise click.ClickException("Index out of range")

    if mode == "crossing":
        comp = CompressorFactory.from_packed_crossing(k, n, words)
    elif mode == "non_crossing":
        comp = CompressorFactory.from_packed_noncross(k, n, words)
    else:
        raise click.ClickException(f"Unknown mode in file: {mode}")

    val = comp.get(index)
    click.echo(str(val))


if __name__ == "__main__":
    cli()
