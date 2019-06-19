import Global as G

class Parameters:

    def __init__(self, mode, simtime=G.SIMTIME, to_dock=G.DOCK_TIMEOUT, to_pickup=G.PICK_UP_TIMEOUT,
                 to_dropoff=G.DROPOFF_TIMEOUT, num_boats=G.NUM_BOATS, capacity = G.CAPACITY,
                 alpha=G.ALPHA_DESTINATION_MIX, beta=G.BETA_DISCOUNT_RECURSION, max_arrival=G.MAX_ARRIVAL_EXPECT,
                 iat=G.INTERARRIVALTIME, expected_arrivals=G.expected_arrivals, edges=G.edgeList, randomseed=G.randomseed):

        self.mode = "CENTRAL" if mode else "HOHO"
        self.SIMTIME = simtime
        self.to_dock = to_dock
        self.to_pickup = to_pickup
        self.to_dropoff = to_dropoff
        self.num_boats = num_boats
        self.capacity = capacity
        self.alpha = alpha
        self.beta = beta
        self.max_arrival = max_arrival
        self.iat = iat
        self.expected_arrivals = expected_arrivals
        self.edges = edges
        self.randomseed = randomseed
        self.dists = [edges[i][2] for i in range(len(edges))]
        self.setG()


    def setG(self):
        G.SIMTIME = self.SIMTIME
        G.DOCK_TIMEOUT = self.to_dock
        G.PICK_UP_TIMEOUT = self.to_pickup
        G.DROPOFF_TIMEOUT = self.to_dropoff
        G.NUM_BOATS = self.num_boats
        G.CAPACITY = self.capacity
        G.ALPHA_DESTINATION_MIX = self.alpha
        G.BETA_DISCOUNT_RECURSION = self.beta
        G.MAX_ARRIVAL_EXPECT = self.max_arrival
        G.INTERARRIVALTIME = self.iat
        G.expected_arrivals = self.expected_arrivals
        G.randomseed = self.randomseed
        G.edgeList = self.edges

    def get_demand(self, type):
        if type == 1:
            demand = uniform
        elif type == 2:
            demand = random
        else:
            demand = skewed

    def to_string(self):
        stringer = "simtime=%s,\ttimeoutdock=%s,\ttimeoutpickup=%s,\ttimeoutdropoff=%s,\t" \
                   "numboats=%s,\tcapacity=%s,\talpha=%s,\tbeta=%s,\tmaxarrivals=%s,\tiat=%s,\t" \
                   "expected_arrivals=%s,\trandomseed=%s" %(self.SIMTIME, self.to_dock, self.to_pickup
                                                       , self.to_dropoff, self.num_boats, self.capacity,
                                                       self.alpha, self.beta, self.max_arrival, self.iat,
                                                       self.expected_arrivals, self.randomseed)
        return stringer

    def print(self):
        print(self.to_string())