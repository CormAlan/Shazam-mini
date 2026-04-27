CREATE TABLE IF NOT EXISTS songs (
	id   INTEGER PRIMARY KEY AUTOINCREMENT,
	name TEXT    NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS fingerprints (
	song_id		  INTEGER NOT NULL,
	anchor_time INTEGER NOT NULL,
	hash				INTEGER NOT NULL,
	FOREIGN KEY (song_id) REFERENCES songs(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_hashes_hash ON fingerprints(hash);
CREATE INDEX IF NOT EXISTS idx_hashes_song ON fingerprints(song_id);
