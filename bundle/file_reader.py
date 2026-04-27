
from collections import defaultdict
import os
import sqlite3
import numpy as np
from tqdm import tqdm

from bundle.create_heat_transform import SpectralMapFactory

def compute(h):
    f1, f2, dt = h
    return (int(f1 // 5) & 0x7FF) << 22 | (int(f2 // 5) & 0x7FF) << 11 | (dt & 0x3FF)

def get_song_names():
    song_names: list[str] = []
    for filename in os.listdir("./songs"):
        if ".wav" not in filename:
            continue
        song_names.append(filename)
    return song_names

def process_files():
    for filename in os.listdir("./songs"):
        if ".wav" not in filename:
            continue
        hashes = SpectralMapFactory().with_path(f"./songs/{filename}").with_number_freqs(4).with_downscaling(1).execute().get_hash()
        #prog.map.plot_freqs()
        input_into_db(hashes, filename)


def input_into_db(hashes: list[tuple[int, tuple[int, int, int]]], filename: str):
    songname = os.path.splitext(os.path.basename(filename))[0]

    with sqlite3.connect("app.db") as con:
        con.execute("DELETE FROM songs WHERE name = ?", (songname,))
        cur = con.execute("INSERT INTO songs(name) VALUES (?)", (songname,))
        song_id = cur.lastrowid
        con.executemany(
            "INSERT INTO fingerprints(song_id, anchor_time, hash) VALUES (?,?,?)",
            [(song_id, a_w, compute(h)) for a_w, h in hashes]
        )
        con.commit()

def output_from_db(hashes: list[tuple[int, tuple[int, int, int]]]) -> dict[str, dict[int, int]]:
    """Return peaks as a list-of-lists, indexed by window."""

    query_lookup = {}  # hash -> [query_anchor_times]
    for q_t, q_h in hashes:
        query_lookup.setdefault(compute(q_h), []).append(q_t)

    with sqlite3.connect("app.db") as con:

        # use a nested dicitonary to store offests (name)(d_window)
        offset_counts = defaultdict(lambda: defaultdict(int))
        batch =500
        hash_store = list(query_lookup.keys())
        for i in tqdm(range(0, len(hash_store), batch), desc="running batches"):
            vals = hash_store[i: i+batch]
            cur = con.execute(
                f"""
                SELECT s.name, anchor_time, hash FROM fingerprints f 
                JOIN songs s ON f.song_id = s.id 
                WHERE hash IN ({",".join("?" * len(vals))})
                """,
                vals
                
            )
            for name, db_w, h in cur:
                for q_w in query_lookup[h]:
                    offset_counts[name][db_w - q_w] += 1

    return offset_counts
