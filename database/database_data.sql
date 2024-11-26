/* Game phases */
INSERT INTO phases (name, sequence) VALUES ('Command Phase', 1);
INSERT INTO phases (name, sequence) VALUES ('Movement Phase', 2);
INSERT INTO phases (name, sequence) VALUES ('Shooting Phase', 3);
INSERT INTO phases (name, sequence) VALUES ('Charge Phase', 4);
INSERT INTO phases (name, sequence) VALUES ('Fight Phase', 5);

/* Insert values for movements */
INSERT INTO movements (name) VALUES ('Normal Move');
INSERT INTO movements (name) VALUES ('Advance');
INSERT INTO movements (name) VALUES ('Charge Move');
INSERT INTO movements (name) VALUES ('Fall Back');
INSERT INTO movements (name) VALUES ('Pile In');
INSERT INTO movements (name) VALUES ('Consolidate');

/* Insert values for rolls */
INSERT INTO rolls (name) VALUES ('Attack Roll');
INSERT INTO rolls (name) VALUES ('Hit Roll');
INSERT INTO rolls (name) VALUES ('Wound Roll');

/* Abilities */
INSERT INTO abilities (name, amount) VALUES ('Anti-monster 4', 4);
INSERT INTO abilities (name, amount) VALUES ('Anti-vehicle 4', 4);
INSERT INTO abilities (name, amount) VALUES ('Blast', NULL);
INSERT INTO abilities (name, amount) VALUES ('Devastating Wounds', NULL);
INSERT INTO abilities (name, amount) VALUES ('Extra Attacks', NULL);
INSERT INTO abilities (name, amount) VALUES ('Heavy', NULL);
INSERT INTO abilities (name, amount) VALUES ('Pistol', NULL);
INSERT INTO abilities (name, amount) VALUES ('Precision', NULL);
INSERT INTO abilities (name, amount) VALUES ('Rapid Fire 1', 1);
INSERT INTO abilities (name, amount) VALUES ('Rapid Fire 2', 2);
INSERT INTO abilities (name, amount) VALUES ('Twin-linked', NULL);


