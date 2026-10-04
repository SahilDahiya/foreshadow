from pathlib import Path

from foreshadow_library import candidates as C
from foreshadow_library.domain import Source
from foreshadow_library.parsers import shakespeare

FIXTURE = Path(__file__).parent / "fixtures" / "macbeth-act-1.txt"
SOURCE = Source(provider="gutenberg", ebook_id=100, url="test", retrieved_at="test", sha256="test")


def play():
    return shakespeare.parse_play("THE TRAGEDY OF MACBETH", FIXTURE.read_text(encoding="utf-8"), SOURCE)[0]


def scene_7():
    return play().scenes[6]


def test_runs_have_exactly_two_speakers():
    for scene in play().scenes:
        for start, end, pair in C.two_speaker_runs(scene):
            speakers = {b.speaker_ids[0] for b in scene.blocks[start:end] if b.kind == "speech"}
            assert speakers == set(pair)


def test_the_host_opens_and_closes():
    scene = scene_7()
    start, end, (x, y) = max(C.two_speaker_runs(scene), key=lambda r: r[1] - r[0])
    for host, partner in ((x, y), (y, x)):
        c = C._candidate(play(), scene, start, end, host, partner)
        assert scene.blocks[c.start].speaker_ids == [host]
        assert scene.blocks[c.end - 1].speaker_ids == [host]


def test_pieces_cut_at_entrances():
    scene = scene_7()
    for start, end in C.pieces(scene, 0, len(scene.blocks)):
        for block in scene.blocks[start:end]:
            assert not C._has_cast_change(block)


def metrics(**changes):
    base = dict(
        host_speeches=8, partner_speeches=7, host_words=400, partner_words=300, host_share=0.57,
        mean_host_words=50, median_host_words=30, max_host_words=220, monologues=1, minutes=5.2,
        questions=0.3, address=0.8, names=1, directions=0, cast_changes=0,
    )
    return C.CandidateMetrics(**{**base, **changes})


def test_a_monologue_is_allowed_but_the_improviser_needs_turns():
    assert C.passes(metrics(), C.Limits())  # one 220-word host speech is fine
    assert not C.passes(metrics(partner_speeches=2), C.Limits())
    assert not C.passes(metrics(host_share=0.95), C.Limits())
    assert not C.passes(metrics(cast_changes=1), C.Limits())


def test_sizes():
    assert [C.size_of(m) for m in (2.0, 5.0, 10.0, 20.0, 40.0)] == [None, "small", "medium", "big", None]
    # 260 host words at reading pace is 2 minutes; ten improvised replies add 3.
    assert C.minutes_of(260, 10) == 5.0
