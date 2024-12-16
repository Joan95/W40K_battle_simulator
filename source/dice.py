import random
import re
from logging_handler import log


class Dices:
    def __init__(self, dice_owner):
        self.dice_owner = dice_owner
        self.last_roll_dice_values = 0
        self.last_roll_dice_value = 0
        self.last_roll_dice_sides = 0
        self.last_roll_modifier = 0
        self.last_roll_dice_count = 0

    def roll_dices(self, number_of_dices=1, sides=6):
        """
        Roll dice(s) with various formats like 'D6+1', 'D3', '2D6'.

        :param number_of_dices: Number of dices or a format string
        :param sides: Number of sides of the dice (default 6)
        :return: List of dice roll results
        """
        self.last_roll_dice_values = list()
        self.last_roll_modifier = 0

        # If number_of_dices is in format like 'D6+1', 'D3', '2D6'
        if isinstance(number_of_dices, str) and 'D' in number_of_dices:
            match = re.match(r'(\d*)D(\d+)([+-]\d+)?', number_of_dices)
            if match:
                self.last_roll_dice_count = int(match.group(1)) if match.group(1) else 1
                self.last_roll_dice_sides = int(match.group(2))
                self.last_roll_modifier = int(match.group(3)) if match.group(3) else 0

                for _ in range(self.last_roll_dice_count):
                    self.last_roll_dice_values.append(random.randint(1, self.last_roll_dice_sides))

                log(f'[{self.dice_owner}\'s dice(s)] Rolling #{self.last_roll_dice_count} dice(s) of '
                    f'{self.last_roll_dice_sides} sides with a '
                    f'modifier of +{self.last_roll_modifier}. Result: {self.last_roll_dice_values} + '
                    f'{self.last_roll_modifier}')
                # Apply the modifier to the total sum of dice rolls
                self.last_roll_dice_value = sum(self.last_roll_dice_values) + self.last_roll_modifier
            else:
                raise ValueError("Invalid dice format")
        else:
            # Handle the case where number_of_dices is a simple integer
            self.last_roll_dice_count = int(number_of_dices)
            self.last_roll_dice_sides = sides

            for _ in range(self.last_roll_dice_count):
                self.last_roll_dice_values.append(random.randint(1, self.last_roll_dice_sides))

            log(f'[{self.dice_owner}\'s dice(s)] Rolling #{self.last_roll_dice_count} dice(s) of '
                f'{self.last_roll_dice_sides} sides with a '
                f'modifier of +{self.last_roll_modifier}. Result: {self.last_roll_dice_values} + '
                f'{self.last_roll_modifier}')
            self.last_roll_dice_value = sum(self.last_roll_dice_values)

        return self.last_roll_dice_value
