import shutil
import subprocess
import time
from pathlib import Path

import pytest

import zmigrate


def run_cli(args):
    zmigrate.main(args)


def docker_available() -> bool:
    return shutil.which("docker") is not None


@pytest.mark.skipif(not docker_available(), reason="docker not available")
def test_postgresql_migration(tmp_path):
    container = "zmigrate_test"
    subprocess.check_call([
        "docker",
        "run",
        "--name",
        container,
        "-e",
        "POSTGRES_PASSWORD=postgres",
        "-p",
        "5432:5432",
        "-d",
        "postgres",
    ])
    try:
        time.sleep(10)
        mig_dir = tmp_path / "migration"
        shutil.copytree(Path("tests/postgresql/migration"), mig_dir)
        run_cli([
            "--migration-dir",
            str(mig_dir),
            "--driver",
            "postgres",
            "--database",
            "db",
            "--user",
            "postgres",
            "--password",
            "postgres",
            "--host",
            "localhost",
            "--seed",
            "yes",
        ])
        run_cli([
            "--migration-dir",
            str(mig_dir),
            "--driver",
            "postgres",
            "--database",
            "db",
            "--user",
            "postgres",
            "--password",
            "postgres",
            "--host",
            "localhost",
            "-d",
            "down",
        ])
        run_cli([
            "--migration-dir",
            str(mig_dir),
            "--driver",
            "postgres",
            "--database",
            "db",
            "--user",
            "postgres",
            "--password",
            "postgres",
            "--host",
            "localhost",
        ])
    finally:
        subprocess.call(["docker", "stop", container])
