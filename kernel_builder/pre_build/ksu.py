import os
import shutil
import subprocess
from pathlib import Path

from kernel_builder.constants import PATCHES, WORKSPACE
from kernel_builder.utils.command import apply_patch
from kernel_builder.utils.github import GithubAPI
from kernel_builder.utils.log import log
from kernel_builder.utils.source import SourceManager


class KSUInstaller:
    MANUAL_HOOK_UNSUPPORTED: list[str] = ["NONE", "OFFICIAL"]
    KNOWN_KSU_DRIVER_PATHS: list[Path] = [
        WORKSPACE / "drivers" / "kernelsu",
        WORKSPACE / "drivers" / "staging" / "kernelsu",
    ]

    def __init__(self, ksu: str, susfs: bool) -> None:
        self.source: SourceManager = SourceManager()
        self.gh_api: GithubAPI = GithubAPI()
        self.variant: str = ksu
        self.use_susfs: bool = susfs

    def _install_ksu(self, url: str, ref: str | None) -> None:
        # Normalize URL format
        if not self.source.is_simplified(url):
            url = self.source.git_simplifier(url)

        # Fetch latest tag
        if "KernelSU-Next" in url:
            user, repo = "KernelSU-Next", "KernelSU-Next"
        else:
            user, repo = url.split(":", 1)[1].split("/", 1)
        latest_tag: str = self._fetch_latest_tag(user, repo)
        ref = ref or latest_tag

        # Expose latest KernelSU version to environment
        os.environ["KSU_VERSION"] = latest_tag

        # Cleaning up drivers
        self._clean_driver()

        # Setup KernelSU
        log(f"Installing KernelSU from {url} | {ref}")
        self._run_setup(url, ref)

        # Setup manual hooks
        self._patch_manual_hooks()

    def _fetch_latest_tag(self, user: str, repo: str) -> str:
        api_url: str = f"https://api.github.com/repos/{user}/{repo}/releases/latest"
        return self.gh_api.fetch_latest_tag(api_url)

    def _run_setup(self, url: str, ref: str) -> None:
        setup_url: str = f"https://raw.githubusercontent.com/{url.split(':', 1)[1]}/{ref}/kernel/setup.sh"

        # Fetch setup script
        script: subprocess.CompletedProcess[bytes] = subprocess.run(
            ["curl", "-LSs", setup_url],
            capture_output=True,
            check=True,
        )

        # Execute setup script
        subprocess.run(
            ["bash", "-s", ref], input=script.stdout, cwd=WORKSPACE, check=True
        )

    def _patch_manual_hooks(self) -> None:
        if self.variant.upper() in self.MANUAL_HOOK_UNSUPPORTED:
            log(f"Skipping manual hooks patch for variant: {self.variant}")
            return

        hook_patch: Path = PATCHES / "manual_hooks.patch"
        apply_patch(hook_patch, check=False, cwd=WORKSPACE)

    def _clean_driver(self) -> None:
        for driver in self.KNOWN_KSU_DRIVER_PATHS:
            if not driver.exists():
                return
            elif driver.is_symlink():
                log("KernelSU driver symlink detected")
                target: Path = (driver.parent / driver.readlink()).resolve(strict=False)
                driver.unlink()
                if target.exists() and target.is_dir():
                    shutil.rmtree(target)
            elif driver.is_dir():
                log("KernelSU driver folder detected")
                shutil.rmtree(driver)

    def install(self) -> None:
        variant: str = self.variant.upper()

        if variant == "NONE":
            log("Skipping KernelSU setup (Disabled)")
            return

        repo: str
        ref: str | None

        match variant:
            case "OFFICIAL":
                repo = "github.com:tiann/KernelSU"
                ref = "main"
            case "NEXT":
                repo = "github.com:sidex15/KernelSU-Next"
                ref = "next-susfs" if self.use_susfs else "next"
            case "SUKI":
                repo = "github.com:SukiSU-Ultra/SukiSU-Ultra"
                ref = "susfs-main" if self.use_susfs else "nongki"
            case _:
                log(f"Unknown KernelSU variant {variant}, skipping install")
                return

        self._install_ksu(repo, ref)


if __name__ == "__main__":
    raise SystemExit("This file is meant to be imported, not executed.")

