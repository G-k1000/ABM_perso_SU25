import numpy as np
import scipy.stats as sps
import mesa
import matplotlib.pyplot as plt
import pandas as pd
import random


class Oil:
    '''
    Oil market management

    Parameters:
        - base_price: initial price of a unit of energy

    Attributes:
        - price: price of energy (in joules or kW/h not in power units)
        - supply: supply of oil availbale for consumption
    '''
    def __init__(self, base_price):
        self.price = base_price
        self.supply = float('inf')


class Gas:
    '''
    Gas market management

    Parameters:
        - base_price: initial price of a unit of energy

    Attributes:
        - price: price of energy (in joules or kW/h not in power units)
        - supply: supply of gas availbale for consumption
    '''
    def __init__(self, base_price):
        self.price = base_price
        self.supply = float('inf')


class Electricity:
    '''
    Electricity market management

    Parameters:
        - base_price: initial price of a unit of energy

    Attributes:
        - price: price of energy (in joules or kW/h not in power units)
        - supply: supply of electricity availbale for consumption
    '''
    def __init__(self, base_price):
        self.price = base_price
        self.supply = float('inf')


class Firm(mesa.Agent):
    '''
    Firm agents. Produce the goods of the economy by drawing from energy
    resources and employing labor.

    Parameters:
        - markup: profit target of firms as increments of real value
          created
        - lab_prod: labor productivity within the firm, i.e. amount of labor 
          required to procduce a single good.
        - wage: wage offered by firms in exchange of labor.
        - X_prod: amount of X needed for the production of a single output
          ceteris paribus
        - alpha: parameter of the Cobb-Douglas production function.

    Atrtributes:
        - labor_demand: labor demanded by firms maximizing profit function
        - energy_cost: energy cost per unit of output
        - X_demand: oil demanded by firms as a result of the profit maximization 
        process
        - gas_demand: gas demanded by firms as a result of the profit maximization
        process
        - electricity_demand: electricity demanded by firms as a result of the profit 
        maximization process
        - wealth: wealth of firms.

    '''
    def __init__(self,
                 model: mesa.Model,
                 markup: float,
                 lab_prod: float,
                 wage: float,
                 oil_prod: float,
                 gas_prod: float,
                 elec_prod: float,
                 initial_wealth: float,
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
        self.oil_prod = oil_prod
        self.gas_prod = gas_prod
        self.elec_prod = elec_prod

        # energy cost of producing a single good
        self.energy_cost = (self.model.oil.price * self.oil_prod
                            + self.model.gas.price * self.gas_prod
                            + self.model.elec.price * self.elec_prod)

        # price setting parameter
        self.wage = wage
        self.markup = markup
        self.lab_prod = lab_prod
        self.price = 0
        self.wealth = initial_wealth

        # parameter of production function
        self.alpha = alpha

        self.output = 0

    def set_price(self):
        '''
        Set price of goods.

        FIXED, NOT DYNAMIC
        '''
        self.price = (1 + self.markup)*(self.wage/self.lab_prod + self.energy_cost)

    def demand_labor(self):
        '''
        determine optimal amount of labor by maximizing profit.

        FIXED, NOT DYNAMIC
        '''
        self.labor_demand = np.floor(self.wage / (self.alpha * self.lab_prod * (self.price - self.energy_cost))) ** (1/(1 - self.alpha))
        print(self.labor_demand)

    def hire(self, laborer):
        '''
        hire labor if funds are sufficient and reservation wage
        is met.
        '''
        if self.wealth >= self.wage and laborer.res_wage <= self.wage:
            self.labor_hired += 1
            self.wealth -= self.wage
            laborer.wealth += self.wage
            laborer.is_employed = True
        else:
            laborer.is_employed = False

    def production(self):
        '''
        produce output given optimal amount of labor.
        '''
        self.output = np.floor(self.lab_prod * self.labor_hired ** self.alpha)
        self.oil_demand = self.oil_prod * self.output
        self.gas_demand = self.gas_prod * self.output
        self.elec_demand = self.elec_prod * self.output

    def buy_oil(self, price):
        if self.wealth > price * self.oil_demand:
            self.oil = self.oil_demand
            self.wealth -= price * self.oil_demand
            self.model.oil.supply -= self.oil_demand

    def buy_gas(self, price):
        if self.wealth > price * self.gas_demand:
            self.gas = self.gas_demand
            self.wealth -= price * self.gas_demand
            self.model.gas.supply -= self.gas_demand

    def buy_elec(self, price):
        if self.wealth > price * self.elec_demand:
            self.elec = self.elec_demand
            self.wealth -= price * self.elec_demand
            self.model.elec.supply -= self.elec_demand


class Farm(mesa.Agent):
    def __init__(self,
                 model,
                 land: float,
                 man_prod: float,
                 animal_prod: float, 
                 machine_prod: float,
                 oil_prod: float,
                 gas_prod: float,
                 elec_prod: float,
                 mechanization_lvl: float):
        super().__init__(model)
        self.land = land
        self.oil_prod = oil_prod
        self.gas_prod = gas_prod
        self.elec_prod = elec_prod
        self.mechanization_lvl = mechanization_lvl

    
    def demand_labor(self):

    def


class Household(mesa.Agent):
    '''
    Householf agents, provide labors to firm and consume their good
    as well as energy. 

    Parameter:
        - oil_cons: oil consomation within a given period of a time (exo parameter)
        - gas_cons: gas consomation within a given period of a time (exo parameter)
        - elec_cons: elec consomation within a given period of a time (exo parameter)
        - good_cons: good consomation within a given period of a time (exo parameter)

    Attribute:
        - wealth: wealth of the household
        - X_demand: household demand of good/resource X
        - X_owned: quantity of good/resources X owned

    Methods:
        - form_res_wage: household formulate a reservation wage which
          is the minimum wage for which they provide labor. This wage
          is informed by their desired level of consumption.
        - house_demand: communicate demand with market. For now its 
          useless, later it will be used to in the dynamic price mechanism
        - buy_X: buy resource/good X, ensuring that corresponding stocks
          are depleted. For now, household try to meet their demand by
          consuming as much as their wallet will alow below their demand 
          level.
    '''
    def __init__(self,
                 model,
                 oil_demand: float,
                 gas_demand: float,
                 elec_demand: float,
                 good_demand: float):
        super().__init__(model)

        # wealth and reservation wage
        self.wealth = 0
        self.res_wage = 0

        # good and energy demand
        self.oil_demand = oil_demand
        self.gas_demand = gas_demand
        self.elec_demand = elec_demand
        self.good_demand = good_demand

        # good and energy possesion
        self.oil_owned = 0
        self.gas_owned = 0
        self.elec_owned = 0
        self.good_owned = 0

        # employment status
        self.is_employed = False

    def form_res_wage(self):
        self.res_wage = (self.oil_demand * self.model.oil.price
                         + self.gas_demand * self.model.gas.price
                         + self.elec_demand * self.model.elec.price
                         + self.good_demand * self.model.good_market.price)

    def house_demand(self):
        self.model.oil.receive_demand(self.oil_cons)
        self.model.gas.receive_demand(self.gas_cons)
        self.model.elec.receive_demand(self.elec_cons)
        self.model.good_market.receive_demand(self.good_cons)

    def buy_oil(self, price):
        '''
        For now, as long as household has money, oil demand is 
        always met. 
        '''
        if self.wealth > price * self.demand_oil:
            self.oil_owned = self.demand_oil
            self.wealth -= price * self.demand_oil

    def buy_gas(self, price):
        '''
        For now, as long as household has money, gas demand is 
        always met. 
        '''
        if self.wealth > price * self.demand_gas:
            self.gas_owned = self.demand_gas
            self.wealth -= price * self.demand_gas

    def buy_oil(self, price):
        '''
        For now, as long as household has money, electricity demand is
        always met.
        '''
        if self.wealth > price * self.demand_elec:
            self.elec_owned = self.demand_elec
            self.wealth -= price * self.demand_elec

    def buy_good(self, firm):
        '''
        firms buys good from the same company until their demand is met or the firms
        runs out of goods.
        '''
        # check how much good could be bought given budget
        allowance = np.floor(self.wealth / firm.price)

        # check firm stock and pick lowest
        goods_purchased = min(allowance, firm.output)

        # update firm and household stock and wealth
        self.good_owned += goods_purchased
        self.wealth -= goods_purchased * firm.price
        firm.output -= goods_purchased
        firm.wealth += goods_purchased * firm.price


class GoodMarket:
    '''
    Manages the goods market. matches demand to supply

    Parameter:
    - None

    Attribute:
    - demand: dictionnary mapping household to their demand
      for good. Keeps data for the whole life of the model. 
      (for now this demand is fixed, will be useful when dynamic)
    - supply: dictionnary mapping firm to their supply.
      Keeps data for the whole life of the model.
    - price_catalog: dictionnary mapping firm to the price of good.
      Keeps data for the whole life of the model. 
      (will be useful when price are dynamic)

    Method:
    - match_supply: match firms goods to buying household making sure
      money is transferred from households to firm properly and there 
      is no consumption beyond available stock.
    - receive_X: update the data frame pertaining to attribute X.
    '''
    def __init__(self, model):
        # records
        self.demand = None
        self.supply = None
        self.price = None
        self.model = model

    def update_market(self, past_price: np.array):
        self.price = past_price.mean()

    def match_supply(self):
        # define priority list in matching
        selling_firm = sorted(
            [firm for firm in self.model.agents if isinstance(firm, Firm) and firm.output > 0],
            key=lambda firm: firm.price
        )
        buying_house = [house for house in self.model.agents if isinstance(house, Household) and house.wealth > 0]
        random.shuffle(buying_house)
        for house in buying_house:
            while house.good_demand < house.good_owned:
                # Check wether there are still goods available and if household can
                # afford the cheapest available option.
                if not selling_firm or house.wealth < selling_firm[0].price:
                    break

                house.buy_good(selling_firm[0])

                # if firm runs out remove it.
                if selling_firm[0].output == 0:
                    selling_firm.remove(selling_firm[0])


class LaborMarket:
    def __init__(self, model):
        # records
        self.res_wage = None
        self.firm_wage = None
        self.labor_employed = None
        self.labor_unemployed = None
        self.model = model

    def match_labor(self):
        # get priority list (for now highest paying firms first)
        hiring_firm = sorted(
            [firm for firm in self.model.agents if isinstance(firm, Firm) and firm.labor_demand > 0],
            key=lambda firm: firm.wage,
            reverse=True
        )
        working_house = [house for house in self.model.agents if isinstance(house, Household)]
        random.shuffle(working_house)

        # hire labor 1 by 1 from priority list until labor needs are met,
        # firm fund are insufficient or labor is scarce.
        for firm in hiring_firm:
            while firm.labor_hired < firm.labor_demand and firm.wealth > firm.wage:

                # check if there's labor left
                if not working_house:
                    break

                # Get next available worker, hire if reservation wage is met.
                worker = working_house.pop(0)
                if worker.res_wage <= firm.wage:
                    firm.hire(worker)


class CityModel(mesa.Model):
    def __init__(self,
                 num_firm: int,
                 num_house: int,
                 oil_base_price: float,
                 gas_base_price: float,
                 elec_base_price: float,
                 markup: np.array,
                 wage: np.array,
                 oil_prod: np.array,
                 gas_prod: np.array,
                 elec_prod: np.array,
                 oil_demand: np.array,
                 gas_demand: np.array,
                 elec_demand: np.array,
                 good_demand: np.array,
                 lab_prod: np.array,
                 initial_wealth: np.array,
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
                        oil_prod=oil_prod[i],
                        gas_prod=gas_prod[i],
                        elec_prod=elec_prod[i],
                        initial_wealth=initial_wealth[i],
                        alpha=alpha[i])
            self.agents.add(firm)
            self.firm[firm.unique_id] = firm

        self.house = {}
        for i in range(num_house):
            house = Household(model=self,
                              oil_demand=oil_demand[i],
                              gas_demand=gas_demand[i],
                              elec_demand=elec_demand[i],
                              good_demand=good_demand[i])
            self.agents.add(house)
            self.house[house.unique_id] = house

        # instantiate markets and initialize records
        self.labor_market = LaborMarket(self)
        self.res_wage = pd.DataFrame(index=range(self.num_house))
        self.firm_wage = pd.DataFrame(index=range(self.num_firm))
        self.labor_employment = pd.DataFrame(index=range(self.num_house))
        self.labor_demand = pd.DataFrame(index=range(self.num_firm))

        self.good_market = GoodMarket(self)
        self.good_demand = pd.DataFrame(index=range(self.num_house))
        self.good_price = pd.DataFrame(index=range(self.num_firm))
        self.good_supply = pd.DataFrame(index=range(self.num_firm))

    def step(self, t):
        # (1) firms set price of goods (+ update records)
        self.agents_by_type[Firm].shuffle_do('set_price')
        self.good_price[f'step_{t}'] = [f.price for f in self.firm.values()]

        # get average price
        self.good_market.price = self.good_price[f'step_{t}'].mean()

        # (2) laborer form reservation wage (+ update record)
        self.agents_by_type[Household].shuffle_do('form_res_wage')
        self.res_wage[f'step_{t}'] = [h.res_wage for h in self.house.values()]

        # update non-dynamic records for the hell of it
        self.firm_wage[f'step_{t}'] = [f.wage for f in self.firm.values()]
        self.good_demand[f'step_{t}'] = [h.good_demand for h in self.house.values()]

        # (3) firm set labor need (+ update record)
        self.agents_by_type[Firm].shuffle_do('demand_labor')
        self.labor_demand[f'step_{t}'] = [f.labor_demand for f in self.firm.values()]

        # (4) buy energy need
        self.agents_by_type[Firm].shuffle_do('buy_oil', self.oil.price)
        self.agents_by_type[Firm].shuffle_do('buy_gas',self.gas.price)
        self.agents_by_type[Firm].shuffle_do('buy_elec',self.elec.price)

        # (5) hire labor (+ update records)
        self.labor_market.match_labor()
        self.labor_employment[f'step_{t}'] = [h.is_employed for h in self.house.values()]

        # (6) make good (+ update record)
        self.agents_by_type[Firm].shuffle_do('production')
        self.good_supply[f'step_{t}'] = [f.output for f in self.firm.values()]

        # (7) sell good
        self.good_market.match_supply()

        # # firm buy energy need
        # self.firm.shuffle_do('buy_oil')
        # self.firm.shuffle_do('buy_gas')
        # self.firm.shuffle_do('buy_elec')

        # # house buy energy need
        # self.firm.shuffle_do()
        # self.firm.shuffle_do()
        # self.firm.shuffle_do()




        
