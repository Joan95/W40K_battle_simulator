DROP TABLE IF EXISTS factions;
DROP TABLE IF EXISTS detachments;
DROP TABLE IF EXISTS abilities;
DROP TABLE IF EXISTS melee_weapons;
DROP TABLE IF EXISTS ranged_weapons;
DROP TABLE IF EXISTS models;
DROP TABLE IF EXISTS model_melee_weapons;
DROP TABLE IF EXISTS model_ranged_weapons;
DROP TABLE IF EXISTS melee_weapon_abilities;
DROP TABLE IF EXISTS ranged_weapon_abilities;
DROP TABLE IF EXISTS phases;
DROP TABLE IF EXISTS movements;
DROP TABLE IF EXISTS rolls;

/* Create table for Game Phases */
CREATE TABLE IF NOT EXISTS phases (
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	name TEXT UNIQUE NOT NULL,
	sequence INTEGER NOT NULL
);

/* Movements */
CREATE TABLE IF NOT EXISTS movements (
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	name TEXT UNIQUE NOT NULL
);

/* Rolls */
CREATE TABLE IF NOT EXISTS rolls (
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	name TEXT UNIQUE NOT NULL
);

/* Factions: Orks, Space Marines, ... */
CREATE TABLE IF NOT EXISTS factions (
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	name TEXT UNIQUE NOT NULL,
	color TEXT NOT NULL
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
	name TEXT UNIQUE NOT NULL,
	amount INTEGER
);

/* Melee Weapons */
CREATE TABLE IF NOT EXISTS melee_weapons (
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	name TEXT UNIQUE NOT NULL,
	range_attack INTEGER,
	attack TEXT NOT NULL,
	ballistic_skill INTEGER NOT NULL,
	strength INTEGER NOT NULL,
	armour_penetration INTEGER NOT NULL,
	damage TEXT NOT NULL
);

/* Ranged Weapons */
CREATE TABLE IF NOT EXISTS ranged_weapons (
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	name TEXT UNIQUE NOT NULL,
	range_attack INTEGER NOT NULL,
	attack INTEGER NOT NULL,
	ballistic_skill INTEGER NOT NULL,
	strength INTEGER NOT NULL,
	armour_penetration INTEGER NOT NULL,
	damage TEXT NOT NULL
);

/* Units */
CREATE TABLE IF NOT EXISTS units (
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	name TEXT UNIQUE NOT NULL,
	faction_id INTEGER,
	points INTEGER NOT NULL,
	battleshock_check_test BOOLEAN DEFAULT(FALSE),
	FOREIGN KEY (faction_id) REFERENCES factions(id)
);

/* Unit Models (association table) */
CREATE TABLE IF NOT EXISTS unit_models (
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	unit_id INTEGER,
	model_id INTEGER,
	model_count INTEGER NOT NULL,
	FOREIGN KEY (unit_id) REFERENCES units(id),
	FOREIGN KEY (model_id) REFERENCES models(id)
);

/* Models */
CREATE TABLE IF NOT EXISTS models (
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	name TEXT UNIQUE NOT NULL,
	faction_id INTEGER NOT NULL,
	movement TEXT NOT NULL,
	toughness INTEGER NOT NULL,
	armor_save INTEGER NOT NULL,
	wounds INTEGER NOT NULL,
	leadership INTEGER NOT NULL,
	objective_control INTEGER NOT NULL,
	invulnerable_save INTEGER,
	feel_no_pain INTEGER,
	FOREIGN KEY (faction_id) REFERENCES factions(id)
);

/* Model Melee Weapons (association table) */
CREATE TABLE IF NOT EXISTS model_melee_weapons (
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	model_id INTEGER,
	melee_weapon_id INTEGER,
	FOREIGN KEY (model_id) REFERENCES models(id),
	FOREIGN KEY (melee_weapon_id) REFERENCES melee_weapons(id)
);

/* Model Ranged Weapons (association table) */
CREATE TABLE IF NOT EXISTS model_ranged_weapons (
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	model_id INTEGER,
	ranged_weapon_id INTEGER,
	FOREIGN KEY (model_id) REFERENCES models(id),
	FOREIGN KEY (ranged_weapon_id) REFERENCES ranged_weapons(id)
);

/* Melee Weapon Abilities (association table) */
CREATE TABLE IF NOT EXISTS melee_weapon_abilities (
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	melee_weapon_id INTEGER,
	ability_id INTEGER,
	FOREIGN KEY (melee_weapon_id) REFERENCES melee_weapons(id),
	FOREIGN KEY (ability_id) REFERENCES abilities(id)
);

/* Ranged Weapon Abilities (association table) */
CREATE TABLE IF NOT EXISTS ranged_weapon_abilities (
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	ranged_weapon_id INTEGER,
	ability_id INTEGER,
	FOREIGN KEY (ranged_weapon_id) REFERENCES ranged_weapons(id),
	FOREIGN KEY (ability_id) REFERENCES abilities(id)
);
