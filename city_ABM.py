import numpy as np
import scipy.stats as sps
import mesa
import matplotlib.pyplot as plt


class Oil: 
    def __init__(self, base_price):
        self.price = base_price
        self.demand = 0
        self.supply = float('inf')

    def add_demand(self, quantity):
        self.demand += quantity
    
    def update_price(self):
        pass


class Gas:
    def __init__(self, base_price):
        self.price = base_price
        self.demand = 0
        self.supply = float('inf')

    def add_demand(self, quantity):
        self.demand += quantity
    
    def update_price(self):
        pass


class Electricity:
    def __init__(self, base_price):
        self.price = base_price
        self.demand = 0
        self.supply = float('inf')

    def add_demand(self, quantity):
        self.demand += quantity
    
    def update_price(self):
        pass


class Nitrate_producer(mesa.Agent):
    def __init__(self, model):
        super().__init__(model)
        self.demand = 0
        self.price = 0


class Firm:
    def __init__(self, model, markup, lab_prod, wage):
        super().__init__(model)
        self.oil_need = 0
        self.gas_need = 0
        self.electricity_need = 0
        self.output = 0
        elec_cost
        self.price = (1 + markup) * (wage/lab_prod)

    def

