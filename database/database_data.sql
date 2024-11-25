
/* Factions */
INSERT INTO factions(name) VALUES ('Orks');

/* Detachments */
INSERT INTO detachments (name, faction_id) SELECT 'Bully Boyz', id FROM factions WHERE name = 'Orks';
INSERT INTO detachments (name, faction_id) SELECT 'Da Big Hunt', id FROM factions WHERE name = 'Orks';
INSERT INTO detachments (name, faction_id) SELECT 'Dread Mob', id FROM factions WHERE name = 'Orks';
INSERT INTO detachments (name, faction_id) SELECT 'Green Tide', id FROM factions WHERE name = 'Orks';
INSERT INTO detachments (name, faction_id) SELECT 'Kult Of Speed', id FROM factions WHERE name = 'Orks';
INSERT INTO detachments (name, faction_id) SELECT 'War Horde', id FROM factions WHERE name = 'Orks';

/* Abilities */

/* Models: ORKS */
/* Characters */
INSERT INTO models (name, faction_id, movement, toughness, armor_save, wounds, leadership, objective_control, invulnerable_save, feel_no_pain) SELECT 'Beastboss', id, 6, 5, 4, 6, 6, 1, 5, 6 FROM factions WHERE name = 'Orks';
INSERT INTO models (name, faction_id, movement, toughness, armor_save, wounds, leadership, objective_control, invulnerable_save, feel_no_pain) SELECT 'Big Mek with Shokk Attack Gun', id, 6, 5, 4, 5, 7, 1, NULL, NULL FROM factions WHERE name = 'Orks';

/* Battleline */
INSERT INTO models (name, faction_id, movement, toughness, armor_save, wounds, leadership, objective_control, invulnerable_save, feel_no_pain) SELECT 'Beast Snagga Boy', id, 6, 5, 5, 1, 7, 2, NULL, 6 FROM factions WHERE name = 'Orks';
INSERT INTO models (name, faction_id, movement, toughness, armor_save, wounds, leadership, objective_control, invulnerable_save, feel_no_pain) SELECT 'Beast Snagga Nob', id, 6, 5, 5, 2, 7, 2, NULL, 6 FROM factions WHERE name = 'Orks';

/* Other Datasheets */
INSERT INTO models (name, faction_id, movement, toughness, armor_save, wounds, leadership, objective_control, invulnerable_save, feel_no_pain) SELECT 'Hunta Rig', id, 10, 10, 3, 16, 7, 5, NULL, 6 FROM factions WHERE name = 'Orks';
