import csv
import pandas as pd

def load_csv(file):
    first, second = [], []

    # out = {
    #     'simtime': self.params.SIMTIME,
    #     'num_stations': self.num_stations,
    #     'num_boats': self.params.num_boats,
    #     'capacity': self.params.capacity,
    #     'alpha': self.params.alpha,
    #     'beta': self.params.beta,
    #     'randomseed': self.params.randomseed,
    #     'mn_boatload_ratio': self.means["boatload_ratio"],
    #     'p_wts': self.means["P_wts"],
    #     'p_otb': self.means["P_otb"],
    #     'mn_waiting_demand': self.means["waiting_demand_station"],
    #     'dem_occ': self.accured_demand,
    #     'dem_left': sum(self.final_demand),
    #     'satisfied': self.satisfied
    # }


    dict = pd.read_csv(file, names=[
            'simtime',
            'num_stations',
            'num_boats',
            'capacity',
            'alpha',
            'beta',
            'randomseed',
            'mn_boatload_ratio',
            'p_wts',
            'p_otb',
            'mn_waiting_demand',
            'dem_occ',
            'dem_left',
            'satisfied'], skiprows=2)
    print(dict)


load_csv("out/HOHOcap10.csv")