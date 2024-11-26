/* Factions */
INSERT INTO factions(name) VALUES ("T\'Au Empire");

/* Detachments: T'AU EMPIRE */
INSERT INTO detachments (name, faction_id) SELECT 'Kauyon', id FROM factions WHERE name = "T\'Au Empire";
INSERT INTO detachments (name, faction_id) SELECT 'Kroot Hunting Pack', id FROM factions WHERE name = "T\'Au Empire";
INSERT INTO detachments (name, faction_id) SELECT "Mont\'Ka", id FROM factions WHERE name = "T\'Au Empire";
INSERT INTO detachments (name, faction_id) SELECT 'Retaliation Cadre', id FROM factions WHERE name = "T\'Au Empire";

/* ----- ----- ----- Models: T'AU EMPIRE ----- ----- ----- */
/* Characters */
INSERT INTO models (name, faction_id, movement, toughness, armor_save, wounds, leadership, objective_control, invulnerable_save, feel_no_pain) SELECT 'Commander Farsight', id, 10, 5, 2, 8, 6, 2, 4, NULL FROM factions WHERE name = "T\'Au Empire";

/* Other Datasheets */
INSERT INTO models (name, faction_id, movement, toughness, armor_save, wounds, leadership, objective_control, invulnerable_save, feel_no_pain) SELECT 'Commander in Coldstar Battlesuit', id, 12, 5, 3, 6, 7, 2, NULL, NULL FROM factions WHERE name = "T\'Au Empire";
INSERT INTO models (name, faction_id, movement, toughness, armor_save, wounds, leadership, objective_control, invulnerable_save, feel_no_pain) SELECT 'Commander in Enforcer Battlesuit', id, 8, 5, 2, 6, 7, 2, NULL, NULL FROM factions WHERE name = "T\'Au Empire";
INSERT INTO models (name, faction_id, movement, toughness, armor_save, wounds, leadership, objective_control, invulnerable_save, feel_no_pain) SELECT 'Broadside Battlesuits', id, 5, 6, 2, 8, 7, 2, NULL, NULL FROM factions WHERE name = "T\'Au Empire";