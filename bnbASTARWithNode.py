"""
#UKI AGENT - Branch and bound - implementacija heapq - 0.022s
class Uki(Agent):
    def __init__(self, x, y, file_name):
        super().__init__(x, y, file_name)

    def get_agent_path(self, coin_distance):
        path = [i for i in range(1, len(coin_distance))]
        n = len(coin_distance) #8
        firstNode = Node([0],0,0)
        listOfNodes = [(firstNode.cost, n-len(firstNode.path), firstNode.path[-1], firstNode)]
        heapq.heapify(listOfNodes)
        while(len(listOfNodes) != 0):
            curr = heapq.heappop(listOfNodes)[3]
            if (len(curr.path) == (n + 1)):  #Nasli smo putanju sa ciljnim cvorom
                return curr.path
            if(len(curr.path) == n): # Ako je putanja obisla sve sem krajnjeg, treba da se vrati
                remaining = [0]
            else:
                remaining = [i for i in range(1, n) if i not in curr.path]
            for i in remaining:
                heapq.heappush(listOfNodes, (curr.cost + coin_distance[curr.path[-1]][i], n - (curr.level + 1), i,
                                             Node(curr.path + [i], curr.cost + coin_distance[curr.path[-1]][i],
                                                  curr.level + 1)))
        return []



#MICKO AGENT - A*
class Micko(Agent):
    def __init__(self, x, y, file_name):
        super().__init__(x, y, file_name)

    def get_agent_path(self, coin_distance):
        path = [i for i in range(1, len(coin_distance))]
        n = len(coin_distance)  # 8
        firstNode = Node([0], 0, 0)
        listOfNodes = [(firstNode.cost, n - len(firstNode.path), firstNode.path[-1], firstNode)]
        heapq.heapify(listOfNodes)
        while (len(listOfNodes) != 0):
            curr = heapq.heappop(listOfNodes)[3]
            if (len(curr.path) == (n + 1)):  # Nasli smo putanju sa ciljnim cvorom
                return curr.path
            if (len(curr.path) == n):  # Ako je putanja obisla sve sem krajnjeg, treba da se vrati
                remaining = [0]
            else:
                remaining = [i for i in range(1, n) if i not in curr.path]
            expandAndCalculate(remaining, listOfNodes, curr, coin_distance, n)

def expandAndCalculate(remaining, listOfNodes, curr, coin_distance, n):
    for i in remaining:
        scaledMatrix = scaleMatrix(curr, n, coin_distance)
        if not len(scaledMatrix):
            heur = 0
        else:
            heur = primsAlgorithm(scaledMatrix)
        heapq.heappush(listOfNodes, (curr.cost + coin_distance[curr.path[-1]][i] + heur, n - (curr.level + 1), i,
                                     Node(curr.path + [i], curr.cost + coin_distance[curr.path[-1]][i],
                                          curr.level + 1)))

def scaleMatrix(curr, n, coin_distance):
    newlist = []
    selected = [i for i in range(1, n) if i not in curr.path[:-1]]
    if not len(selected):
        return []
    selected.append(0)
    selected.sort()
    for i in selected:
        subList = []
        for j in selected:
            subList.append(coin_distance[i][j])
        newlist.append(subList)
    return newlist

def primsAlgorithm(scaledMatrix):
    inf = 2147483647
    n = len(scaledMatrix)
    selected_node = [0] * n
    no_edge = 0
    selected_node[0] = True
    sumAll = 0
    while (no_edge < n - 1):
        minimum = inf
        a = 0
        b = 0
        for m in range(n):
            if selected_node[m]:
                for i in range(n):
                    if((not selected_node[i]) and scaledMatrix[m][i]):
                        if minimum > scaledMatrix[m][i]:
                            minimum = scaledMatrix[m][i]
                            a = m
                            b = i
        sumAll = sumAll + scaledMatrix[a][b]
        selected_node[b] = True
        no_edge = no_edge + 1
    return sumAll
"""