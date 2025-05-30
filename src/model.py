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
                b.check_if_infected(v, timestep)
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



def animate_simulation(steps=100):
    """
    Run and animate the agent-based model with real-time visualization:
    - Left: grid view of DOM, bacteria, and viruses
    - Right: time series of total bacterial and viral abundances

    Args:
        steps (int): Number of simulation steps to animate.
    """
    bacteria = simulation_state["bacteria"]
    viruses = simulation_state["viruses"]
    dom_pool = simulation_state["dom_pool"]
    times = simulation_state["times"]
    bacteria_counts = simulation_state["bacteria_counts"]
    virus_counts = simulation_state["virus_counts"]

    fig, (ax_grid, ax_plot) = plt.subplots(1, 2, figsize=(12, 6))
    plt.tight_layout()

    dom_img = ax_grid.imshow(dom_pool.grid.T, cmap='Blues', origin='lower', alpha=0.5)
    scat_bac = ax_grid.scatter([], [], c=[], cmap='viridis', vmin=0.5, vmax=5, s=35, edgecolor='k', label='Bacteria')
    scat_vir = ax_grid.scatter([], [], c='red', marker='x', s=40, label='Viruses')
    ax_grid.set_xlim(0, GRID_SIZE[0])
    ax_grid.set_ylim(0, GRID_SIZE[1])
    ax_grid.set_title("Grid View")
    ax_grid.legend()

    line_bac, = ax_plot.plot([], [], label='Bacteria')
    line_vir, = ax_plot.plot([], [], label='Viruses')
    ax_plot.set_xlim(0, steps)
    ax_plot.set_ylim(0, len(bacteria) + len(viruses))
    ax_plot.set_title("Population Over Time")
    ax_plot.set_xlabel("Time Step")
    ax_plot.set_ylabel("Count")
    ax_plot.legend()

    def init():
        """
        Initialize animation with empty datasets.
        """
        scat_bac.set_offsets(np.empty((0, 2)))
        scat_bac.set_array(np.array([]))
        scat_vir.set_offsets(np.empty((0, 2)))
        line_bac.set_data([], [])
        line_vir.set_data([], [])
        return scat_bac, scat_vir, dom_img, line_bac, line_vir

    def update(frame):
        """
        Update function called for each frame of the animation.
        Advances simulation by one step and updates the visualizations.

        Args:
            frame (int): The current frame number.

        Returns:
            tuple: Updated matplotlib artists for rendering.
        """
        step(bacteria, viruses, dom_pool, frame)

        bac_pos = np.array([[b.x, b.y] for b in bacteria])
        bac_color = np.array([b.biomass for b in bacteria])
        vir_pos = np.array([[v.x, v.y] for v in viruses])

        scat_bac.set_offsets(bac_pos)
        scat_bac.set_array(bac_color)
        scat_vir.set_offsets(vir_pos)
        dom_img.set_array(dom_pool.grid.T)

        times.append(frame)
        bacteria_counts.append(len(bacteria))
        virus_counts.append(len(viruses))

        line_bac.set_data(times, bacteria_counts)
        line_vir.set_data(times, virus_counts)
        ax_plot.set_xlim(0, max(10, frame + 1))
        ax_plot.set_ylim(0, max(max(bacteria_counts), max(virus_counts)) + 10)

        return scat_bac, scat_vir, dom_img, line_bac, line_vir
    

    ani = animation.FuncAnimation(fig, update, init_func=init, frames=steps, interval=200, blit=True)
    plt.show()


# Grid size
GRID_SIZE = (20, 20)

# Parameters
B_LINEAR_MORT = 0.01
B_QUADRATIC_MORT = 0.001
V_DECAY_RATE = 0.01
V_BURST_SIZE = 5
INFECTION_LAG = 5  # in timesteps
TIMESTEPS = 100
NUM_BAC = 50
NUM_VIR = 5
NUM_GROUPS = 2

simulation_state = init_simulation(NUM_BAC, NUM_VIR, NUM_GROUPS)
animate_simulation(TIMESTEPS)