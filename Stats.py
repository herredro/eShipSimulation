import matplotlib.pyplot as plt
import json

class Stats_Boat:
    def __init__(self, boat):
        self.boat = boat
        self.luggage = {}
        self.boatrewards = {}
        self.pickedup = {}
        self.droppedoff = {}
        self.droveto = {}

    def return_all_dicts(self):
        return [self.boatrewards, self.pickedup, self.droppedoff, self.droveto]

    def plot_free(self, dictionary, title="Plot"):
        dict = dictionary
        fig, ax = plt.subplots(1, 2, figsize=(9, 3))
        plt.title(title)
        #for dict in dictionary:
        i=0
        for dict in dictionary:
            ax[i].step(dict.keys(), dict.values(), label='Boat %s' %self.boat.id)
            i+=1
            plt.legend()
        return plt






    def save_dict(self, dict):
        with open('data.txt', 'w') as outfile:
            json.dump(dict, outfile)

    def open_dict(self, dict):
        with open('data.txt') as json_file:
            data = json.load(json_file)
        print(type(data))
        print(data)

class Stats_Station:
    def __init__(self, map):
        self.map = map
        self.energy_supplied = {}
        self.usage_in_time = {}
        for station in map.get_all_stations():
            self.energy_supplied[station]=0
            self.usage_in_time[station] = {}
            self.usage_in_time[station][0] = 0


    def plot_step(self, dictionary, title="Plot"):
        fig, ax = plt.subplots()
        plt.title(title)
        for dict in dictionary:
            ax.step(dict.keys(), dict.values(), label="Station %s"%str(self.station))
            plt.legend()
        return ax
