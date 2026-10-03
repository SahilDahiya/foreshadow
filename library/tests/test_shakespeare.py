from pathlib import Path

import pytest

from foreshadow_library.analyse import analyse
from foreshadow_library.domain import Source
from foreshadow_library.parsers import shakespeare
from foreshadow_library.sources import gutenberg

FIXTURE = Path(__file__).parent / "fixtures" / "macbeth-act-1.txt"
CACHE = Path(__file__).parents[1] / ".cache" / "gutenberg" / "100.txt"
SOURCE = Source(provider="gutenberg", ebook_id=100, url="test", retrieved_at="test", sha256="test")


@pytest.fixture(scope="module")
def macbeth():
    play, report = shakespeare.parse_play("THE TRAGEDY OF MACBETH", FIXTURE.read_text(encoding="utf-8"), SOURCE)
    return analyse(play), report


def test_act_one_scenes(macbeth):
    play, _ = macbeth
    assert [s.id for s in play.scenes] == [f"macbeth/1/{n}" for n in range(1, 8)]
    assert play.scenes[6].location == "The same. A Lobby in the Castle."


def test_cast_list(macbeth):
    play, _ = macbeth
    by_id = {c.id: c for c in play.characters}
    assert by_id["duncan"].description == "King of Scotland"
    assert by_id["lady-macbeth"].in_dramatis_personae
    assert not by_id["first-witch"].in_dramatis_personae  # only "three Witches" are listed


def test_direction_inside_a_speech(macbeth):
    play, _ = macbeth
    scene = play.scenes[6]
    first = scene.blocks[1]
    assert first.kind == "speech" and first.speaker_label == "MACBETH"
    kinds = [p.kind for p in first.parts]
    # "Enter Lady Macbeth." interrupts Macbeth, and he carries on: "How now! what news?"
    entrance = next(i for i, p in enumerate(first.parts) if p.kind == "direction")
    assert first.parts[entrance].text == "Enter Lady Macbeth."
    assert first.parts[entrance + 1].text == "How now! what news?"
    assert kinds[0] == "line" and first.parts[0].text.startswith("If it were done")


def test_scene_seven_is_a_two_hander(macbeth):
    play, _ = macbeth
    stats = play.scenes[6].stats
    assert stats.two_hander
    assert {s.character_id for s in stats.speakers} == {"macbeth", "lady-macbeth"}


@pytest.mark.skipif(not CACHE.exists(), reason="run `library build` once to download the source")
def test_every_play_parses_cleanly():
    body = gutenberg.strip_boilerplate(CACHE.read_text(encoding="utf-8"))
    works = shakespeare.split_works(body)
    assert len(works) == 38
    for title, text in works:
        play, report = shakespeare.parse_play(title, text, SOURCE)
        assert report.ok, (play.id, report.warnings)
        if report.scenes_in_contents is not None:
            assert report.scenes_found == report.scenes_in_contents, play.id
