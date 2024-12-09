

players_army_configuration = \
    {
        'default': {

        },
        'Shuan': {
            'faction': 'Orks',
            'detachment': 'Da Big Hunt',
            'army': {
                'units': [
                    {
                        'unit_name': 'Mozrog Skragbad',
                        'models': [
                            {
                                'name': 'Mozrog Skragbad',
                                'weapons': {
                                    'ranged': ['Thump gun'],
                                    'melee': ["Big Chompa\'s jaws", 'Gutrippa']
                                },
                                'warlord': True
                            }
                        ]
                    },
                    {
                        'unit_name': 'Beastboss + Beast Snagga Boyz',
                        'models': [
                            {
                                'name': 'Beastboss',
                                'weapons': {
                                    'ranged': ['Shoota'],
                                    'melee': ['Beast Snagga klaw', 'Beastchoppa']
                                },
                            },
                            {
                                'name': 'Beast Snagga Boy',
                                'amount': 8,
                                'weapons': {
                                    'ranged': ['Slugga'],
                                    'melee': ['Choppa']
                                },
                            },
                            {
                                'name': 'Beast Snagga Boy',
                                'amount': 1,
                                'weapons': {
                                    'ranged': ['Thump gun'],
                                    'melee': ['Close combat weapon']
                                },
                            },
                            {
                                'name': 'Beast Snagga Nob',
                                'amount': 1,
                                'weapons': {
                                    'ranged': ['Slugga'],
                                    'melee': ['Power snappa']
                                },
                            },
                        ]
                    },
                ],
            },
        },
        'Victor': {
            'faction': 'Astra Militarum',
            'detachment': 'Combined Regiment',
            'army': {
                'units': [
                    {
                        'unit_name': 'Tech-Priest Enginseer + Infantry Squad',
                        'models': [
                            {
                                'name': 'Tech-Priest Enginseer',
                                'weapons': {
                                    'ranged': ['Archeotech pistol'],
                                    'melee': ['Enginseer axe', 'Servo-arm']
                                },
                                'warlord': True
                            },
                            {
                                'name': 'Sergeant',
                                'amount': 1,
                                'weapons': {
                                    'ranged': ['Laspistol'],
                                    'melee': ['Close combat weapon']
                                },
                            },
                            {
                                'name': 'Guardsman',
                                'amount': 9,
                                'weapons': {
                                    'ranged': ['Lasgun'],
                                    'melee': ['Close combat weapon']
                                },
                            },
                        ]
                    },
                ],
            },
        },
        'Warrià': {
            'faction': 'Chaos Space Marines',
            'detachment': 'Veterans Of The Long War',
            'army': {
                'units': [
                    {
                        'unit_name': 'Abaddon da pussy + Termis',
                        'models': [
                            {
                                'name': 'Abaddon the Despoiler',
                                'weapons': {
                                    'melee': ['Talon of Horus', "Drach\'nyen"],
                                    'ranged': ['Talon of Horus']
                                },
                                'warlord': True
                            },
                            {
                                'name': 'Terminator Champion',
                                'amount': 1,
                                'weapons': {
                                    'ranged': ['Combi-bolter'],
                                    'melee': ['Accursed weapon']
                                }
                            },
                            {
                                'name': 'Chaos Terminator',
                                'amount': 4,
                                'weapons': {
                                    'ranged': ['Combi-bolter'],
                                    'melee': ['Accursed weapon']
                                }
                            }
                        ]
                    },
                ]
            },
        },
        'Uri': {
            'faction': 'Space Wolves',
            'detachment': '',
            'army': {}
        },
        'Berni': {
            'faction': 'Space Wolves',
            'detachment': '',
            'army': {}
        },
        'Marc': {
            'faction': 'Orks',
            'detachment': '',
            'army': {}
        }
    }
