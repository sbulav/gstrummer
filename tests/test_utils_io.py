import pytest
from app.utils.io import validate_song_data, validate_pattern_data, validate_song_structure

def test_validate_song_data_happy():
    song = dict(title='t', artist='a', bpm=100, time_sig=[4,4], pattern_id='p', progression=['A','D'], notes='yay')
    errs = validate_song_data(song)
    assert not errs

def test_validate_song_data_missing_fields():
    song = dict(artist='a')
    errs = validate_song_data(song)
    assert any('Missing required field' in e for e in errs)

def test_validate_pattern_data_bad_step():
    pat = dict(id='x', name='x', time_sig=[4,4], steps_per_bar=1, steps=[{'t': -0.1, 'dir': 'Z'}], bpm_default=80, bpm_min=60, bpm_max=120, notes='')
    errs = validate_pattern_data(pat)
    assert any('must be a number between 0 and 1' in e or "'dir'" in e for e in errs)

def test_validate_song_structure_weird_section():
    structure = {'wacky': {'chords':['A']}}
    errs = validate_song_structure(structure)
    assert any('Unknown section type' in e for e in errs)
