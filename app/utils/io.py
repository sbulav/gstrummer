"""
Input/Output utilities for loading and validating YAML data.
"""

from typing import Dict, Any, List
import yaml


def validate_song_data(song_data: Dict[str, Any]) -> List[str]:
    """
    Validate song data structure and return list of validation errors.
    
    Args:
        song_data: Dictionary containing song data from YAML
        
    Returns:
        List of validation error messages (empty if valid)
    """
    errors = []
    
    # Required fields for all songs
    required_fields = ["title", "artist", "bpm", "time_sig", "pattern_id", "progression", "notes"]
    for field in required_fields:
        if field not in song_data:
            errors.append(f"Missing required field: {field}")
    
    # Validate BPM
    if "bpm" in song_data:
        bpm = song_data["bpm"]
        if not isinstance(bpm, int) or bpm < 30 or bpm > 200:
            errors.append(f"BPM must be an integer between 30-200, got: {bpm}")
    
    # Validate time signature
    if "time_sig" in song_data:
        time_sig = song_data["time_sig"]
        if not isinstance(time_sig, list) or len(time_sig) != 2:
            errors.append(f"time_sig must be a list of two integers, got: {time_sig}")
        elif not all(isinstance(x, int) for x in time_sig):
            errors.append(f"time_sig values must be integers, got: {time_sig}")
    
    # Validate progression
    if "progression" in song_data:
        progression = song_data["progression"]
        if not isinstance(progression, list) or len(progression) == 0:
            errors.append("progression must be a non-empty list of chords")
        elif not all(isinstance(chord, str) for chord in progression):
            errors.append("All progression chords must be strings")
    
    # Validate extended structure if present
    if "structure" in song_data:
        structure_errors = validate_song_structure(song_data["structure"])
        errors.extend(structure_errors)
    
    # Validate all_chords if present
    if "all_chords" in song_data:
        all_chords = song_data["all_chords"]
        if not isinstance(all_chords, list):
            errors.append("all_chords must be a list of chord names")
        elif not all(isinstance(chord, str) for chord in all_chords):
            errors.append("All chords in all_chords must be strings")
    
    # Validate difficulty if present
    if "difficulty" in song_data:
        difficulty = song_data["difficulty"]
        valid_difficulties = ["beginner", "intermediate", "advanced"]
        if difficulty not in valid_difficulties:
            errors.append(f"difficulty must be one of {valid_difficulties}, got: {difficulty}")
    
    return errors


def validate_song_structure(structure: Dict[str, Any]) -> List[str]:
    """
    Validate the structure section of a song.
    
    Args:
        structure: Dictionary containing section definitions
        
    Returns:
        List of validation error messages
    """
    errors = []
    
    valid_sections = ["intro", "verse", "pre_chorus", "chorus", "bridge", "outro", "solo"]
    
    for section_name, section_data in structure.items():
        if section_name not in valid_sections:
            errors.append(f"Unknown section type: {section_name}. Valid sections: {valid_sections}")
        
        # Required fields for each section
        if "chords" not in section_data:
            errors.append(f"Section {section_name} missing required 'chords' field")
        else:
            chords = section_data["chords"]
            if not isinstance(chords, list) or len(chords) == 0:
                errors.append(f"Section {section_name} 'chords' must be a non-empty list")
            elif not all(isinstance(chord, str) for chord in chords):
                errors.append(f"All chords in section {section_name} must be strings")
        
        # Optional fields validation
        if "pattern" in section_data and not isinstance(section_data["pattern"], str):
            errors.append(f"Section {section_name} 'pattern' must be a string")
        
        if "bars" in section_data:
            bars = section_data["bars"]
            if not isinstance(bars, int) or bars < 1 or bars > 32:
                errors.append(f"Section {section_name} 'bars' must be an integer between 1-32")
        
        if "repeat" in section_data:
            repeat = section_data["repeat"]
            if not isinstance(repeat, int) or repeat < 1 or repeat > 10:
                errors.append(f"Section {section_name} 'repeat' must be an integer between 1-10")
        
        if "bpm_override" in section_data:
            bpm_override = section_data["bpm_override"]
            if not isinstance(bpm_override, int) or bpm_override < 30 or bpm_override > 200:
                errors.append(f"Section {section_name} 'bpm_override' must be an integer between 30-200")
    
    return errors


def load_and_validate_songs(path: str) -> tuple[List[Dict[str, Any]], List[str]]:
    """
    Load songs from YAML file and validate them.
    
    Args:
        path: Path to songs YAML file
        
    Returns:
        Tuple of (valid_songs_data, all_validation_errors)
    """
    try:
        with open(path, "r", encoding="utf-8") as f:
            songs_data = yaml.safe_load(f)
    except FileNotFoundError:
        return [], [f"Songs file not found: {path}"]
    except yaml.YAMLError as e:
        return [], [f"YAML parsing error in {path}: {e}"]
    
    if not isinstance(songs_data, list):
        return [], ["Songs file must contain a list of songs"]
    
    valid_songs = []
    all_errors = []
    
    for i, song_data in enumerate(songs_data):
        errors = validate_song_data(song_data)
        if errors:
            all_errors.extend([f"Song {i+1} ({song_data.get('title', 'Unknown')}): {error}" for error in errors])
        else:
            valid_songs.append(song_data)
    
    return valid_songs, all_errors


def validate_pattern_data(pattern_data: Dict[str, Any]) -> List[str]:
    """
    Validate pattern data structure.
    
    Args:
        pattern_data: Dictionary containing pattern data from YAML
        
    Returns:
        List of validation error messages
    """
    errors = []
    
    required_fields = ["id", "name", "time_sig", "steps_per_bar", "steps", 
                      "bpm_default", "bpm_min", "bpm_max", "notes"]
    
    for field in required_fields:
        if field not in pattern_data:
            errors.append(f"Missing required field: {field}")
    
    # Validate steps
    if "steps" in pattern_data:
        steps = pattern_data["steps"]
        if not isinstance(steps, list):
            errors.append("'steps' must be a list")
        else:
            for i, step in enumerate(steps):
                if not isinstance(step, dict):
                    errors.append(f"Step {i+1} must be a dictionary")
                    continue
                
                if "t" not in step:
                    errors.append(f"Step {i+1} missing 't' field")
                elif not isinstance(step["t"], (int, float)) or step["t"] < 0 or step["t"] >= 1:
                    errors.append(f"Step {i+1} 't' must be a number between 0 and 1")
                
                if "dir" not in step:
                    errors.append(f"Step {i+1} missing 'dir' field")
                elif step["dir"] not in ["D", "U", "-"]:
                    errors.append(f"Step {i+1} 'dir' must be 'D', 'U', or '-'")
                
                if "accent" in step:
                    accent = step["accent"]
                    if not isinstance(accent, (int, float)) or accent < 0 or accent > 1:
                        errors.append(f"Step {i+1} 'accent' must be a number between 0 and 1")
                
                if "technique" in step:
                    technique = step["technique"]
                    valid_techniques = ["open", "mute", "palm", "ghost"]
                    if technique not in valid_techniques:
                        errors.append(f"Step {i+1} 'technique' must be one of {valid_techniques}")
    
    return errors
