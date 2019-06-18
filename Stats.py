import Global as G
import json
import matplotlib.pyplot as plt
import statistics as st
from tabulate import tabulate
import numpy as np


class Stats:
    def __init__(self, sim):
        self.sim = sim
        self.params = sim.params
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

        if sim.central:
            self.mode = "Central"
        else:
            self.mode = "HOHO"

    def init(self):
        self.num_stations = len(self.sim.map.get_all_stations())
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

    def micro__print_data_light(self):
        # MEANS
        a=1
        for item in self.means.keys():
            #print("%s: %s,\t"%(item, self.means[item]), end="")
            print("%s%s: %s," % ("\t"*a, item, self.means[item]))
            a+=1
        # FINAL DEMAND
        print("occured_demand=%s \t demand_left=%s \t SATISFIED=%s%%" %(self.accured_demand, sum(self.final_demand), self.satisfied))
        print()

    def micro__analyze_data(self):
        #print(run.sim.params.to_string())

        self.satisfied = 100 - round(sum(self.final_demand) / self.accured_demand * 100)

        # Passenger Stats
        wts, otb, tot = [], [], []
        for passenger in self.dropped_passengers:
            wts.append(passenger.stat_wts)
            otb.append(passenger.stat_otb)
            tot.append(passenger.stat_wts + passenger.stat_otb)

        # MEANS
        self.means = {
            # BOATS
            "boatload": round(st.mean(self.boat_load_raw), 2),
            "boatload_ratio": round(st.mean(self.boat_load_raw_ratio), 2),
            # PASSENGER
            "P_wts": round(st.mean(wts), 2),
            "P_otb": round(st.mean(otb), 2),
            "P_tot": round(st.mean(tot), 2),
            "waiting_demand_station": round(st.mean(self.waiting_demand), 2)}

        self.medians = {
            # BOATS
            "boatload": st.median(self.boat_load_raw),
            "boatload_ratio": st.median(self.boat_load_raw_ratio),
            # PASSENGER
            "P_wts": st.median(wts),
            "P_otb": st.median(otb),
            "P_tot": st.median(tot),
            "waiting_demand_station": st.median(self.waiting_demand)}

        self.stdev = {
            # BOATS
            "boatload": st.stdev(self.boat_load_raw),
            "boatload_ratio": st.stdev(self.boat_load_raw_ratio),
            # PASSENGER
            "P_wts": st.stdev(wts),
            "P_otb": st.stdev(otb),
            "P_tot": st.stdev(tot),
            "waiting_demand_station": st.median(self.waiting_demand)}

    @staticmethod
    def macro__summary(stats):
        for stat in stats:
            part = stat.csv_output()

    def csv_output(self):
        out = {
            'simtime':self.params.SIMTIME,
            'num_stations': self.num_stations,
            'num_boats':self.params.num_boats,
            'capacity':self.params.capacity,
            'alpha':self.params.alpha,
            'beta':self.params.beta,
            'randomseed':self.params.randomseed,
            'mn_boatload_ratio':self.means["boatload_ratio"],
            'p_wts':self.means["P_wts"],
            'p_otb':self.means["P_otb"],
            'mn_waiting_demand':self.means["waiting_demand_station"],
            'dem_occ':self.accured_demand,
            'dem_left':sum(self.final_demand),
            'satisfied':self.satisfied
        }
        return out

    def macro__plot_num_cap(self, stats):
        num_boats = []
        capacity = []
        for stat in stats:
            num_boats.append(stat.params.num_boats)
            capacity.append(stat.params.capacity)
        capacity = sorted(list(set(capacity)))
        num_boats = sorted(list(set(num_boats)))

        arr = [[0 for i in range(len(num_boats))] for j in range(len(capacity))]
        for stat in stats:
            arr[capacity.index(stat.params.capacity)][num_boats.index(stat.params.num_boats)] = stat.satisfied

        a=1

        fig, ax = plt.subplots()
        im = ax.imshow(arr)

        # We want to show all ticks...
        ax.set_xticks(np.arange(len(num_boats)))
        ax.set_yticks(np.arange(len(capacity)))
        # ... and label them with the respective list entries
        ax.set_xticklabels(num_boats)
        ax.set_yticklabels(capacity)

        # Rotate the tick labels and set their alignment.
        plt.setp(ax.get_xticklabels(), rotation=45, ha="right",
                 rotation_mode="anchor")

        # Loop over data dimensions and create text annotations.
        for i in range(len(num_boats)):
            for j in range(len(capacity)):
                text = ax.text(i, j, arr[j][i], ha="center", va="center", color="w")
                pass

        ax.set_title("Parameters #boats & capacity")
        fig.tight_layout()
        plt.show()

    def macro__print_data(self, runs):
        for run in runs:
            #print(run.sim.params.to_string())
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
            medians.update({"P_wts": st.median(wts)})
            medians.update({"P_otb": st.median(otb)})
            medians.update({"P_tot": st.median(tot)})
            medians.update({"waiting_demand_station": st.median(run.waiting_demand)})

            # population variance
            pvariances = {}
            pvariances.update({"boatload": st.pstdev(run.boat_load_raw)})
            pvariances.update({"boatload_ratio": st.pstdev(run.boat_load_raw_ratio)})
            pvariances.update({"P_wts": st.pstdev(wts)})
            pvariances.update({"P_otb": st.pstdev(otb)})
            pvariances.update({"P_tot": st.pstdev(tot)})
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
            if G.means: print(tabulate(tabs, headers=['Variable', 'Median', 'Mean', 'Population Variance'], tablefmt="fancy_grid"))
            if G.accrued_demand: print("Accured demand summed: %i" %run.accured_demand)

            # Stations approached per boat
            for i in range(len(run.boat_at_station)):
                sum = np.sum(run.boat_at_station[i][1:])
                for j in range(1, len(run.boat_at_station[0])):
                    run.boat_at_station[i][j] = run.boat_at_station[i][j] / sum *100
            if G.approached_stations: print("Stations approached per boat in %\n" + tabulate(run.boat_at_station, ['S1', 'S2', 'S3'], tablefmt="fancy_grid"))
            #print(tabulate(run.boat_at_station, ['S1', 'S2', 'S3'], tablefmt="fancy_grid"))

            # print("Quantities Boats going from to:")
            # for i in range(G.NUM_BOATS):
            #     print("Boat %s" %(i+1))
            #     print(tabulate(run.drovefromto[i], ['S1', 'S2', 'S3'], tablefmt="fancy_grid"))

            print("\n\n")
        for run in runs:
            print("%s:%s \t--> %i"%(run.mode, run.final_demand, np.sum(run.final_demand)))


    def macro__plot_data(self, runs):
        central = None
        for run in runs:
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
        colors = ["blue", "red", "green", "blue", "black", "blue", "red", "green", "blue", "black", "blue", "red", "green", "blue", "black", "blue", "red", "green", "blue", "black", "blue", "red", "green", "blue", "black", "blue", "red", "green", "blue", "black"]
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
