import numpy as np
import scipy.stats as sps
import mesa
import matplotlib.pyplot as plt


class Oil: 
    def __init__(self, base_price):
        self.price = base_price
        self.demand = 0
        self.supply = float('inf')

    def receive_demand(self, firm_id, quantity):
        self.demand[firm_id] = quantity
    
    def update_price(self):
        pass


class Gas:
    def __init__(self, base_price):
        self.price = base_price
        self.demand = {}
        self.supply = float('inf')

    def receive_demand(self, firm_id, quantity):
        self.demand[firm_id] = quantity
    
    def update_price(self):
        pass


class Electricity:
    def __init__(self, base_price):
        self.price = base_price
        self.demand = 0
        self.supply = float('inf')

    def receive_demand(self, firm_id, quantity):
        self.demand[firm_id] = quantity
    
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
                 model,
                 markup: float,
                 lab_prod: float,
                 wage: float,
                 good_per_oil: float,
                 good_per_gas: float,
                 good_per_elec: float,
                 alpha: float,
                 ):
        super().__init__(model)
        self.oil_demand = 0
        self.gas_demand = 0
        self.electricity_demand = 0
        self.good_per_oil = good_per_oil
        self.good_per_gas = good_per_gas
        self.good_per_elec = good_per_elec
        self.energy_cost = self.model.oil.price + self.model.gas.price + self.model.electricity.price
        self.output = 0
        self.wage = wage
        self.markup = markup
        self.lab_prod = lab_prod
        self.price = (1 + self.markup)*(self.wage/self.lab_prod + self.energy_cost)
        self.labor_demand = 0
        self.alpha = alpha

    def production(self):
        self.output = self.lab_prod * self.labor_demand ** self.alpha

    def demand_labor(self):
        self.labor_demand = (self.wage / (self.alpha * self.lab_prod * (self.price - self.energy_cost))) ** (1/(1 - self.alpha))

    def demand_energy(self):
        # compute energy needed (linear function of quantity produced)
        oil_quant = self.good_per_oil*self.outputs
        self.model.oil.receive_demand(self.unique_id, oil_quant)

        gas_quant = self.good_per_gas*self.output
        self.model.gas.receive_demand(self.unique_id, gas_quant)

        elec_quant = self.good_per_elec*self.output
        self.model.electricity.receive_demand(self.unique_id, elec_quant)




