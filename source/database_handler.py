import sqlite3


class DatabaseHandler:
    def __init__(self, db_path):
        self.database_path = db_path

    def get_melee_weapon_by_name(self, melee_weapon_name, model_id):
        with sqlite3.connect(self.database_path) as conn:
            cursor = conn.cursor()
            cursor.execute(f'SELECT range_attack, attack, ballistic_skill, strength, armour_penetration, damage'
                           f' FROM melee_weapons WHERE name = \"{melee_weapon_name}\" AND model_id = \"{model_id}\"')
            return cursor.fetchall()

    def get_ranged_weapon_by_name(self, ranged_weapon_name, model_id):
        with sqlite3.connect(self.database_path) as conn:
            cursor = conn.cursor()
            cursor.execute(f'SELECT range_attack, attack, ballistic_skill, strength, armour_penetration, damage'
                           f' FROM ranged_weapons WHERE name = \"{ranged_weapon_name}\" AND model_id = \"{model_id}\"')
            return cursor.fetchall()

    def get_weapon_abilities(self, model_name, weapon_name, weapon_type):
        with sqlite3.connect(self.database_path) as conn:
            cursor = conn.cursor()

            if weapon_type.name == 'MELEE':
                query = '''
                SELECT DISTINCT abilities.name AS ability_name 
                FROM abilities 
                JOIN melee_weapon_abilities mwa ON abilities.id = mwa.ability_id 
                JOIN melee_weapons mw ON mwa.melee_weapon_id = mw.id 
                JOIN models m ON mw.model_id = m.id 
                WHERE mw.name = ? AND m.name = ?
                '''
            elif weapon_type.name == 'RANGED':
                query = '''
                SELECT DISTINCT abilities.name AS ability_name 
                FROM abilities 
                JOIN ranged_weapon_abilities rwa ON abilities.id = rwa.ability_id 
                JOIN ranged_weapons rw ON rwa.ranged_weapon_id = rw.id 
                JOIN models m ON rw.model_id = m.id 
                WHERE rw.name = ? AND m.name = ?
                '''
            else:
                raise ValueError

            cursor.execute(query, (weapon_name, model_name,))
            return cursor.fetchall()

    def get_model_id_by_name(self, model_name):
        with sqlite3.connect(self.database_path) as conn:
            cursor = conn.cursor()
            cursor.execute(f'SELECT id FROM models WHERE name = \"{model_name}\"')
            return cursor.fetchall()

    def get_model_by_name(self, model_name):
        with sqlite3.connect(self.database_path) as conn:
            cursor = conn.cursor()
            cursor.execute(f'SELECT movement, toughness, armor_save, wounds, leadership, objective_control, '
                           f'invulnerable_save, feel_no_pain FROM models WHERE name = \"{model_name}\"')
            return cursor.fetchall()

    def get_model_keywords(self, model_name):
        with sqlite3.connect(self.database_path) as conn:
            cursor = conn.cursor()
            query = ''' 
            SELECT k.name AS keyword 
            FROM models m 
            JOIN model_keywords mk ON m.id = mk.model_id 
            JOIN keywords k ON mk.keyword_id = k.id 
            WHERE m.name = ? '''
            cursor.execute(query, (model_name,))
            keywords = cursor.fetchall()
            return [keyword[0] for keyword in keywords]

    def get_factions(self):
        with sqlite3.connect(self.database_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM factions')
            return cursor.fetchall()

    def get_faction_by_id(self, faction_id):
        with sqlite3.connect(self.database_path) as conn:
            cursor = conn.cursor()
            cursor.execute(f'SELECT name, color FROM factions WHERE id = \"{faction_id}\"')
            return cursor.fetchall()

    def get_faction_by_name(self, faction_name):
        with sqlite3.connect(self.database_path) as conn:
            cursor = conn.cursor()
            cursor.execute(f'SELECT id, color FROM factions WHERE name = \"{faction_name}\"')
            return cursor.fetchall()
