import Global as G
import json
import matplotlib.pyplot as plt
import statistics as st
from tabulate import tabulate
import numpy as np


class Stats:
    def __init__(self, sim):
        self.sim = sim
        # STATIONS                      # #NETWORK#
        self.final_demand = 0
        self.demand_in_time = {}        # [station][time] = demand at station *Network*
        self.total_demand_in_time = {}  # [time] = total demand *Network*
        self.charger_usage_in_time = {} # [station][time] = 1 or 0 *Network*
        self.waiting_demand = []        # list: #waiting_passengers each IAT (when new arrive)
        self.waiting_demand_in_time = {}# list: #waiting_passengers each IAT (when new arrive)
        self.accured_demand = 0
        # BOATS                         # #BOAT#
        self.boat_load_in_time = {}     # [boat.id][time] = len(boat.passengers)
        self.boat_load = {}             # [load_amount] += 1
        self.boat_load_raw = []         # list of loads (int) when driving
        self.boat_load_raw_ratio = []   # list of load% when driving
        self.boat_at_station = []       # [boat.id][station.id] += 1
        self.drovefromto = []           # [from.id][to.id] += 1
        self.visited_stations = {}      # [boat][station] += 1 **Network**
        # PASSENGERS                            # ##BOAT##
        self.dropped_passengers = []            # list: all dispatched passengers
        self.override_in_time= {}               # list: drive_time - distance
        self.passenger_waiting_time = []        # list: time(pu) - time(pas.arrival)
        self.p_wait_till_pickup = {}            # dict: [time] -> P was picked, how long was the wait
        # MISC                                  # ##PASSENGERS##
        self.poisson_value_station = {}         # [station.id][time] = poisson_val
        self.poisson_value = {}                 # [time] = poisson_val
        if sim.mode:
            self.mode = "Central"
        else:
            self.mode = "HOHO"

    def init(self):
        for station in self.sim.map.get_all_stations():
            self.demand_in_time[station] = {}
            self.demand_in_time[station][0] = 0
            self.charger_usage_in_time[station] = {}
            self.charger_usage_in_time[station][0] = 0
            self.poisson_value_station[station] = {}

        # Boat
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
            self.charger_usage_in_time[station] = {}
            for boat in self.sim.cb.boats.values():
                self.charger_usage_in_time[station][boat] = 0

    def visualize_data(self, runs):
        central = None
        for run in runs:
            print(run.final_demand)
            if run.mode == "Central": central = runs.index(run)

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

        # # Histogram
        # f2 = plt.figure(2)
        # for run in runs:
        #     plt.subplot(1,2,runs.index(run)+1)
        #     vals = []
        #     plt.hist(run.passenger_processing_delay)
        #     plt.title("Passenger over_ride_time in %s" %(run.mode))
        #     plt.legend()

        # Demand Stations
        f3 = plt.figure(3)
        colors = ["blue", "red", "green", "blue", "black", "blue", "red", "green", "blue", "black", "blue", "red", "green", "blue", "black"]
        plt.title('boat load over time with %i boats, IAT:%i, MAE:%i' % (
            len(self.sim.cb.boats), G.INTERARRIVALTIME, G.MAX_ARRIVAL_EXPECT))
        col = 0
        for run in runs:
            boats = list(run.boat_load_in_time.values())
            num = 1
            if run.mode is "Central":
                line = "dashed"
            else:
                line = "dotted"

            for boat in boats:
                plt.plot(boat.keys(), boat.values(), label=run.mode + ": B" + str(num), linestyle=line,
                         color=colors[num])
                num += 1
            col += 1
        plt.legend()

        # Promised time difference
        f4 = plt.figure(4)
        plt.title('Passenger information over time with %i boats, IAT:%i, MAE:%i' % (
            len(self.sim.cb.boats), G.INTERARRIVALTIME, G.MAX_ARRIVAL_EXPECT))

        z = runs[central].override_in_time.keys()
        x = runs[central].p_wait_till_pickup.keys()


        plt.plot(z, runs[central].override_in_time.values(), 'ro', label="over_ride_time", color=colors[1], alpha=0.1)
        plt.plot(x, runs[central].p_wait_till_pickup.values(), 'ro', label="P_wait_till_PU", color=colors[3], alpha=1)

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
            plt.plot(run.poisson_value.keys(), run.poisson_value.values(), alpha=0.5, label=run.mode, linestyle=line, color=colors[num])
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

        f7 = plt.figure(7)
        for run in runs:
            num = 1
            if run.mode is "Central":
                col = "red"
            else:
                col = "blue"
            plt.title('Total demand over time with %i boats, IAT:%i, MAE:%i' % (
                len(self.sim.cb.boats), G.INTERARRIVALTIME, G.MAX_ARRIVAL_EXPECT))
            plt.plot(run.total_demand_in_time.keys(), run.total_demand_in_time.values(), label=run.mode, color=col)
            num += 1
        plt.legend()

        # f7 = plt.figure(7)
        # colors = ["blue", "red", "green", "blue", "red", "green", "blue", "red", "green", "blue"]
        # col = 0
        # for run in runs:
        #     boats = run.boat_at_station.values()
        #     num = 1
        #     if run.mode is "Central":
        #         line = "dashed"
        #     else:
        #         line = "dotted"
        #
        #     for boat in boats:
        #         plt.title('Demand at stations over time with %i boats, IAT:%i, MAE:%i' % (
        #             len(self.sim.cb.boats), G.INTERARRIVALTIME, G.MAX_ARRIVAL_EXPECT))
        #         plt.plot(boat.keys(), boat.values(), label=run.mode + ": B" + str(num), linestyle=line,
        #                  color=colors[num])
        #         num += 1
        #     col += 1
        # plt.legend()

        plt.show()

        # self.boat_at_station = []  # [boat.id][station.id] += 1

    def analyze_data(self, runs):
        for run in runs:
            # Passenger Stats
            wts, otb, tot = [], [], []
            for passenger in run.dropped_passengers:
                wts.append(passenger.stat_wts)
                otb.append(passenger.stat_otb)
                tot.append(passenger.stat_wts + passenger.stat_otb)



            # MEANS
            means = {}
            # Boat
            means.update({"boatload":st.mean(run.boat_load_raw)})
            means.update({"boatload_ratio": st.mean(run.boat_load_raw_ratio)})
            # Passenger
            means.update({"P_wts": st.mean(wts)})
            means.update({"P_otb": st.mean(otb)})
            means.update({"P_tot": st.mean(tot)})
            means.update({"waiting_demand_station": st.mean(run.waiting_demand)})


            # medians
            medians = {}
            medians.update({"boatload": st.median(run.boat_load_raw)})
            medians.update({"boatload_ratio": st.median(run.boat_load_raw_ratio)})

            medians.update({"P_wts": st.mean(wts)})
            medians.update({"P_otb": st.mean(otb)})
            medians.update({"P_tot": st.mean(tot)})
            medians.update({"waiting_demand_station": st.median(run.waiting_demand)})

            # population variance
            pvariances = {}
            pvariances.update({"boatload": st.pstdev(run.boat_load_raw)})
            pvariances.update({"boatload_ratio": st.pstdev(run.boat_load_raw_ratio)})

            pvariances.update({"P_wts": st.mean(wts)})
            pvariances.update({"P_otb": st.mean(otb)})
            pvariances.update({"P_tot": st.mean(tot)})
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


        # Todo Repair, put back in
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