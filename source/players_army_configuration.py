

players_army_configuration = \
    {
        'default': {
            'faction': 'Orks',
            'detachment': 'Da Big Hunt',
            'army': {
                'units': [
                    {
                        'unit_name': 'Mozrog Skragbad + Beast Snaggas',
                        'models': [
                            {
                                'name': 'Mozrog Skragbad',
                                'weapons': {
                                    'RANGED': ['Thump gun'],
                                    'MELEE': ["Big Chompa\'s jaws", 'Gutrippa']
                                },
                                'warlord': True
                            },
                        ]
                    },
                    {
                        'unit_name': 'Beastboss + Beast Snagga Boyz',
                        'models': [
                            {
                                'name': 'Beastboss',
                                'weapons': {
                                    'RANGED': ['Shoota'],
                                    'MELEE': ['Beast Snagga klaw', 'Beastchoppa']
                                },
                            },
                            {
                                'name': 'Beast Snagga Boy',
                                'amount': 8,
                                'weapons': {
                                    'RANGED': ['Slugga'],
                                    'MELEE': ['Choppa']
                                },
                            },
                            {
                                'name': 'Beast Snagga Boy',
                                'amount': 1,
                                'weapons': {
                                    'RANGED': ['Thump gun'],
                                    'MELEE': ['Close combat weapon']
                                },
                            },
                            {
                                'name': 'Beast Snagga Nob',
                                'amount': 1,
                                'weapons': {
                                    'RANGED': ['Slugga'],
                                    'MELEE': ['Power snappa']
                                },
                            },
                        ]
                    },
                    {
                        'unit_name': 'Wurrboy + Beast Snagga Boyz',
                        'models': [
                            {
                                'name': 'Wurrboy',
                                'weapons': {
                                    'RANGED': ['Eyez of Mork'],
                                    'MELEE': ['Close combat weapon']
                                },
                            },
                            {
                                'name': 'Beast Snagga Boy',
                                'amount': 8,
                                'weapons': {
                                    'RANGED': ['Slugga'],
                                    'MELEE': ['Choppa']
                                },
                            },
                            {
                                'name': 'Beast Snagga Boy',
                                'amount': 1,
                                'weapons': {
                                    'RANGED': ['Thump gun'],
                                    'MELEE': ['Close combat weapon']
                                },
                            },
                            {
                                'name': 'Beast Snagga Nob',
                                'amount': 1,
                                'weapons': {
                                    'RANGED': ['Slugga'],
                                    'MELEE': ['Power snappa']
                                },
                            },
                        ]
                    },
                    {
                        'unit_name': 'Big Mek + Boyz',
                        'models': [
                            {
                                'name': 'Big Mek with Shokk Attack Gun',
                                'weapons': {
                                    'RANGED': ['Shokk attack gun'],
                                    'MELEE': ['Close combat weapon']
                                },
                            },
                            {
                                'name': 'Boy',
                                'amount': 4,
                                'weapons': {
                                    'RANGED': ['Slugga'],
                                    'MELEE': ['Choppa']
                                },
                            },
                            {
                                'name': 'Boy',
                                'amount': 4,
                                'weapons': {
                                    'RANGED': ['Shoota'],
                                    'MELEE': ['Close combat weapon']
                                },
                            },
                            {
                                'name': 'Boy',
                                'amount': 1,
                                'weapons': {
                                    'RANGED': ['Rokkit launcha'],
                                    'MELEE': ['Close combat weapon']
                                },
                            },
                            {
                                'name': 'Boss Nob',
                                'amount': 1,
                                'weapons': {
                                    'RANGED': ['Slugga'],
                                    'MELEE': ['Power klaw']
                                },
                            },
                        ]
                    }
                ],
            },
        },
        'Shuan': {
            'faction': 'Orks',
            'detachment': 'Da Big Hunt',
            'army': {
                'units': [
                    {
                        'unit_name': 'Mozrog Skragbad + Squighog Boyz',
                        'models': [
                            {
                                'name': 'Mozrog Skragbad',
                                'weapons': {
                                    'RANGED': ['Thump gun'],
                                    'MELEE': ["Big Chompa\'s jaws", 'Gutrippa']
                                },
                                'warlord': True
                            },
                            {
                                'name': 'Squighog Boy',
                                'amount': 3,
                                'weapons': {
                                    'RANGED': ['Saddlegit weapons'],
                                    'MELEE': ['Squig jaws', 'Stikka']
                                },
                            },
                            {
                                'name': 'Nob on Smasha Squig',
                                'amount': 1,
                                'weapons': {
                                    'RANGED': ['Slugga'],
                                    'MELEE': ['Big choppa', 'Squig jaws']
                                },
                            },
                        ]
                    },
                    {
                        'unit_name': 'Big Mek + Ranged Boyz',
                        'models': [
                            {
                                'name': 'Big Mek with Shokk Attack Gun',
                                'weapons': {
                                    'RANGED': ['Shokk attack gun'],
                                    'MELEE': ['Close combat weapon']
                                },
                            },
                            {
                                'name': 'Boy',
                                'amount': 8,
                                'weapons': {
                                    'RANGED': ['Shoota'],
                                    'MELEE': ['Close combat weapon']
                                },
                            },
                            {
                                'name': 'Boy',
                                'amount': 1,
                                'weapons': {
                                    'RANGED': ['Rokkit launcha'],
                                    'MELEE': ['Close combat weapon']
                                },
                            },
                            {
                                'name': 'Boss Nob',
                                'amount': 1,
                                'weapons': {
                                    'RANGED': ['Kombi-weapon'],
                                    'MELEE': ['Close combat weapon']
                                },
                            },
                        ]
                    }
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
                                    'RANGED': ['Archeotech pistol'],
                                    'MELEE': ['Enginseer axe', 'Servo-arm']
                                },
                                'warlord': True
                            },
                            {
                                'name': 'Sergeant',
                                'amount': 1,
                                'weapons': {
                                    'RANGED': ['Laspistol'],
                                    'MELEE': ['Close combat weapon']
                                },
                            },
                            {
                                'name': 'Guardsman',
                                'amount': 9,
                                'weapons': {
                                    'RANGED': ['Lasgun'],
                                    'MELEE': ['Close combat weapon']
                                },
                            },
                        ]
                    },
                ],
            },
        },
        'Guarrià': {
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
                                    'MELEE': ['Talon of Horus', "Drach\'nyen"],
                                    'RANGED': ['Talon of Horus']
                                },
                                'warlord': True
                            },
                            {
                                'name': 'Terminator Champion',
                                'amount': 1,
                                'weapons': {
                                    'RANGED': ['Combi-bolter'],
                                    'MELEE': ['Accursed weapon']
                                }
                            },
                            {
                                'name': 'Chaos Terminator',
                                'amount': 4,
                                'weapons': {
                                    'RANGED': ['Combi-bolter'],
                                    'MELEE': ['Accursed weapon']
                                }
                            }
                        ]
                    },
                    {
                        'unit_name': 'Termis',
                        'models': [
                            {
                                'name': 'Terminator Champion',
                                'amount': 1,
                                'weapons': {
                                    'RANGED': ['Combi-weapon'],
                                    'MELEE': ['Accursed weapon']
                                }
                            },
                            {
                                'name': 'Chaos Terminator',
                                'amount': 4,
                                'weapons': {
                                    'RANGED': ['Combi-weapon'],
                                    'MELEE': ['Accursed weapon']
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
