import Global as G
import json
import matplotlib.pyplot as plt
import statistics as st
from tabulate import tabulate
import numpy as np


class Stats:
    def __init__(self, sim):
        self.sim = sim
        # STATIONS
        self.final_demand = 0
        self.demand_in_time = {}
        self.usage_in_time = {}
        self.waiting_demand = []
        self.accured_demand = 0
        # BOATS
        self.boat_load_in_time = {}
        self.boat_load = {}
        self.boat_load_raw = []
        self.boat_load_raw_ratio = []
        self.boat_at_station = []
        self.drovefromto = []
        # PASSENGERS
        self.dropped_passengers = []
        self.passenger_processing_ratio = []
        self.passenger_waiting_time = []
        self.passenger_promise = []
        # MISC
        self.poisson_value_station = {}
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
            self.poisson_value_station[station] = {}

        # Boat
        self.visited_stations = {}
        for boat in self.sim.cb.boats.values():
            self.visited_stations[boat] = {}

            for station in self.sim.map.get_all_stations():
                self.visited_stations[boat][station] = 0

        for i in range(1,G.NUM_BOATS+1):
            self.boat_load_in_time[i] = {}
        for i in range(0, G.CAPACITY+1):
            self.boat_load[i] = 0
        for i in range(G.NUM_BOATS):
            self.boat_at_station.append([ "B%s" %str(i+1) ])
            self.drovefromto.append([])
            for j in range(len(self.sim.map.get_all_stations())):
                self.boat_at_station[i].append(0)
                self.drovefromto[i].append(["S%s"%str(j+1)])
                for k in range(len(self.sim.map.get_all_stations())):
                    self.drovefromto[i][j].append(0)

        for station in self.sim.map.get_all_stations():
            self.usage_in_time[station] = {}
            for boat in self.sim.cb.boats.values():
                self.usage_in_time[station][boat] = 0

    def visualize_data(self, runs):
        for run in runs:
            print(run.final_demand)

        # plt.subplots(1, G.NUM_BOATS)
        boatload = []
        f1 = plt.figure(1)
        for run in runs:
            plt.subplot(1,2,runs.index(run)+1)
            vals = []
            for load in range(0,G.CAPACITY+1):
                vals.append(load)
            plt.bar(run.boat_load.keys(), run.boat_load.values())
            plt.title("Boat Load in %s" %(run.mode))
            plt.legend()

        # Histogram
        f2 = plt.figure(2)
        for run in runs:
            plt.subplot(1,2,runs.index(run)+1)
            vals = []
            plt.hist(run.passenger_processing_ratio)
            plt.title("Passenger waiting ratio in %s" %(run.mode))
            plt.legend()

        # Demand Stations
        f3 = plt.figure(3)
        colors = ["blue", "red", "green", "blue", "black"]
        col = 0
        for run in runs:
            boats = list(run.boat_load_in_time.values())
            num = 1
            if run.mode is "Central":
                line = "dashed"
            else:
                line = "dotted"

            for boat in boats:
                plt.title('boat load over time with %i boats, IAT:%i, MAE:%i' % (
                len(self.sim.cb.boats), G.INTERARRIVALTIME, G.MAX_ARRIVAL_EXPECT))
                plt.plot(boat.keys(), boat.values(), label=run.mode + ": B" + str(num), linestyle=line,
                         color=colors[num])
                num += 1
            col += 1
        plt.legend()

        # Promised time difference
        plt.title('Passenger information over time with %i boats, IAT:%i, MAE:%i' % (
            len(self.sim.cb.boats), G.INTERARRIVALTIME, G.MAX_ARRIVAL_EXPECT))
        f4 = plt.figure(4)
        w = np.linspace(0, len(runs[1].passenger_promise)-1, len(runs[1].passenger_promise))
        x = np.linspace(0, len(runs[1].passenger_processing_ratio) - 1, len(runs[1].passenger_processing_ratio))
        y = np.linspace(0, len(runs[1].passenger_waiting_time) - 1, len(runs[1].passenger_waiting_time))
        z = np.linspace(0, len(runs[1].waiting_demand) - 1, len(runs[1].waiting_demand))
        plt.plot(w, runs[1].passenger_promise, 'ro', label="Delta Passenger Promise", color=colors[1], alpha=0.5)
        plt.plot(x, runs[1].passenger_processing_ratio, 'ro', label="Passenger Processing ratio", color=colors[2], alpha=0.5)
        plt.plot(y, runs[1].passenger_waiting_time, 'ro', label="Passenger Waiting Time", color=colors[3], alpha=0.5)
        plt.plot(z, runs[1].waiting_demand, 'ro', label="Accrued Demand at Stations", color=colors[4], alpha=0.5)
        plt.legend()

        # New demand over time
        f5 = plt.figure(5)
        colors = ["blue", "red", "green", "blue", "red", "green", "blue", "red", "green", "blue"]
        col = 0
        num = 1
        for run in runs:
            if run.mode is "Central":
                line = "dashed"
            else:
                line = "dotted"
            plt.title('New demand over time with %i boats, IAT:%i, MAE:%i' % (
                len(self.sim.cb.boats), G.INTERARRIVALTIME, G.MAX_ARRIVAL_EXPECT))
            plt.plot(run.poisson_value.keys(), run.poisson_value.values(), alpha=0.5, label=run.mode + ": S" + str(num),
                     linestyle=line,
                     color=colors[num])
            num += 1
        plt.legend()

        f6 = plt.figure(6)
        colors = ["blue", "red", "green", "blue", "red", "green", "blue", "red", "green", "blue"]
        col = 0
        for run in runs:
            stations = list(run.demand_in_time.values())
            num = 1
            if run.mode is "Central":
                line = "dashed"
            else:
                line = "dotted"

            for station in stations:
                plt.title('Demand at stations over time with %i boats, IAT:%i, MAE:%i' % (
                len(self.sim.cb.boats), G.INTERARRIVALTIME, G.MAX_ARRIVAL_EXPECT))
                plt.plot(station.keys(), station.values(), label=run.mode + ": S" + str(num), linestyle=line,
                         color=colors[num])
                num += 1
            col += 1
        plt.legend()

        plt.show()

    def analyze_data(self, runs):
        for run in runs:
            # MEANS
            means = {}
            # Boat
            means.update({"boatload":st.mean(run.boat_load_raw)})
            means.update({"boatload_ratio": st.mean(run.boat_load_raw_ratio)})
            # Passenger
            means.update({"passenger_waiting_time": st.mean(run.passenger_waiting_time)})
            means.update({"passenger_processing_ratio":st.mean(run.passenger_processing_ratio)})
            means.update({"waiting_demand_station": st.mean(run.waiting_demand)})


            # medians
            medians = {}
            medians.update({"boatload": st.median(run.boat_load_raw)})
            medians.update({"boatload_ratio": st.median(run.boat_load_raw_ratio)})
            medians.update({"passenger_waiting_time": st.median(run.passenger_waiting_time)})
            medians.update({"passenger_processing_ratio": st.median(run.passenger_processing_ratio)})
            medians.update({"waiting_demand_station": st.median(run.waiting_demand)})

            # population variance
            pvariances = {}
            pvariances.update({"boatload": st.pstdev(run.boat_load_raw)})
            pvariances.update({"boatload_ratio": st.pstdev(run.boat_load_raw_ratio)})
            pvariances.update({"passenger_waiting_time": st.pstdev(run.passenger_waiting_time)})
            pvariances.update({"passenger_processing_ratio": st.pstdev(run.passenger_processing_ratio)})
            pvariances.update({"waiting_demand_station": st.pstdev(run.waiting_demand)})

            tabs = []
            for name in means.keys():
                tab = []
                tab.append(str(name))
                tab.append(medians[name])
                tab.append(means[name])
                tab.append(pvariances[name])
                tabs.append(tab)

            print(run.mode)

            print(tabulate(tabs, headers=['Variable', 'Median', 'Mean', 'Population Variance'], tablefmt="fancy_grid"))
            print("Accured demand summed: %i" %run.accured_demand)
            if run.mode == "Central":
                mean =  st.mean(run.passenger_promise)
                median =st.median(run.passenger_promise)
                pvar = st.pstdev(run.passenger_promise)
                print("passenger promise failure mean, median, variance: ", mean, median, pvar)

            print("Stations approached per boat in %")
            for i in range(len(run.boat_at_station)):
                sum = np.sum(run.boat_at_station[i][1:])
                for j in range(1, len(run.boat_at_station[0])):
                    run.boat_at_station[i][j] = run.boat_at_station[i][j] / sum *100
            print(tabulate(run.boat_at_station, ['S1', 'S2', 'S3'], tablefmt="fancy_grid"))

            # print("Quantities Boats going from to:")
            # for i in range(G.NUM_BOATS):
            #     print("Boat %s" %(i+1))
            #     print(tabulate(run.drovefromto[i], ['S1', 'S2', 'S3'], tablefmt="fancy_grid"))

            print("\n\n")



















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