/* Faction */
INSERT INTO factions(name, color) VALUES ('Orks', 'Green');

/* Detachments */
INSERT INTO detachments (name, faction_id) SELECT 'Bully Boyz', id FROM factions WHERE name = 'Orks';
INSERT INTO detachments (name, faction_id) SELECT 'Da Big Hunt', id FROM factions WHERE name = 'Orks';
INSERT INTO detachments (name, faction_id) SELECT 'Dread Mob', id FROM factions WHERE name = 'Orks';
INSERT INTO detachments (name, faction_id) SELECT 'Green Tide', id FROM factions WHERE name = 'Orks';
INSERT INTO detachments (name, faction_id) SELECT 'Kult Of Speed', id FROM factions WHERE name = 'Orks';
INSERT INTO detachments (name, faction_id) SELECT 'War Horde', id FROM factions WHERE name = 'Orks';


/* Weapons */
/* Ranged: Big Shoota */
INSERT INTO ranged_weapons (name, range_attack, attack, ballistic_skill, strength, armour_penetration, damage) VALUES ('Big Shoota', '36"', "3", 4, 5, 0, "1");
INSERT INTO ranged_weapon_abilities (ranged_weapon_id, ability_id) SELECT rw.id, a.id FROM ranged_weapons rw, abilities a WHERE rw.name = 'Big Shoota' and a.name = 'Rapid Fire 2';

/* Ranged: Shokk Attack Gun */
INSERT INTO ranged_weapons (name, range_attack, attack, ballistic_skill, strength, armour_penetration, damage) VALUES ('Shokk Attack Gun', '60"', "D6+1", 5, 9, -4, "D6");
INSERT INTO ranged_weapon_abilities (ranged_weapon_id, ability_id) SELECT rw.id, a.id FROM ranged_weapons rw, abilities a WHERE rw.name = 'Shokk Attack Gun' and a.name = 'Blast';
INSERT INTO ranged_weapon_abilities (ranged_weapon_id, ability_id) SELECT rw.id, a.id FROM ranged_weapons rw, abilities a WHERE rw.name = 'Shokk Attack Gun' and a.name = 'Heavy';

/* Ranged: Shoota */
INSERT INTO ranged_weapons (name, range_attack, attack, ballistic_skill, strength, armour_penetration, damage) VALUES ('Shoota', '18"', "2", 4, 4, 0, "1");
INSERT INTO ranged_weapon_abilities (ranged_weapon_id, ability_id) SELECT rw.id, a.id FROM ranged_weapons rw, abilities a WHERE rw.name = 'Shoota' and a.name = 'Rapid Fire 1';

/* Ranged: Slugga */
INSERT INTO ranged_weapons (name, range_attack, attack, ballistic_skill, strength, armour_penetration, damage) VALUES ('Slugga', '12"', "1", 4, 4, 0, "1");
INSERT INTO ranged_weapon_abilities (ranged_weapon_id, ability_id) SELECT rw.id, a.id FROM ranged_weapons rw, abilities a WHERE rw.name = 'Slugga' and a.name = 'Pistol';

/* Ranged: Thump Gun */
INSERT INTO ranged_weapons (name, range_attack, attack, ballistic_skill, strength, armour_penetration, damage) VALUES ('Thump Gun', '18"', "D3", 5, 6, 0, "2");
INSERT INTO ranged_weapon_abilities (ranged_weapon_id, ability_id) SELECT rw.id, a.id FROM ranged_weapons rw, abilities a WHERE rw.name = 'Thump Gun' and a.name = 'Blast';


/* Melee: Beast Snagga Klaw */
INSERT INTO melee_weapons (name, range_attack, attack, ballistic_skill, strength, armour_penetration, damage) VALUES ('Beast Snagga Klaw', NULL, "4", 3, 10, -2, 2);
INSERT INTO melee_weapon_abilities (melee_weapon_id, ability_id) SELECT mw.id, a.id FROM melee_weapons mw, abilities a WHERE mw.name = 'Beast Snagga Klaw' and a.name = 'Anti-monster 4';
INSERT INTO melee_weapon_abilities (melee_weapon_id, ability_id) SELECT mw.id, a.id FROM melee_weapons mw, abilities a WHERE mw.name = 'Beast Snagga Klaw' and a.name = 'Anti-vehicle 4';

/* Melee: Beastchoppa */
INSERT INTO melee_weapons (name, range_attack, attack, ballistic_skill, strength, armour_penetration, damage) VALUES ('Beastchoppa', NULL, "6", 2, 6, -1, 2);
INSERT INTO melee_weapon_abilities (melee_weapon_id, ability_id) SELECT mw.id, a.id FROM melee_weapons mw, abilities a WHERE mw.name = 'Beastchoppa' and a.name = 'Anti-monster 4';
INSERT INTO melee_weapon_abilities (melee_weapon_id, ability_id) SELECT mw.id, a.id FROM melee_weapons mw, abilities a WHERE mw.name = 'Beastchoppa' and a.name = 'Anti-vehicle 4';

/* Melee: Big Chompa's Jaws */
INSERT INTO melee_weapons (name, range_attack, attack, ballistic_skill, strength, armour_penetration, damage) VALUES ("Big Chompa's Jaws", NULL, "3", 3, 7, -2, 4);
INSERT INTO melee_weapon_abilities (melee_weapon_id, ability_id) SELECT mw.id, a.id FROM melee_weapons mw, abilities a WHERE mw.name = "Big Chompa's Jaws" and a.name = 'Devastating Wounds';
INSERT INTO melee_weapon_abilities (melee_weapon_id, ability_id) SELECT mw.id, a.id FROM melee_weapons mw, abilities a WHERE mw.name = "Big Chompa's Jaws" and a.name = 'Extra Attacks';

/* Melee: Close Combat Weapon */
INSERT INTO melee_weapons (name, range_attack, attack, ballistic_skill, strength, armour_penetration, damage) VALUES ('Close Combat Weapon', NULL, "4", 3, 5, 0, 1);

/* Melee: Gutrippa */
INSERT INTO melee_weapons (name, range_attack, attack, ballistic_skill, strength, armour_penetration, damage) VALUES ('Gutrippa', NULL, "6", 2, 7, -1, 3);
INSERT INTO melee_weapon_abilities (melee_weapon_id, ability_id) SELECT mw.id, a.id FROM melee_weapons mw, abilities a WHERE mw.name = 'Gutrippa' and a.name = 'Anti-monster 4';
INSERT INTO melee_weapon_abilities (melee_weapon_id, ability_id) SELECT mw.id, a.id FROM melee_weapons mw, abilities a WHERE mw.name = 'Gutrippa' and a.name = 'Anti-vehicle 4';

/* Melee: Mork's Teeth */
INSERT INTO melee_weapons (name, range_attack, attack, ballistic_skill, strength, armour_penetration, damage) VALUES ("Mork's Teeth", NULL, "6", 2, 6, -1, 2);
INSERT INTO melee_weapon_abilities (melee_weapon_id, ability_id) SELECT mw.id, a.id FROM melee_weapons mw, abilities a WHERE mw.name = "Mork's Teeth" and a.name = 'Precision';
INSERT INTO melee_weapon_abilities (melee_weapon_id, ability_id) SELECT mw.id, a.id FROM melee_weapons mw, abilities a WHERE mw.name = "Mork's Teeth" and a.name = 'Twin-linked';

/* Melee: 'Uge Choppa */
INSERT INTO melee_weapons (name, range_attack, attack, ballistic_skill, strength, armour_penetration, damage) VALUES ("'Uge Choppa", NULL, "4", 2, 12, -2, 2);


/* Models */
/* Characters */
INSERT INTO models (name, faction_id, movement, toughness, armor_save, wounds, leadership, objective_control, invulnerable_save, feel_no_pain) SELECT 'Beastboss', id, '6"', 5, 4, 6, 6, 1, 5, 6 FROM factions WHERE name = 'Orks';
INSERT INTO models (name, faction_id, movement, toughness, armor_save, wounds, leadership, objective_control, invulnerable_save, feel_no_pain) SELECT 'Big Mek with Shokk Attack Gun', id, '6"', 5, 4, 5, 7, 1, NULL, NULL FROM factions WHERE name = 'Orks';
INSERT INTO models (name, faction_id, movement, toughness, armor_save, wounds, leadership, objective_control, invulnerable_save, feel_no_pain) SELECT 'Boss Snikrot', id, '6"', 5, 5, 6, 6, 1, 5, NULL FROM factions WHERE name = 'Orks';

/* Battleline */
INSERT INTO models (name, faction_id, movement, toughness, armor_save, wounds, leadership, objective_control, invulnerable_save, feel_no_pain) SELECT 'Beast Snagga Boy', id, '6"', 5, 5, 1, 7, 2, NULL, 6 FROM factions WHERE name = 'Orks';
INSERT INTO models (name, faction_id, movement, toughness, armor_save, wounds, leadership, objective_control, invulnerable_save, feel_no_pain) SELECT 'Beast Snagga Nob', id, '6"', 5, 5, 2, 7, 2, NULL, 6 FROM factions WHERE name = 'Orks';

/* Other Datasheets */
INSERT INTO models (name, faction_id, movement, toughness, armor_save, wounds, leadership, objective_control, invulnerable_save, feel_no_pain) SELECT 'Hunta Rig', id, '10"', 10, 3, 16, 7, 5, NULL, 6 FROM factions WHERE name = 'Orks';