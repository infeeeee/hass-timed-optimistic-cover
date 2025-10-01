import time
import logging

_LOGGER = logging.getLogger(__package__)


class TravelCalculator:
    def __init__(
        self, travel_time_up: int, travel_time_down: int, position: int = 0
    ) -> None:
        self.travel_time_up = travel_time_up
        self.travel_time_down = travel_time_down

        self.current_position = position

        self.current_travel: None | Travel = None

    def set_position(self, target_position):
        self.current_travel = Travel(self, target_position)

    def stop_travel(self):
        if self.current_travel:
            self.current_position = self.current_travel.current_position
            self.current_travel = None

    def get_relative_direction(self, target_position) -> int:
        rel_pos = target_position - self.current_position
        if rel_pos == 0:
            return 0
        return rel_pos / abs(rel_pos)

    @property
    def position_reached(self):
        if self.current_travel is None:
            return True
        if self.current_travel.target_position == self.current_position:
            self.stop_travel()
            return True
        return False

    @property
    def current_position(self):
        if self.current_travel is not None:
            self._current_position = self.current_travel.current_position
        return self._current_position

    @current_position.setter
    def current_position(self, position: int):
        position = max(0, position)
        position = min(100, position)
        self._current_position = position

    @property
    def direction(self):
        if self.current_travel is None:
            return 0
        else:
            return self.current_travel.direction


class Travel:
    def __init__(self, tc: TravelCalculator, target_position) -> None:
        self.start_position = tc.current_position
        self.target_position = target_position
        self.relative_position = self.target_position - self.start_position

        if self.relative_position == 0:
            raise ValueError

        self.start_time = time.time()

        travel_time_full = (
            tc.travel_time_up if self.relative_position > 0 else tc.travel_time_down
        )

        self.travel_time = travel_time_full * abs(self.relative_position) / 100

    @property
    def direction(self):
        return self.relative_position / abs(self.relative_position)

    @property
    def current_position(self):
        progress = (time.time() - self.start_time) / self.travel_time
        position = self.start_position + self.relative_position * progress
        return int(position)
