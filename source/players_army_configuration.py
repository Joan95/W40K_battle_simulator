

players_army_configuration = \
    {
        'default': {
            'faction': None,
            'detachment': None,
            'characters': [
                {
                    'name': None,
                    'weapons': {
                        'melee': [],
                        'ranged': []
                    },
                    'warlord': False,
                    'leading': None,
                }
            ],
            'battleline': [
                {
                    'name': None,
                    'weapons': {
                        'melee': [],
                        'ranged': []
                    },
                }
            ],
            'dedicated_transports': [
                {
                    'name': None,
                    'weapons': {
                        'melee': [],
                        'ranged': []
                    },
                    'is_transport': False,
                }
            ],
            'other_datasheets': [
                {
                    'name': None,
                    'weapons': {
                        'melee': [],
                        'ranged': []
                    },
                    'is_transport': False,
                }
            ],
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
                        'unit_name': 'Beast Snagga Boyz',
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
        'Warrià': {
            'faction': 'Chaos Space Marines',
            'detachment': 'Veterans Of The Long War',
            'army': {
                'characters': [
                    {
                        'name': 'Abaddon the Despoiler',
                        'weapons': {
                            'melee': ['Talon of Horus', "Drach\'nyen"],
                            'ranged': ['Talon of Horus']
                        },
                        'warlord': True
                    }
                ],
                'battleline': [],
                'dedicated_transports': [],
                'other_datasheets': [],
            },
        },
        'Uri': {
            'faction': 'Orks',
            'detachment': 'Da Big Hunt',
            'characters': [
                {
                    'name': 'Mozrog Skragbad',
                    'weapons': {
                        'melee': ["Big Chompa\'s Jaws", 'Gutrippa'],
                        'ranged': ['Thump Gun']
                    },
                    'warlord': True
                }
            ],
            'battleline': [],
            'dedicated_transports': [],
            'other_datasheets': [],
        },
        'Berni': {
            'faction': 'Orks',
            'detachment': 'Da Big Hunt',
            'characters': [
                {
                    'name': 'Mozrog Skragbad',
                    'weapons': {
                        'melee': ["Big Chompa\'s Jaws", 'Gutrippa'],
                        'ranged': ['Thump Gun']
                    },
                    'warlord': True
                }
            ],
            'battleline': [],
            'dedicated_transports': [],
            'other_datasheets': [],
        },
        'Marc': {
            'faction': 'Orks',
            'detachment': 'Da Big Hunt',
            'characters': [
                {
                    'name': 'Mozrog Skragbad',
                    'weapons': {
                        'melee': ["Big Chompa\'s Jaws", 'Gutrippa'],
                        'ranged': ['Thump Gun']
                    },
                    'warlord': True
                }
            ],
            'battleline': [],
            'dedicated_transports': [],
            'other_datasheets': [],
        },
    }

