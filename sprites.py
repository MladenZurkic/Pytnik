import heapq
import itertools
import math
import queue

import pygame
import os
import config
from util import Node

class BaseSprite(pygame.sprite.Sprite):
    images = dict()

    def __init__(self, x, y, file_name, transparent_color=None, wid=config.SPRITE_SIZE, hei=config.SPRITE_SIZE):
        pygame.sprite.Sprite.__init__(self)
        if file_name in BaseSprite.images:
            self.image = BaseSprite.images[file_name]
        else:
            self.image = pygame.image.load(os.path.join(config.IMG_FOLDER, file_name)).convert()
            self.image = pygame.transform.scale(self.image, (wid, hei))
            BaseSprite.images[file_name] = self.image
        # making the image transparent (if needed)
        if transparent_color:
            self.image.set_colorkey(transparent_color)
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)


class Surface(BaseSprite):
    def __init__(self):
        super(Surface, self).__init__(0, 0, 'terrain.png', None, config.WIDTH, config.HEIGHT)


class Coin(BaseSprite):
    def __init__(self, x, y, ident):
        self.ident = ident
        super(Coin, self).__init__(x, y, 'coin.png', config.DARK_GREEN)

    def get_ident(self):
        return self.ident

    def position(self):
        return self.rect.x, self.rect.y

    def draw(self, screen):
        text = config.COIN_FONT.render(f'{self.ident}', True, config.BLACK)
        text_rect = text.get_rect(center=self.rect.center)
        screen.blit(text, text_rect)


class CollectedCoin(BaseSprite):
    def __init__(self, coin):
        self.ident = coin.ident
        super(CollectedCoin, self).__init__(coin.rect.x, coin.rect.y, 'collected_coin.png', config.DARK_GREEN)

    def draw(self, screen):
        text = config.COIN_FONT.render(f'{self.ident}', True, config.RED)
        text_rect = text.get_rect(center=self.rect.center)
        screen.blit(text, text_rect)


class Agent(BaseSprite):
    def __init__(self, x, y, file_name):
        super(Agent, self).__init__(x, y, file_name, config.DARK_GREEN)
        self.x = self.rect.x
        self.y = self.rect.y
        self.step = None
        self.travelling = False
        self.destinationX = 0
        self.destinationY = 0

    def set_destination(self, x, y):
        self.destinationX = x
        self.destinationY = y
        self.step = [self.destinationX - self.x, self.destinationY - self.y]
        magnitude = math.sqrt(self.step[0] ** 2 + self.step[1] ** 2)
        self.step[0] /= magnitude
        self.step[1] /= magnitude
        self.step[0] *= config.TRAVEL_SPEED
        self.step[1] *= config.TRAVEL_SPEED
        self.travelling = True

    def move_one_step(self):
        if not self.travelling:
            return
        self.x += self.step[0]
        self.y += self.step[1]
        self.rect.x = self.x
        self.rect.y = self.y
        if abs(self.x - self.destinationX) < abs(self.step[0]) and abs(self.y - self.destinationY) < abs(self.step[1]):
            self.rect.x = self.destinationX
            self.rect.y = self.destinationY
            self.x = self.destinationX
            self.y = self.destinationY
            self.travelling = False

    def is_travelling(self):
        return self.travelling

    def place_to(self, position):
        self.x = self.destinationX = self.rect.x = position[0]
        self.y = self.destinationX = self.rect.y = position[1]

    # coin_distance - cost matrix
    # return value - list of coin identifiers (containing 0 as first and last element, as well)
    def get_agent_path(self, coin_distance):
        pass

"""
class ExampleAgent(Agent):
    def __init__(self, x, y, file_name):
        super().__init__(x, y, file_name)

    def get_agent_path(self, coin_distance):
        path = [i for i in range(1, len(coin_distance))]
        print(coin_distance)
        print(path)
        random.shuffle(path)
        print([0] + path + [0])
        return [0] + path + [0]
"""

class Aki(Agent):
    def __init__(self, x, y, file_name):
        super().__init__(x, y, file_name)

    def get_agent_path(self, coin_distance):
        coins = [i for i in range(1, len(coin_distance))]
        path = []
        nextCoin = 0
        path.append(nextCoin)

        while len(coins):
            availCoins = {}
            rowCoinsCost = coin_distance[nextCoin]
            #Pravimo dictionary {idCoin: costToCoin)
            for i in coins:
                availCoins[i] = rowCoinsCost[i]
            nextCoin = min(availCoins, key=availCoins.get)
            path.append(nextCoin)
            coins.remove(nextCoin)
        path.append(0)
        return path


class Jocke(Agent):
    def __init__(self, x, y, file_name):
        super().__init__(x, y, file_name)

    def get_agent_path(self, coin_distance):
        path = [i for i in range(1, len(coin_distance))]
        allPaths = permutations(path)
        costs = calculateCost(allPaths, coin_distance)
        minimumCost = min(costs)
        minimumCostIndex = costs.index(minimumCost)
        return [0] + list(allPaths[minimumCostIndex]) + [0]

def permutations(list_perm):
    return list(itertools.permutations(list_perm))

def calculateCost(allPaths, coin_distance):
    costs = []
    for path in allPaths:
        path = list(path)
        path.insert(0, 0)
        sum = 0
        for i in range(0, (len(path) - 1)):
            sum += coin_distance[path[i]][path[i+1]]
        sum += coin_distance[path[len(path) - 1]][0]
        costs.append(sum)
    return costs


#UKI AGENT - Branch and bound - implementacija heapq - 0.022s - BEZ NODE!!!
class Uki(Agent):
    def __init__(self, x, y, file_name):
        super().__init__(x, y, file_name)

    def get_agent_path(self, coin_distance):
        path = [i for i in range(1, len(coin_distance))]
        n = len(coin_distance) #8
        firstNode = (0, n, 0, [0])

        listOfNodes = [firstNode]
        heapq.heapify(listOfNodes)
        while(len(listOfNodes) != 0):
            curr = heapq.heappop(listOfNodes)
            if (len(curr[3]) == (n + 1)):  #Nasli smo putanju sa ciljnim cvorom
                return curr[3]
            if(len(curr[3]) == n): # Ako je putanja obisla sve sem krajnjeg, treba da se vrati
                remaining = [0]
            else:
                remaining = [i for i in range(1, n) if i not in curr[3]]
            for i in remaining:
                heapq.heappush(listOfNodes, (curr[0] + coin_distance[curr[2]][i], (curr[1] - 1), i, curr[3] + [i]))
        return []



#MICKO AGENT - A*
class Micko(Agent):
    def __init__(self, x, y, file_name):
        super().__init__(x, y, file_name)

    def get_agent_path(self, coin_distance):
        path = [i for i in range(1, len(coin_distance))]
        n = len(coin_distance)  # 8
        firstNode = (0, n, 0, [0], 0)
        listOfNodes = [firstNode]
        heapq.heapify(listOfNodes)
        while (len(listOfNodes) != 0):
            curr = heapq.heappop(listOfNodes)
            if (len(curr[3]) == (n + 1)):  # Nasli smo putanju sa ciljnim cvorom
                return curr[3]
            if (len(curr[3]) == n):  # Ako je putanja obisla sve sem krajnjeg, treba da se vrati
                remaining = [0]
            else:
                remaining = [i for i in range(1, n) if i not in curr[3]]
            expandAndCalculate(remaining, listOfNodes, curr, coin_distance, n)

def expandAndCalculate(remaining, listOfNodes, curr, coin_distance, n):
    scaledMatrix = scaleMatrix(curr, n, coin_distance)
    if not len(scaledMatrix):
        heur = 0
    else:
        heur = primsAlgorithm(scaledMatrix)
    for i in remaining:
        heapq.heappush(listOfNodes, (curr[4] + coin_distance[curr[2]][i] + heur, (curr[1] - 1), i, curr[3] + [i], curr[4] + coin_distance[curr[2]][i]))

def scaleMatrix(curr, n, coin_distance):
    newlist = []
    selected = [i for i in range(1, n) if i not in curr[3]]
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





#####################################################################

#UKI AGENT - Branch and bound - implementacija pq - 0.3s
class UkiAgentPQ(Agent):
    def __init__(self, x, y, file_name):
        super().__init__(x, y, file_name)

    def get_agent_path(self, coin_distance):
        path = [i for i in range(1, len(coin_distance))]
        n = len(coin_distance) #8
        firstNode = Node([0],0,0)
        queueOfNodes = queue.PriorityQueue()
        queueOfNodes.put((firstNode.cost, n-len(firstNode.path), firstNode.path[-1], firstNode))
        while not queueOfNodes.empty():
            curr = queueOfNodes.get()[3]
            if (len(curr.path) == (n + 1)):  #Nasli smo putanju sa ciljnim cvorom
                return curr.path
            if(len(curr.path) == n): # Ako je putanja obisla sve sem krajnjeg, treba da se vrati
                remaining = [0]
            else:
                remaining = [i for i in range(1, n) if i not in curr.path]
            for i in remaining:
                queueOfNodes.put((curr.cost + coin_distance[curr.path[-1]][i], n - (curr.level + 1), i,
                                  Node(curr.path + [i], curr.cost + coin_distance[curr.path[-1]][i], curr.level + 1)))
        return []



#UKI AGENT - Branch and bound - implementacija lista listi - 2.4s
class UkiAgentListaListi(Agent):
    def __init__(self, x, y, file_name):
        super().__init__(x, y, file_name)

    def get_agent_path(self, coin_distance):
        path = [i for i in range(1, len(coin_distance))]
        n = len(coin_distance) #8
        print(n)
        firstNode = Node([0],0,0)
        listOfNodes = [firstNode]
        while(len(listOfNodes) != 0):
            curr = listOfNodes.pop(0)
            if (len(curr.path) == (n + 1)):  #Nasli smo putanju sa ciljnim cvorom
                print(curr.cost)
                return curr.path
            if(len(curr.path) == n): # Ako je putanja obisla sve sem krajnjeg, treba da se vrati
                remaining = [0]
            else:
                remaining = [i for i in range(1, n) if i not in curr.path]

            newPaths = expandNode(curr, remaining, coin_distance)
            addNewPathsAndSort(listOfNodes, newPaths, n)
        return []


def expandNode(curr, remaining, coin_distance):
    newNodesList = []
    for i in remaining:
        newNodesList.append(Node(curr.path + [i], curr.cost + coin_distance[curr.path[-1]][i], curr.level + 1))
    return newNodesList


def addNewPathsAndSort(listOfNodes, newPaths, n):
    listOfNodes.extend(newPaths)
    key = lambda x: (x.cost, n-len(x.path), x.path[-1])
    listOfNodes.sort(key=key)
    return


