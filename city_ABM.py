import numpy as np
import scipy.stats as sps
import mesa
import matplotlib.pyplot as plt
import pandas as pd
import random

class Oil: 
    def __init__(self, base_price):
        self.price = base_price
        self.demand = {}
        self.demand_total = 0
        self.supply = float('inf')

    def receive_demand(self, agent_id, quantity):
        self.demand[agent_id] = quantity
    
    def update_price(self):
        pass


class Gas:
    def __init__(self, base_price):
        self.price = base_price
        self.demand = {}
        self.demand_total = 0
        self.supply = float('inf')

    def receive_demand(self, agent_id, quantity):
        self.demand[agent_id] = quantity

    
    def update_price(self):
        pass


class Electricity:
    def __init__(self, base_price):
        self.price = base_price
        self.demand = {}
        self.demand_total = 0
        self.supply = float('inf')

    def receive_demand(self, agent_id, quantity):
        self.demand[agent_id] = quantity
    
    def update_price(self):
        pass


class Nitrate_producer(mesa.Agent):
    def __init__(self, model):
        super().__init__(model)
        self.demand = 0
        self.price = 0


class Firm(mesa.Agent):
    '''
    Firm agents. Produce the goods of the economy by drawing from energy 
    resources and employing labor.

    Atrtributes:
        - markup: profit target of firms as increments of real value
        created
        - lab_prod: labor productivity within the firm, i.e. amount of labor 
        required to procduce a single good.
        - wage: wage offered by firms in exchange of labor.
        - good_per_oil: amount of oil needed for the production of a single good.
        - good_per_gas: amount of gas needed for the production of a single good.
        - good_per_elec: amount of electricity needed for the production of 
        a single good.
        - alpha: parameter of the Cobb-Douglas production function.
        - labor_demand: labor demanded by firms that maximizes profit function
        - oil_demand: oil demanded by firms as a result of the profit maximization 
        process
        - gas_demand: gas demanded by firms as a result of the profit maximization
        process
        - electricity_demand: electricity demanded by firms as a result of the profit 
        maximization process

    '''
    def __init__(self,
                 model: mesa.Model,
                 markup: float,
                 lab_prod: float,
                 wage: float,
                 good_per_oil: float,
                 good_per_gas: float,
                 good_per_elec: float,
                 alpha: float,
                 ):
        super().__init__(model)
        # energy demanded by firms
        self.oil_demand = 0
        self.gas_demand = 0
        self.elec_demand = 0

        # labor demanded and hired
        self.labor_demand = 0
        self.labor_hired = 0

        # number of good per unit of X energy
        self.good_per_oil = good_per_oil
        self.good_per_gas = good_per_gas
        self.good_per_elec = good_per_elec

        # energy cost of producing a single good
        self.energy_cost = self.model.oil.price + self.model.gas.price + self.model.elec.price
        
        # price setting parameter
        self.wage = wage
        self.markup = markup
        self.lab_prod = lab_prod
        self.price = (1 + self.markup)*(self.wage/self.lab_prod + self.energy_cost)

        # parameter of production function
        self.alpha = alpha

        self.output = 0

    def production(self):
        '''
        produce output given optimal amount of labor.
        '''
        self.output = np.floor(self.lab_prod * self.labor_demand ** self.alpha)

    def demand_labor(self):
        '''
        determine optimal amount of labor by maximizing profit.
        '''
        self.labor_demand = np.floor(self.wage / (self.alpha * self.lab_prod * (self.price - self.energy_cost))) ** (1/(1 - self.alpha))

    def buy_oil(self, price):
        if self.wealth > price * self.oil_demand: 
            self.oil = self.oil_demand
            self.wealth -= price * self.oil_demand
    
    def buy_gas(self, price):
        if self.wealth > price * self.gas_demand: 
            self.gas = self.gas_demand
            self.wealth -= price * self.gas_demand

    def buy_oil(self, price):
        if self.wealth > price * self.elec_demand: 
            self.elec = self.elec_demand
            self.wealth -= price * self.elec_demand
    
    def sell_good(self):
        '''
        '''
        if self.output > 0:
            self.output -= 1
            self.wealth += self.price


    def demand_energy(self):
        '''
        demand energy to supplier
        '''
        # compute energy needed (linear function of quantity produced)
        oil_quant = self.good_per_oil*self.output
        self.model.oil.receive_demand(self.unique_id, oil_quant)

        gas_quant = self.good_per_gas*self.output
        self.model.gas.receive_demand(self.unique_id, gas_quant)

        elec_quant = self.good_per_elec*self.output
        self.model.electricity.receive_demand(self.unique_id, elec_quant)


class Household(mesa.Agent):
    def __init__(self,
                 model,
                 oil_cons: float,
                 gas_cons: float,
                 elec_cons: float,
                 good_cons:float):
        super().__init__(model)

        # consomation behavior
        self.oil_cons = oil_cons
        self.gas_cons = gas_cons
        self.elec_cons = elec_cons
        self.good_cons = good_cons

        # wealth and reservation wage
        self.wealth = 0
        self.res_wage = 0

        # good and energy demand
        self.demand_oil = 0
        self.demand_gas = 0
        self.demand_elec = 0
        self.demand_good = 0

        # good and energy possesion
        self.oil = 0
        self.gas = 0
        self.elec = 0
        self.good = 0


    def form_res_wage(self):
        self.res_wage = (self.oil_cons * self.model.oil.price
                         + self.gas_cons * self.model.gas.price
                         + self.elec_cons * self.model.elec.price
                         + self.good_cons * self.model.good_market.price)

    def house_demand(self):
        self.model.oil.receive_demand(self.oil_cons)
        self.model.gas.receive_demand(self.gas_cons)
        self.model.elec.receive_demand(self.elec_cons)
        self.model.good_market.receive_demand(self.good_cons)

    def buy_oil(self, price):
        if self.wealth > price * self.demand_oil: 
            self.oil = self.demand_oil
            self.wealth -= price * self.demand_oil
    
    def buy_gas(self, price):
        if self.wealth > price * self.demand_gas: 
            self.gas = self.demand_gas
            self.wealth -= price * self.demand_gas

    def buy_oil(self, price):
        if self.wealth > price * self.demand_elec: 
            self.elec = self.demand_elec
            self.wealth -= price * self.demand_elec

    def buy_good(self, price):
        if self.wealth > price and self.demand > self.good: 
            self.good += 1 
            self.wealth -= 1
        

class GoodMarket:
    '''
    Manages the goods market. matches demand to supply
    '''
    def __init__(self):
        self.demand = {}
        self.supply = {}
        self.price_catalog = {}

    def update_pricecat(self):
        for fid, firm in self.model.firm.items():
            self.price_catalog[fid] = [firm.price]


    
    def receive_demand(self, house_id, quantity):
        self.demand[house_id] = quantity

    def receive_supply(self, firm_id, quantity):
        self.supply[firm_id] = quantity

    def match_supply(self):
        # define priority list in matching: in future should account for proximity between 
        # firms and households.
        selling_firm = sorted(
            [firm for firm in self.model.agents if isinstance(firm, Firm) and firm.output > 0]
            key=lambda firm: firm.price
        )
        buying_house = [house for house in self.model.agent if isinstance(house, Household) and house.wealth > 0]
        random.shuffle(buying_house)
        while selling_firm: 
            for house in buying_house:
                if selling_firm

 




class LaborMarket:
    def __init__(self):
        pass

    def match(self):
        pass


class CityModel(mesa.Model):
    def __init__(self,
                 num_firm: int,
                 num_house: int,
                 oil_base_price: float,
                 gas_base_price: float,
                 elec_base_price: float,
                 markup: np.array,
                 wage: np.array,
                 good_per_oil: np.array,
                 good_per_gas: np.array,
                 good_per_elec: np.array,
                 oil_cons: np.array,
                 gas_cons: np.array,
                 elec_cons: np.array,
                 good_cons: np.array,
                 lab_prod: np.array,
                 alpha: np.array,
                 seed=None):
        super().__init__(seed=seed)
        self.num_firm = num_firm
        self.num_house = num_house

        # instantiate energy carriers
        self.oil = Oil(oil_base_price)
        self.gas = Gas(gas_base_price)
        self.elec = Electricity(elec_base_price)

        # instantiate firms and households
        self.firm = {}
        for i in range(num_firm):
            firm = Firm(model=self,
                        markup=markup[i],
                        lab_prod=lab_prod[i],
                        wage=wage[i],
                        good_per_oil=good_per_oil[i],
                        good_per_gas=good_per_gas[i],
                        good_per_elec=good_per_elec[i],
                        alpha=alpha[i])
            self.agents.add(firm)
            self.firm[firm.unique_id] = firm

        self.house = {}
        for i in range(num_house):
            house = Household(model=self,
                              oil_cons=oil_cons[i],
                              gas_cons=gas_cons[i],
                              elec_cons=elec_cons[i],
                              good_cons=good_cons[i])
            self.agents.add(house)
            self.house[house.unique_id] = house

        # instantiate markets
        self.labor_market = LaborMarket
        self.good_market = GoodMarket


        
