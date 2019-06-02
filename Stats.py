
import json



class Stats:
    def __init__(self, sim):
        self.sim = sim

        self.final_demand = 0
        self.demand_in_time = {}
        self.usage_in_time = {}
        self.poisson_value = {}
        if sim.mode:
            self.mode = "Central"
        else:
            self.mode = "HOHO"

    def init(self):
        for station in self.sim.map.get_all_stations():
            self.demand_in_time[station] = {}
            self.demand_in_time[station][0] = 0
            self.usage_in_time[station] = {}
            self.usage_in_time[station][0] = 0
            self.poisson_value[station] = {}
        # Boat
        self.visited_stations = {}
        for boat in self.sim.cb.boats.values():
            self.visited_stations[boat] = {}
            for station in self.sim.map.get_all_stations():
                self.visited_stations[boat][station] = 0

        for station in self.sim.map.get_all_stations():
            self.usage_in_time[station] = {}
            for boat in self.sim.cb.boats.values():
                self.usage_in_time[station][boat] = 0



class Stats_Boat:
    def __init__(self, boats):
        self.boats = boats
        self.luggage = {}
        self.boatrewards = {}
        self.pickedup = {}
        self.droppedoff = {}
        self.droveto = {}
        self.visited_stations = {}

    def return_all_dicts(self):
        return [self.boatrewards, self.pickedup, self.droppedoff, self.droveto]

    # def plot_free(self, dictionary, title="Plot"):
    #     dict = dictionary
    #     fig, ax = plt.subplots(1, 2, figsize=(9, 3))
    #     plt.title(title)
    #     #for dict in dictionary:
    #     i=0
    #     for dict in dictionary:
    #         ax[i].step(dict.keys(), dict.values(), label='Boat %s' %self.boat.id)
    #         i+=1
    #         plt.legend()
    #     return plt



    def save_dict(self, dict):
        with open('data.txt', 'w') as outfile:
            json.dump(dict, outfile)

    def open_dict(self, dict):
        with open('data.txt') as json_file:
            data = json.load(json_file)
        print(type(data))
        print(data)

