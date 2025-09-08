import pytest
from app.core.patterns import Step, StrumPattern, load_patterns, Song, load_songs

def test_step_init_and_fields():
    s = Step(t=0.0, dir='D', accent=0.5, technique='open')
    assert s.t == 0.0
    assert s.dir == 'D'
    assert s.accent == 0.5
    assert s.technique == 'open'

def test_strummpattern_fields():
    steps = [Step(t=0.0, dir='D'), Step(t=0.5, dir='U')]
    pat = StrumPattern(id='test', name='Test', time_sig=(4,4), steps_per_bar=2, steps=steps, bpm_default=90, bpm_min=60, bpm_max=120, notes='foo')
    assert pat.steps_per_bar == 2
    assert pat.steps[1].dir == 'U'

def test_load_patterns_default():
    pats = load_patterns("app/data/patterns.yaml")
    assert isinstance(pats, dict)
    assert len(pats) > 0
    for p in pats.values():
        assert isinstance(p, StrumPattern)

def test_song_model():
    s = Song(title="foo", artist="bar", bpm=100, time_sig=(4,4), pattern_id="test", progression=["A"], notes="n")
    assert s.title == "foo"
    assert s.all_chords == ["A"]
    assert not s.has_extended_structure()
    # Structure
    sect = s.get_section("intro")
    assert sect is None
    # Extended structure
    from app.core.patterns import SongSection
    ext_song = Song(title="foo2", artist="b", bpm=90, time_sig=(4,4), pattern_id="test", progression=["Am"], notes="n", structure={"verse": SongSection(name="verse", chords=["Am"], pattern="test")})
    assert ext_song.has_extended_structure()
