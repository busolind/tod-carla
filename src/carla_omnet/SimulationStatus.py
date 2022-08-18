import enum


# (simulation_status, car_status)
class SimulationStatus(int, enum.Enum):
    RUNNING = 0
    FINISHED_OK = 1,
    FINISHED_ACCIDENT = 1,
    FINISHED_ERROR = -1

    @classmethod
    def is_finished(cls, status):
        return status in (cls.FINISHED_OK, cls.FINISHED_ACCIDENT, cls.FINISHED_ERROR)

    @property
    def simulation_status_value(self):
        return self.value[0]
