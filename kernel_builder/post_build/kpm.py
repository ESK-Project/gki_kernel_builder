import gzip
import shutil
from pathlib import Path

import lz4.frame
from sh import Command, chmod

from kernel_builder.config.config import IMAGE_COMP
from kernel_builder.constants import WORKSPACE
from kernel_builder.utils.command import curl
from kernel_builder.utils.fs import FileSystem
from kernel_builder.utils.github import GithubAPI
from kernel_builder.utils.log import log


class KPMPatcher:
    def __init__(self, ksu: str) -> None:
        self.fs: FileSystem = FileSystem()
        self.gh = GithubAPI()
        self.image_comp: str = IMAGE_COMP
        self.ksu: str = ksu

    def _open(self, path: Path, mode: str):
        if self.image_comp == "gz":
            return gzip.open(path, mode)
        if self.image_comp == "lz4":
            return lz4.frame.open(path, mode)
        return path.open(mode)

    def patch(self) -> None:
        if self.ksu != "SUKI":
            return

        log("Patching KPM for SukiSU variant")
        cwd: Path = Path.cwd()
        temp: Path = cwd / "kpm_patch"
        self.fs.reset_path(temp)
        image: str = "Image" if self.image_comp == "raw" else f"Image.{self.image_comp}"
        image_path: Path = WORKSPACE / "out" / "arch" / "arm64" / "boot" / image
        decompressed: Path = temp / "Image"
        temp_img: Path = temp / image
        kpm_patcher_path: Path = temp / "patcher"

        try:
            self.fs.cd(temp)

            latest_kpm_patcher: str = self.gh.fetch_latest_download_url(
                "https://api.github.com/repos/SukiSU-Ultra/SukiSU_KernelPatch_patch/releases/latest",
                "patch_linux",
            )
            curl("-o", str(kpm_patcher_path), latest_kpm_patcher)
            chmod("a+x", str(kpm_patcher_path))
            patcher: Command = Command(kpm_patcher_path)

            shutil.move(image_path, temp_img)
            if self.image_comp == "raw":
                shutil.copy(temp_img, decompressed)
            else:
                with (
                    self._open(temp_img, "rb") as fsrc,
                    decompressed.open("wb") as fdst,
                ):
                    shutil.copyfileobj(fsrc, fdst)

            patcher()

            patched: Path = temp / "oImage"
            if not patched.exists():
                log(f"Patched image not found at {patched}", "error")
                return

            temp_img.unlink(missing_ok=True)
            image_path.unlink(missing_ok=True)

            if self.image_comp == "raw":
                shutil.copy(patched, temp_img)
            else:
                with patched.open("rb") as fsrc, self._open(temp_img, "wb") as fdst:
                    shutil.copyfileobj(fsrc, fdst)
            shutil.move(temp_img, image_path)

            log("KPM patch applied successfully")

        except Exception as e:
            log(f"Error during patching: {e}", "error")
            return

        finally:
            self.fs.cd(cwd)


if __name__ == "__main__":
    raise SystemExit("This file is meant to be imported, not executed.")
