#!/usr/bin/env python3
# encoding: utf-8

import os
import shutil
from pathlib import Path
from typing import Annotated

import dotenv
import typer
from typer import Option
from typer.main import Typer

from kernel_builder.config.config import LOGFILE
from kernel_builder.constants import OUTPUT, ROOT, TOOLCHAIN, WORKSPACE
from kernel_builder.kernel_builder import KernelBuilder
from kernel_builder.utils.log import configure_log

app: Typer = typer.Typer(help="GKI Kernel Builder CLI", pretty_exceptions_enable=False)


def _bool_env(var: str, default: bool = False) -> bool:
    return os.getenv(var, str(default)).lower() in ("true", "1", "yes")


@app.command()
def build(
    ksu: Annotated[
        str,
        Option(
            "--ksu",
            "-k",
            envvar="KSU",
            help="KernelSU variant (NONE, OFFICIAL, SUKI, NEXT)",
        ),
    ] = "NONE",
    susfs: Annotated[
        bool,
        Option(
            "--susfs/--no-susfs",
            "-s",
            help="Enable SUSFS support",
        ),
    ] = _bool_env("SUSFS"),
    lxc: Annotated[
        bool,
        Option(
            "--lxc/--no-lxc",
            "-l",
            help="Enable or disable LXC",
        ),
    ] = _bool_env("LXC"),
) -> None:
    if ksu == "NONE" and susfs:
        typer.secho("[ERROR] SUSFS requires KernelSU", err=True, fg=typer.colors.RED)
        raise typer.Exit(1)

    if os.getenv("GITHUB_ACTIONS") != "true":
        dotenv.load_dotenv()

    typer.echo(message=f"Start Build: {ksu=}, {susfs=}, {lxc=}")

    configure_log(logfile=LOGFILE)

    os.environ.update(
        KSU=str(ksu),
        SUSFS=str(susfs).lower(),
        LXC=str(lxc).lower(),
    )

    builder: KernelBuilder = KernelBuilder(ksu, susfs, lxc)
    builder.run_build()


@app.command()
def clean(
    all: Annotated[
        bool,
        typer.Option(
            "--all/--no-all",
            "-a",
            help="Also delete dist/ (output) directory",
        ),
    ] = False,
) -> None:
    targets: list[Path] = [WORKSPACE, TOOLCHAIN]

    if all:
        targets.append(OUTPUT)
    for folder in targets:
        shutil.rmtree(folder, ignore_errors=True)

    (ROOT / "github.env").unlink(missing_ok=True)

    typer.secho("Cleanup completed!", fg=typer.colors.GREEN)


if __name__ == "__main__":
    app()
