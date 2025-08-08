import os
import re
import sys
from os import cpu_count
from pathlib import Path

from sh import make

from kernel_builder.config.config import BUILD_HOST, BUILD_USER, DEFCONFIG, IMAGE_COMP
from kernel_builder.constants import (
    CLANG_TRIPLE,
    CROSS_COMPILE,
    LLVM,
    LLVM_IAS,
    LTO_CLANG_FULL,
    LTO_CLANG_THIN,
    TOOLCHAIN,
    WORKSPACE,
)
from kernel_builder.pre_build.configurator import configurator
from kernel_builder.utils.fs import FileSystem
from kernel_builder.utils.log import log


class Builder:
    def __init__(self) -> None:
        self.fs: FileSystem = FileSystem()
        self.clang_bin: Path = TOOLCHAIN / "clang" / "bin"
        self.workspace: Path = WORKSPACE
        self.defconfig: str = DEFCONFIG
        self.image_comp: str = IMAGE_COMP
        self.jobs: int = cpu_count() or 1

        overrides = {
            "ARCH": "arm64",
            "SUBARCH": "arm64",
            "KBUILD_BUILD_USER": BUILD_USER,
            "KBUILD_BUILD_HOST": BUILD_HOST,
            "PATH": f"{self.clang_bin}{os.pathsep}{os.getenv('PATH', '')}",
            "CC": "ccache clang",
            "CXX": "ccache clang++",
            "CLANG_TRIPLE": CLANG_TRIPLE,
            "CROSS_COMPILE": CROSS_COMPILE,
            "LLVM": LLVM,
            "LLVM_IAS": LLVM_IAS,
            "CONFIG_LTO_CLANG_THIN": LTO_CLANG_THIN,
            "CONFIG_LTO_CLANG_FULL": LTO_CLANG_FULL,
            "LD": str(self.clang_bin / "ld.lld"),
        }
        self.make_env: dict[str, str] = {**os.environ, **overrides}

    def _make(
        self, args: list[str] | None = None, *, jobs: int, out: str | Path
    ) -> None:
        make(
            f"-j{jobs}",
            *(args or []),
            f"O={out}",
            _cwd=Path.cwd(),
            _env={**self.make_env},
            _out=sys.stdout,
            _err=sys.stderr,
        )

    def build(
        self,
        jobs: int | None = None,
        *,
        out: str | Path = "out",
    ) -> None:
        target: str = (
            "Image" if self.image_comp == "raw" else f"Image.{self.image_comp}"
        )
        jobs = jobs or self.jobs
        log(
            f"Start build: {self.defconfig=}, {out=}, {jobs or self.jobs=}, {self.image_comp=}"
        )
        self._make([self.defconfig], jobs=jobs, out=out)

        configurator()

        log("Making olddefconfig")
        self._make(["olddefconfig"], jobs=jobs, out=out)

        log("Defconfig completed. Starting full build.")
        self._make([target, "modules"], jobs=jobs, out=out)
        log("Build completed successfully.")

    def get_kernel_version(self) -> str:
        log("Fetching kernel version...")
        makefile: str = (self.workspace / "Makefile").read_text()
        version = re.findall(
            r"^(?:VERSION|PATCHLEVEL|SUBLEVEL)\s*=\s*(\d+)$", makefile, re.MULTILINE
        )
        assert version, "Unable to determine kernel version"
        return ".".join(version[:3])


if __name__ == "__main__":
    raise SystemExit("This file is meant to be imported, not executed.")
