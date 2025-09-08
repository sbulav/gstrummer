#!/usr/bin/env python3
"""
Test script to verify the extended song structure implementation.
"""

import sys
import os

# Add the app directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from core.patterns import load_songs, load_patterns
from utils.io import load_and_validate_songs

def test_load_songs():
    """Test loading songs with extended structure."""
    print("Testing song loading...")
    
    try:
        songs = load_songs("app/data/songs.yaml")
        print(f"✓ Loaded {len(songs)} songs successfully")
        
        # Test backward compatibility
        simple_songs = [s for s in songs if not s.has_extended_structure()]
        extended_songs = [s for s in songs if s.has_extended_structure()]
        
        print(f"  - Simple format songs: {len(simple_songs)}")
        print(f"  - Extended format songs: {len(extended_songs)}")
        
        # Test a simple song
        if simple_songs:
            song = simple_songs[0]
            print(f"  - Testing simple song: {song.title}")
            print(f"    * Has structure: {song.has_extended_structure()}")
            print(f"    * All chords: {song.all_chords}")
            print(f"    * Progression: {song.progression}")
        
        # Test an extended song
        if extended_songs:
            song = extended_songs[0]
            print(f"  - Testing extended song: {song.title}")
            print(f"    * Has structure: {song.has_extended_structure()}")
            print(f"    * All chords: {song.all_chords}")
            print(f"    * Sections: {song.get_section_names()}")
            
            # Test section access
            for section_name in song.get_section_names():
                section = song.get_section(section_name)
                print(f"    * {section_name}: {len(section.chords)} chords, {section.bars} bars, pattern: {section.pattern}")
                
    except Exception as e:
        print(f"✗ Error loading songs: {e}")
        return False
    
    return True

def test_validation():
    """Test YAML validation."""
    print("\nTesting validation...")
    
    try:
        valid_songs, errors = load_and_validate_songs("app/data/songs.yaml")
        
        if errors:
            print(f"✗ Validation errors found:")
            for error in errors:
                print(f"  - {error}")
            return False
        else:
            print(f"✓ All {len(valid_songs)} songs passed validation")
            return True
            
    except Exception as e:
        print(f"✗ Validation error: {e}")
        return False

def test_patterns():
    """Test that patterns referenced in songs exist."""
    print("\nTesting pattern references...")
    
    try:
        songs = load_songs("app/data/songs.yaml")
        patterns = load_patterns("app/data/patterns.yaml")
        
        pattern_ids = set(patterns.keys())
        missing_patterns = set()
        
        for song in songs:
            # Check main pattern
            if song.pattern_id not in pattern_ids:
                missing_patterns.add(song.pattern_id)
            
            # Check section patterns
            if song.has_extended_structure():
                for section in song.structure.values():
                    if section.pattern not in pattern_ids:
                        missing_patterns.add(section.pattern)
        
        if missing_patterns:
            print(f"✗ Missing patterns: {missing_patterns}")
            return False
        else:
            print(f"✓ All pattern references are valid")
            return True
            
    except Exception as e:
        print(f"✗ Error checking patterns: {e}")
        return False

def print_song_summary():
    """Print a summary of all songs."""
    print("\nSong Summary:")
    print("=" * 60)
    
    try:
        songs = load_songs("app/data/songs.yaml")
        
        for song in songs:
            print(f"\n{song.artist} - {song.title}")
            print(f"  BPM: {song.bpm}, Pattern: {song.pattern_id}")
            print(f"  Difficulty: {song.difficulty or 'Not specified'}")
            print(f"  All chords: {', '.join(song.all_chords)}")
            
            if song.has_extended_structure():
                print(f"  Structure:")
                for section_name in song.get_section_names():
                    section = song.get_section(section_name)
                    chords_str = ', '.join(section.chords)
                    print(f"    {section_name}: [{chords_str}] ({section.pattern})")
            else:
                print(f"  Simple format - Progression: {', '.join(song.progression)}")
                
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    print("Extended Song Structure Test")
    print("=" * 40)
    
    success = True
    success &= test_load_songs()
    success &= test_validation()
    success &= test_patterns()
    
    if success:
        print("\n✓ All tests passed!")
        print_song_summary()
    else:
        print("\n✗ Some tests failed!")
        sys.exit(1)
