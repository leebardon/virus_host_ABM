import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import random
from scipy.ndimage import convolve

# Define grid size
GRID_SIZE = (20, 20)

class Bacteria:

    def __init__(self, group_id, growth_rate, resistance, x, y):
        """
        Instantiates an instance of the Bacteria class (i.e. creates a B)

        Args:
            self: Instance of B
            group_id (Int64): Functional group id
            growth_rate (Float64): Rate of reproduction
            resistance (Float64): Resistance to infection 
            x (Int64): X coordinate on grid
            y (Int64) Y coordinate on grid

        """
        self.group_id = group_id
        self.growth_rate = growth_rate
        self.resistance = resistance
        self.biomass = 1.0
        self.infected = False
        self.x = x
        self.y = y
        
            
    def move(self, grid_size):
        """
        Moves B one grid cell in a random direction (or stays in current location)

        Args:
            grid_size (tuple)
        """
        dx, dy = random.choice([(0,1), (1,0), (0,-1), (-1,0), (0,0)])
        self.x = (self.x + dx) % grid_size[0]
        self.y = (self.y + dy) % grid_size[1]
        
    def grow(self):
        """
        If B is not infected, B will grow as a function of maximum uptake rate and substrate concentration.

        Returns:
            uptake: Zero if infected, Float otherwise
        """
        if not self.infected:
            uptake = self.growth_rate
            self.biomass += uptake
            return uptake
        return 0
    
    def check_if_infected(self, virus):
        """
        When B and V instances land on same grid cell, check if B is already in an infected state. 
        If not, check if V group_id is the same as B group_id. If true, if randomly selected number 
        between )-1 is higher than B resistance value, B state is set to Infected.

        Args:
            virus (object): Instance of V class.

        Returns:
            Bool: Uninfected B instance is infected (return True) or not (return False)
        """
        if not self.infected and virus.group_id == self.group_id:
            if random.random() > self.resistance:
                self.infected == True 
                return True
        return False
    

class Virus:  
    def __init__(self, group_id, x, y):
        """
        Instantiates an instance of the Virus class (i.e. creates a V)

        Args:
            self: Instance of V
            group_id (Int64): V group id
            x (Int64): X coordinate on grid
            y (Int64) Y coordinate on grid

        """
        self.group_id = group_id
        self.x = x
        self.y = y


    #TODO create Helper class (mixin?) so V and B can share move functionality
    def move(self, grid_size):
        """
        Moves V one grid cell in a random direction (or stays in current location)

        Args:
            grid_size (tuple)
        """
        dx, dy = random.choice([(0,1), (1,0), (0,-1), (-1,0), (0,0)])
        self.x = (self.x + dx) % grid_size[0]
        self.y = (self.y + dy) % grid_size[1]


def initialize_agents(num_bacteria, num_viruses, num_groups):
    """
    Function initializes B and V agents with specified group traits and random grid positions.
    Implements a B trade-off between growth rate and resistance to V infection.

    Args:
        num_bacteria (int): Number of B  to create.
        num_viruses (int): Number of V to create.
        num_groups (int): Number of B & V groups with distinct traits.

    Returns:
        tuple: Lists of initialized B and V.
    """
    bacteria, viruses = [], []
    for i in range(num_bacteria):
        group_id = i % num_groups
        growth_rate = 0.3 * (1 - group_id / num_groups)
        resistance = 1 - growth_rate
        x, y = np.random.randint(0, GRID_SIZE[0]), np.random.randint(0, GRID_SIZE[1])
        bacteria.append(Bacteria(group_id, growth_rate, resistance, x, y))
        
    for i in range(num_viruses):
        group_id = i % num_groups
        x, y = np.random.randint(0, GRID_SIZE[0]), np.random.randint(0, GRID_SIZE[1])
        viruses.append(Virus(group_id, x, y))
        
    return bacteria, viruses


def step(bacteria, viruses):
    """
    Perform one simulation step:
    - Update growth and movement of B
    - Check for infections and move V

    Args:
        bacteria (list): List of B objects.
        viruses (list): List of V objects.
    """
    for b in bacteria:
        b.move(GRID_SIZE)
        
    for v in viruses:
        for b in bacteria:
            if b.x == v.x and b.y == v.y:
                b.check_if_infected(v)
        v.move(GRID_SIZE)
        
