'''Level progression: intro -> entry -> active combat -> clear -> next level.'''

from . import config as C


class LevelManager:
    '''Owns the level number and the within-level phase.

    Phases: 'intro' (WAVE N banner), 'entry' (enemies flying in),
    'active' (combat), 'clear' (banner, then next level starts).
    '''
    def __init__(self):
        '''Start at level 1 with its parameters loaded.'''
        self.level = 1
        self.phase = 'intro'
        self.timer = 0.0

    def start(self) -> None:
        '''Advance to the next level and load its parameters.'''
        self.level = 1
        self.phase = 'intro'
        self.timer = 2.4

    @property
    def params(self) -> dict:
        '''Parameters dict for the current level.'''
        return C.level_params(self.level)

    def update(self, dt: float, fleet: 'Fleet', sound: 'SoundBank') -> str:
        '''Advance the level machine. Returns the current phase.'''
        if self.phase == 'intro':
            self.timer -= dt

            if self.timer <= 0:
                fleet.setup(self.level)
                self.phase = 'entry'
        elif self.phase == 'entry':
            if fleet.all_in_formation():
                self.phase = 'active'
        elif self.phase == 'active':
            if len(fleet.alive_enemies()) == 0:
                self.phase = 'clear'
                self.timer = 2.6
                sound.play('level_clear')
        elif self.phase == 'clear':
            self.timer -= dt

            if self.timer <= 0:
                self.level += 1
                self.phase = 'intro'
                self.timer = 2.4

        return self.phase
