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
        - ownership (dict[agent ID, parcel size]): parcel and owners have same ID, map
        agent to parcel size. parcel 1 is not owned.
    '''
    def __init__(self, model, area):
        self.area = area
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
    def __init__(self,  model, natural_yld):
        super().__init__(model)
        self.health = 1
        self.use = True
        self.yld = [natural_yld]
    
    def get_yld(self, model):
        # generate pre-weather yield.
        fert = 0.5 + 1.5*self.health

        # account for weather shock
        shock = self.model.land.shock[-1]
        self.yld.append(fert*(1 + shock))

     def degrade_par(self):
        # degrade land
        if self.use:
            self.health *= 0.95
        else:
            self.health = min(1, self.health*1.05)




# define econmic actors 
class Capitalist(mesa.Agent):
    def __init__(self, model):
        super.__init__(model)
        self.wealth = 0
        self.wheat = 0
        self.parcel = None
        self.parcel_size = None
        
    def grow(self, price, wage):
        # get expected yield (previous yield)
        EY = self.parcel.yld[-2]

        L = self.parcel_size * self.model.land.area
        land_used = int(EY*L*price - 2*wage > 0)
        if land_used == 1:
            self.model.parcel.use = True
            self.wheat += L*self.model.parcel.yld
        else: 
            self.model.parcel.use = False

    def sell(self, price, wage):
        if self.wheat != 0:
            self.wealth += self.wheat*price - 2*self.parcel_size*wage




class Simulation(mesa.Model):
    def __init__(self, n: int, land_size: float, parcel_size: list, seed=None):
        super().__init__(seed=seed)
        self.num_agents = n

        # create parcel and agents
        self.parcel = Parcel.create_agents(model=self, n=n+1)
        self.capitalist = Capitalist.create_agents(model=self, n=n+1)

        # create land environment and distribute parcels
        self.land = Land(self, size=land_size)
        for cap, par in zip(self.capitalist, self.parcel):
            cap.parcel = par
        for cap, size in zip(self.capitalist, parcel_size):
            cap.parcel_size = size
        

    def step(self):
        # generate weather shock
        self.land.weather_shock()

        # get parcel yields
        self.parcel.shuffle_do("")

        # grow crops

        # sell wheat

        # degrade land
      









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