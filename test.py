import numpy as np
import matplotlib.pyplot as plt
from firm_ABM import Simulation


parcel_size = [0.25, 0.5, 0.25]
price = 200
wage = 40000
land_size = 1000
NY = 5


model = Simulation(3, land_size, parcel_size, price, wage, NY)
for i in range(100):
    model.step()

