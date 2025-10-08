import click

@click.group()
def cli():
    """BitPacking CLI"""
    pass

@cli.command()
@click.option("--input", "-i", required=True, help="Input file (plain ints)")
@click.option("--output", "-o", required=True, help="Output binary file")
@click.option("--mode", "-m", default="crossing",
              type=click.Choice(["crossing", "non_crossing"]),
              help="Compression mode")
def compress(input, output, mode):
    """Compress input -> output"""
    click.echo(f"compress: input={input} output={output} mode={mode}")
    # TODO: add compression logic later

@cli.command()
@click.option("--input", "-i", required=True, help="Input binary file")
@click.option("--output", "-o", required=True, help="Output plaintext file")
def decompress(input, output):
    """Decompress input -> output"""
    click.echo(f"decompress: input={input} output={output}")
    # TODO

@cli.command()
@click.option("--input", "-i", required=True, help="Input binary file")
@click.option("--index", "-n", required=True, type=int, help="Index to retrieve")
def get(input, index):
    """Get the i-th integer without full decompression"""
    click.echo(f"get: input={input} index={index}")
    # TODO

if __name__ == "__main__":
    cli()
