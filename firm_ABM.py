import numpy as np
import pandas as pd
import mesa
import seaborn as sns
from scipy.optimize import linprog
import scipy.stats as sss


# define resource stocks
class Land:
    '''
    Manage land distirbution in the econmy

    Attributes:
        - area (float): Total area of land within reach of the economy
        - parcels (dict[parcel ID, share of land]): Maps instance of Parcel to 
        their share of the overall land available
        - ownership (dict[agent ID, parcel ID]): maps parcels to their owner
    '''
    def __init__(self, model, size):
        self.area = size
        self.parcels = {}
        self.ownership = {}
        self.shock = []
    
    def weather_shock(self):
        '''Generate weather shock affecting yield for all parcels'''
        W = sss.norm.rvs(loc=0, scale=0.255)
        self.shock.append(W)

class Parcel(mesa.Agent):
    '''
    Represent the dynamics of each individual parcels

    Attributes:
        - health (float in [0,1]): captures the health of the parcel.
        - yld (float): captures the yield in mass per surface of the parcel.
        - use (bool): True if land is being used to grow crop, False ow.
    '''
    def __init__(self,  model):
        super().__init__(model)
        self.health = 1
        self.use = True
        self.yld = []
    
    def cycle(self, model):
        # generate pre-weather yield.
        fert = 0.5 + 1.5*self.health

        # account for weather shock
        shock = self.model.land.shock[-1]
        self.yld.append(fert*(1 + shock))
        
        # degrade land
        if self.use:
            self.health *= 0.95
        else:
            self.health = min(1, self.health*1.05)


class Simulation(mesa.Model):
    def __init__(self, n, seed=None):
        super().__init__(seed=seed)
        self.land = Land(self, size=100)
        self.num_agents = n
        Parcel.create_agents(model=self, n=n)
        

    def step(self):
        self.agents.shuffle_do("cycle")




# define econmic actors 
class Capitalist(mesa.Agent):
    def __init__(self, model, share):
        super.__init__(model)
        self.wealth = 0
        self.land = Land*share
        self.wheat = 0
        
    def grow(self, price, wage):
        EY = Land.yld_hist[-1]
        L = 1 
        land_used = int(EY*L*price - 2*wage > 0)
        if land_used == 1:
            self.land.use = True
            self.wheat =  L*Y




        









class Laborer(mesa.Agent):
     
    def __init__(self, model, age, wealth, res_wage):
        '''
        age: Age of the agent. Age determines the agent's ability to work
        wealth: capture accumulated wealth of the agent.
        res_wage: Resevation wage of the agent. Wage under which agent may be 
        willling to walk out or unionize.
        
        
        '''
        super.__init__(model)
        self.age = age
        self.wealth = wealth
        self.res_wage = res_wage

    def reserve_wage(self):
        '''
        Formulate reserve wage based on past indicator (prices, hunger, wealth, past wage).
        Heuristics choice making.
        '''
        


def diet_optimization(Wealth: float,
                      a: float,
                      P_m: float,
                      P_w: float,
                      C_m: float,
                      C_w: float,
                      Cal: float) -> np.array:
    '''
    Solve the linear optimaztion problem. Laborers are assumed to favor meat
    above wheat and thus seek to maximize the quantity of meat consumed w.r.t.
    (1) budget constraints, (2) calorie equality and (3) non-negativity.

    Solves:
        max U_a(Meat, Wheat) = a * Meat + (1-a) * Wheat - Meat * P_m - Wheat * P_w
        s.t. (1) Meat * P_m + Wheat * P_w <= Wealth
             (2) Meat * C_m + Wheat * C_w = Cal
             (3) Meat >= 0, Wheat >= 0

    '''
    # define terms 
    A = Wealth - (P_w * Cal) / C_w
    B = P_m - (P_w * C_m) / C_w

    # define slope
    S = (a - P_m - C_m/C_w*(1 - a - P_w))

    # define upper bound for meat := x
    if S > 0:
        x = np.min([A/B, Cal/C_m])
    else:
        x = 0