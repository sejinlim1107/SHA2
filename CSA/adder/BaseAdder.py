from abc import ABC, abstractmethod





class BaseAdder(ABC):
    _instance_count = 0
    def __init__(self, is_metric_mode=False):
        self.A = None
        self.B = None
        self.circuit = None
        self.result = None

        self.is_metric_mode = is_metric_mode
        self.id = str(BaseAdder._instance_count)  # use the counter as the unique id
        BaseAdder._instance_count += 1  # increment the counter


    @abstractmethod
    def create(self, a, b, is_metric_mode=False):
        pass

    def construct_circuit(self):
        pass
