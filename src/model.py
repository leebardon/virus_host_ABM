import numpy as np
import matplotlib.pyplot as plt   
import random

# Define grid size
GRID_SIZE = (20, 20)

class Bacteria:

    def __init__(self, group_id, growth_rate, resistance, x, y):
        """
        Description of __init__

        Args:
            self (undefined):
            group_id (undefined):
            growth_rate (undefined):
            resistance (undefined):
            x (undefined):
            y (undefined):

        """
        self.group_id = group_id
        self.growth_rate = growth_rate
        self.resistance = resistance
        self.biomass = 1.0
        self.infected = False
        self.x = x
        self.y = y
        
            
    def move(self, grid_size):
        """_summary_

        Args:
            grid_size (_type_): _description_
        """
        dx, dy = random.choice([(0,1), (1,0), (0,-1), (-1,0), (0,0)])
        self.x = (self.x + dx) % grid_size[0]
        self.y = (self.y + dy) % grid_size[1]
        
        
    def grow(self):
        """_summary_

        Returns:
            _type_: _description_
        """
        if not self.infected:
            uptake = self.growth_rate
            self.biomass += uptake
            return uptake
        return 0
    
    def check_if_infected(self, virus):
        """_summary_

        Args:
            virus (_type_): _description_

        Returns:
            _type_: _description_
        """
        if not self.infected and virus.group_id == self.group_id:
            if random.random() > self.resistance:
                self.infected == True 
                return True
        return False
    

