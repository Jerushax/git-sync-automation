from pathlib import Path

from src.sync_engine import SyncEngine


def test_sync_engine(tmp_path):
    source = tmp_path / "source"
    target = tmp_path / "target"

    source.mkdir()
    target.mkdir()

    file_path = source / "test.txt"
    file_path.write_text("hello")

    engine = SyncEngine([])

    synced = engine.sync_files(
        source,
        target,
        [("M", "test.txt")]
    )

    assert (target / "test.txt").exists()
    assert synced == ["test.txt"]