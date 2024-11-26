/* Factions */
INSERT INTO factions(name) VALUES ('Chaos Space Marines');

/* Detachments: CHAOS SPACE MARINE */
INSERT INTO detachments (name, faction_id) SELECT 'Chaos Cult', id FROM factions WHERE name = 'Chaos Space Marines';
INSERT INTO detachments (name, faction_id) SELECT 'Deceptors', id FROM factions WHERE name = 'Chaos Space Marines';
INSERT INTO detachments (name, faction_id) SELECT 'Dread Talons', id FROM factions WHERE name = 'Chaos Space Marines';
INSERT INTO detachments (name, faction_id) SELECT 'Fellhammer Siege-Host', id FROM factions WHERE name = 'Chaos Space Marines';
INSERT INTO detachments (name, faction_id) SELECT 'Pactbound Zealots', id FROM factions WHERE name = 'Chaos Space Marines';
INSERT INTO detachments (name, faction_id) SELECT 'Renegade Raiders', id FROM factions WHERE name = 'Chaos Space Marines';
INSERT INTO detachments (name, faction_id) SELECT 'Soulforged Warpack', id FROM factions WHERE name = 'Chaos Space Marines';
INSERT INTO detachments (name, faction_id) SELECT 'Veterans Of The Long War', id FROM factions WHERE name = 'Chaos Space Marines';

/* ----- ----- ----- Models: CHAOS SPACE MARINES ----- ----- ----- */
/* Characters */
INSERT INTO models (name, faction_id, movement, toughness, armor_save, wounds, leadership, objective_control, invulnerable_save, feel_no_pain) SELECT 'Abaddon The Despoiler', id, 5, 5, 2, 9, 5, 4, 4, NULL FROM factions WHERE name = 'Chaos Space Marines';

/* Battleline */
INSERT INTO models (name, faction_id, movement, toughness, armor_save, wounds, leadership, objective_control, invulnerable_save, feel_no_pain) SELECT 'Legionaries', id, 6, 4, 3, 2, 6, 2, NULL, NULL FROM factions WHERE name = 'Chaos Space Marines';

/* Other Datasheets */
INSERT INTO models (name, faction_id, movement, toughness, armor_save, wounds, leadership, objective_control, invulnerable_save, feel_no_pain) SELECT 'Forgefiend', id, 8, 10, 3, 12, 6, 3, 5, NULL FROM factions WHERE name = 'Chaos Space Marines';
