# Terra
# Copyright (C) 2026  Goodarz Mehr

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.

# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

'''Level progression'''

from . import config as C


class LevelManager:
    '''
    Manages the current level and its phase. The level machine has the
    following four phases: 'intro' (wave N banner), 'entry' (enemies flying
    in), 'active' (combat), 'clear' (banner, then next level starts).
    '''
    def __init__(self):
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
        '''
        Return the parameters dict for the current level.
        
        Returns:
            level parameters.
        '''
        return C.level_params(self.level)

    def update(self, dt: float, fleet: 'Fleet', sound: 'SoundBank') -> str:
        '''
        Advance the level state machine.
        
        Args:
            dt: frame delta (seconds).
            fleet: the Enemy fleet.
            sound: SoundBank instance for playing level clear sound.
            
        Returns:
            the current phase.
        '''
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
