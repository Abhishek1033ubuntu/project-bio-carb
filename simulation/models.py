# simulation/models.py
import random
import numpy as np

class ProductionRack:
    """
    Represents an isolated 2D planar microfluidic biolithography slide housing 
    the engineered host organisms controlled by an Orthogonal Ribosome core.
    """
    def __init__(self, bay_id, weibull_scale, weibull_shape):
        self.bay_id = bay_id
        # Stagger initial ages to simulate a continuous operating plant
        self.age = random.uniform(0, 300) 
        self.weibull_scale = weibull_scale
        self.weibull_shape = weibull_shape
        self.output_yield = 1.0
        self.is_failed = False

    def calculate_decay(self):
        """
        Calculates metabolic decay and mutation drift using a Weibull distribution.
        Orthogonal Ribosome systems heavily buffer this scale.
        """
        self.output_yield = np.exp(-((self.age / self.weibull_scale) ** self.weibull_shape))
        if self.output_yield < 0.20:
            self.is_failed = True


class FactoryStateTracker:
    """
    Maintains quantitative tracking of raw materials, total outputs, 
    and robotic events across the entire runtime timeline.
    """
    def __init__(self):
        self.total_liters_produced = 0.0
        self.total_glucose_consumed_kg = 0.0
        self.total_swaps_performed = 0
        self.accumulated_feedstock_cost = 0.0
