import numpy as np
import matplotlib.pyplot as plt
from city_ABM import CityModel

num_house = 150
markup = np.array([0.2, 0.1, 0.3, 0.4, 0.5])
oil_prod = np.array([50, 100, 70, 30, 200])
gas_prod = np.array([50, 100, 70, 30, 200])
elec_prod = np.array([50, 100, 70, 30, 200])
lab_prod = np.array([75, 25, 150, 40, 10])
wage = np.array([100, 500, 200, 250, 250])
oil_demand = np.random.normal(loc=5400, scale=500, size=num_house)
gas_demand = np.random.normal(loc=6000, scale=500, size=num_house)
elec_demand = np.random.normal(loc=850, scale=100, size=num_house)
good_demand =np.random.normal(loc=50, scale=10, size=num_house)
initial_wealth = np.ones(5) * 10e6
alpha = np.array([0.3, 0.4, 0.33, 0.35, 0.45])

model = CityModel(num_firm=5,
                 num_house=num_house,
                 oil_base_price=0,
                 gas_base_price=0,
                 elec_base_price=0,
                 markup=markup,
                 wage=wage,
                 oil_prod=oil_prod,
                 gas_prod=gas_prod,
                 elec_prod=elec_prod,
                 oil_demand=oil_demand,
                 gas_demand=gas_demand,
                 elec_demand=elec_demand,
                 good_demand=good_demand,
                 lab_prod=lab_prod,
                 initial_wealth=initial_wealth,
                 alpha=alpha,
                 seed=None)
for i in range(5):
    model.step(i)
print(model.labor_employment)
print(model.res_wage)