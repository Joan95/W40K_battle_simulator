DROP TABLE factions;
DROP TABLE detachments;
DROP TABLE models;

/* Factions: Orks, Space Marines, ... */
CREATE TABLE IF NOT EXISTS factions (
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	name TEXT UNIQUE NOT NULL
);

/* Detatchments */
CREATE TABLE IF NOT EXISTS detachments (
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	name TEXT UNIQUE NOT NULL,
	faction_id INTEGER,
	FOREIGN KEY (faction_id) REFERENCES factions(id)
);

/* Abilities */
CREATE TABLE IF NOT EXISTS abilities (
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	name TEXT UNIQUE NOT NULL
);

/* Units */

/* Models */
CREATE TABLE IF NOT EXISTS models (
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	name TEXT UNIQUE NOT NULL,
	faction_id INTEGER,
	movement INTEGER NOT NULL,
	toughness INTEGER NOT NULL,
	armor_save INTEGER NOT NULL,
	wounds INTEGER NOT NULL,
	leadership INTEGER NOT NULL,
	objective_control INTEGER NOT NULL,
	invulnerable_save INTEGER,
	feel_no_pain INTEGER,
	FOREIGN KEY (faction_id) REFERENCES factions(id)
);