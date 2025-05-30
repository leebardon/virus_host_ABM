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
        self.infection_time = None
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
        
    def grow(self, dom_value):
        """
        If B is not infected, B will grow as a function of maximum uptake rate and dom concentration.

        Returns:
            uptake: Zero if infected, Float otherwise
        """
        if not self.infected:
            uptake = min(self.growth_rate * dom_value, dom_value)
            self.biomass += uptake
            return uptake
        return 0
    
    def check_if_infected(self, virus, timestep):
        """
        When B and V instances land on same grid cell, check if B is already in an infected state. 
        If not, check if V group_id is the same as B group_id. If true, if randomly selected number 
        between )-1 is higher than B resistance value, B state is set to Infected. Timestep of infection recorded.

        Args:
            virus (object): Instance of V class.

        Returns:
            Bool: Uninfected B instance is infected (return True) or not (return False)
        """
        if not self.infected and virus.group_id == self.group_id:
            if random.random() < self.resistance:
                self.infected = True
                self.infection_time = timestep
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
        
class DOMPool:
    def __init__(self, grid_size):
        """_summary_

        Args:
            grid_size (_type_): _description_
        """
        self.grid = np.full(grid_size, 10.0)

    def diffuse(self):
        """_summary_
        """
        kernel = np.array([[0.05, 0.1, 0.05],
                           [0.1,  0.4, 0.1],
                           [0.05, 0.1, 0.05]])
        self.grid = convolve(self.grid, kernel, mode='wrap')


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
        growth_rate = 0.1 + 0.2 * (1 - group_id / num_groups)
        resistance = 1 - growth_rate
        x, y = np.random.randint(0, GRID_SIZE[0]), np.random.randint(0, GRID_SIZE[1])
        bacteria.append(Bacteria(group_id, growth_rate, resistance, x, y))
        
    for i in range(num_viruses):
        group_id = i % num_groups
        x, y = np.random.randint(0, GRID_SIZE[0]), np.random.randint(0, GRID_SIZE[1])
        viruses.append(Virus(group_id, x, y))
        
    return bacteria, viruses
        

def step(bacteria, viruses, dom_pool, timestep):
    """
    Perform one simulation step:
    - Update growth and movement of B
    - Check for infections and move V

    Args:
        bacteria (list): List of B objects.
        viruses (list): List of V objects.
    """
    dom_pool.diffuse()
    new_viruses = []

    # Bacteria growth and movement
    for b in bacteria:
        dom_value = dom_pool.grid[b.x, b.y]
        uptake = b.grow(dom_value)
        dom_pool.grid[b.x, b.y] -= uptake
        b.move(GRID_SIZE)

    # Virus infection and movement
    for v in viruses:
        for b in bacteria:
            if b.x == v.x and b.y == v.y:
                b.check_infection(v, timestep)
        v.move(GRID_SIZE)

    # Apply mortality and process infections
    survivors = []
    for b in bacteria:
        natural_death_prob = B_LINEAR_MORT + B_QUADRATIC_MORT * b.biomass
        if random.random() < natural_death_prob:
            continue  # B dies

        if b.infected and timestep - b.infection_time >= INFECTION_LAG:
            for _ in range(V_BURST_SIZE):
                new_viruses.append(Virus(b.group_id, b.x, b.y))
            continue  # Infected B dies
        survivors.append(b)
    bacteria[:] = survivors

    # Viral decay
    viruses[:] = [v for v in viruses if random.random() > V_DECAY_RATE]
    viruses.extend(new_viruses)


def init_simulation(num_bacteria, num_viruses, num_groups):
    """
    Initialize the simulation state with bacteria, viruses, and DOM pool.
    Clears and sets global simulation state variables.
    
    Args:
        num_bacteria (Int): Number of B objects
        num_viruses (Int): Number of V objects
        num_groups (Int): Number of B groups of differing trait combinations
    """
    simulation_state = {
        "bacteria": [],
        "viruses": [],
        "bacteria_counts": [],
        "virus_counts": [],
        "times": []
    }

    bacteria, viruses = initialize_agents(num_bacteria, num_viruses, num_groups)
    dom_pool = DOMPool(GRID_SIZE)
    simulation_state["bacteria"] = bacteria
    simulation_state["viruses"] = viruses
    simulation_state["dom_pool"] = dom_pool
    simulation_state["bacteria_counts"].clear()
    simulation_state["virus_counts"].clear()
    simulation_state["times"].clear()
    
    return simulation_state




# Grid size
GRID_SIZE = (20, 20)

# Parameters
B_LINEAR_MORT = 0.01
B_QUADRATIC_MORT = 0.001
V_DECAY_RATE = 0.01
V_BURST_SIZE = 5
INFECTION_LAG = 5  # in timesteps
TIMESTEPS = 100