from pathlib import Path
from click.testing import Result
from pytest_mock import MockerFixture, MockType
from typer.testing import CliRunner
from cli import app
import cli
import os
import pytest

runner: CliRunner = CliRunner()


def test_env_var(mocker: MockerFixture) -> None:
    fake: MockType = mocker.patch("cli.KernelBuilder", autospec=True)
    result: Result = runner.invoke(
        app, ["build", "--ksu", "SUKI", "--no-susfs", "--lxc"]
    )

    fake.assert_called_once_with("SUKI", False, True)

    assert result.exit_code == 0
    assert result.output.strip() == "Start Build: ksu='SUKI', susfs=False, lxc=True"
    assert os.environ["KSU"] == "SUKI"
    assert os.environ["SUSFS"] == "false"
    assert os.environ["LXC"] == "true"


@pytest.mark.parametrize(
    "ksu, susfs, expect_exit",
    [
        ("NEXT", True, False),
        ("SUKI", True, False),
        ("NONE", True, True),
    ],
)
def test_build_guard(
    mocker: MockerFixture, ksu: str, susfs: str, expect_exit: bool
) -> None:
    cmd: list[str] = ["build", "--ksu", ksu, "--lxc"]
    if susfs:
        cmd.append("--susfs")

    fake: MockType = mocker.patch("cli.KernelBuilder", autospec=True)
    result: Result = runner.invoke(app, cmd)

    if expect_exit:
        assert result.exit_code != 0
    else:
        fake.assert_called_once_with(ksu, susfs, True)
        assert result.exit_code == 0


@pytest.fixture()
def clean_init(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    fake: Path = tmp_path / "out_dir"
    fake.mkdir()

    fake_output: Path = fake / "fake_out"
    fake_workspace: Path = fake / "fake_ws"
    fake_toolchain: Path = fake / "fake_tc"
    fake_root: Path = fake / "fake_root"
    fake_github_env: Path = fake_root / "github.env"

    for folder in (fake_output, fake_workspace, fake_toolchain, fake_root):
        folder.mkdir()
    fake_github_env.touch()
    fake_github_env.write_text("DUMMY=True")

    monkeypatch.setattr(cli, "OUTPUT", fake_output)
    monkeypatch.setattr(cli, "WORKSPACE", fake_workspace)
    monkeypatch.setattr(cli, "TOOLCHAIN", fake_toolchain)
    monkeypatch.setattr(cli, "ROOT", fake_root)


def test_clean(tmp_path: Path, clean_init) -> None:
    result: Result = runner.invoke(app, ["clean"])
    fake: Path = tmp_path / "out_dir"
    root = fake / "fake_root"
    out  = fake / "fake_out"

    assert result.exit_code == 0
    assert result.output.strip() == "Cleanup completed"
    assert fake.exists()
    assert set(fake.iterdir()) == {root, out}
    assert list(root.iterdir()) == []


def test_clean_all(tmp_path: Path, clean_init):
    result: Result = runner.invoke(app, ["clean", "--all"])
    fake: Path = tmp_path / "out_dir"

    assert result.exit_code == 0
    assert result.output.strip() == "Cleanup completed"
    assert fake.exists()
    assert list(fake.iterdir()) == [fake / "fake_root"]
    assert list((fake / "fake_root").iterdir()) == []
