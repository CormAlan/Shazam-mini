import numpy as np
import math

from tqdm import tqdm

from bundle.create_heat_transform import SpectralMapFactory
from bundle.file_reader import get_song_names, output_from_db

def match_audio(audio: np.ndarray):
    prog = SpectralMapFactory().with_downscaling(1).with_audio(audio).with_number_freqs(4).execute()
    hashes = prog.get_hash()

    offset_counts = output_from_db(hashes)
    best_song, best_score, best_offset, best_percentage = None, -1, 0, 0
    for song_name, offsets in tqdm(offset_counts.items()):
        if not offsets:
            continue
        # get the best key
        top_offset = max(offsets, key=offsets.get)
        top_count = offsets[top_offset]
        if top_count > best_score:
            best_song = song_name
            best_score = top_count
            best_offset = top_offset

    print(f"Found {best_song}")
    return prog, best_song
    
