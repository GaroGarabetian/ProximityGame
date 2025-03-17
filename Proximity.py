import random
from typing import List, Tuple, Union

class Cell:
    def __init__(self, value: int, owner: int):
        self.value = value
        self.owner = owner

    def getValue(self) -> int:
        return self.value

    def setValue(self, value: int) -> 'Cell':
        self.value = value
        return self

    def getOwner(self) -> int:
        return self.owner

    def setOwner(self, owner: int) -> 'Cell':
        self.owner = owner
        return self

    # For printing and debugging
    def __repr__(self) -> str:
        return f'Cell({self.value},{self.owner})'

    def __str__(self) -> str:
        return f'Cell({self.value},{self.owner})'


class Proximity11:
    def __init__(self, pid: int, length_X: int, length_Y: int):
        self.pid = pid
        self.length_X = length_X
        self.length_Y = length_Y
        # Custom attributes
        self.report = {}

    def setPid(self, pid: int) -> 'Proximity11':
        self.pid = pid
        return self

    def setBoardSize(self, length_X: int, length_Y: int) -> 'Proximity11':
        self.length_X = length_X
        self.length_Y = length_Y
        return self

    def getPlayerName(self) -> str:
        return 'Mpeleli_Tsioulis_Gkarampetian'

    def findNeighbours(self, cells: List[Cell]) -> List[Cell]:
        """Obtain a peek of the available positions that are adjacent to the currently placed tiles"""
        # Avoid affecting the original cells state
        cellsPeek = cells.copy()
        # Get occupied positions from given table
        occupied = [i for i in range(len(cells)) if cells[i].owner > 0]
        # Get all the neighbours of each occupied Cell.
        # Note: neighboursList is a list of integers representing Cell positions
        neighboursList = list(map(lambda o: self.findMyNeighbours(o), occupied))
        # Discard neighbours that are already occupied
        neighboursList = list(filter(lambda a: a not in occupied, neighboursList))
        # Flatten the list, and discard duplicate Cell positions by converting the list to a set
        neighboursList = set([item for sublist in neighboursList for item in sublist])
        # Set all neighbours as cells with potential owner the player, and initial values 0
        for i in neighboursList:
            # We are creating a new Cell instance and replacing it,
            # instead of using setOwner and setValue.
            # Otherwise, it would alter the original state's Cell instance,
            # because even if cellsPeek is a copy of cells, their elements
            # point to the same class instances in memory.
            cellsPeek[i] = Cell(0, self.pid) if cells[i].owner == 0 else cells[i]
        return cellsPeek

    def findMyNeighbours(self, pos: int) -> List[int]:
        """Return a list of positions of all the tiles adjacent to the position on the board given"""
        # Initializing a default state of neighbours which we will evaluate and/or alter later
        neighbours = {
            'left': pos - 1,
            'right': pos + 1,
            'top_right': pos + self.length_X,
            'bottom_right': pos - self.length_X + 1,
            'top_left': pos + self.length_X - 1,
            'bottom_left': pos - self.length_X
        }
        # Exception 1
        # If the row of the tile is an even number or 0,
        # then the leftmost tile will be adjacent to the leftmost tile of the previous row
        # on its top-right position, therefore we offset the bottom-adjacent tiles by one to the left.
        if pos >= self.length_X and (pos // self.length_X) % 2 == 0:
            neighbours['bottom_left'] -= 1
            neighbours['bottom_right'] -= 1
        # Exception 2
        # Likewise, on the opposite situation of Exception 1,
        # we offset the top-adjacent tiles by one to the right.
        if pos >= self.length_X and (pos // self.length_X) % 2 != 0:
            neighbours['top_left'] += 1
            neighbours['top_right'] += 1
        # Leftmost tiles have no left-adjacent tiles
        if pos % self.length_X == 0:
            neighbours.pop('left')
        # If we're in Exception 1 on the leftmost tile,
        # then there won't be any tiles on neither the tile's top-left nor bottom-left position
        if (pos // self.length_X) % 2 == 0:
            neighbours.pop('top_left')
            neighbours.pop('bottom_left')
        # On the bottom edge of the board, no bottom-adjacent tiles are to be found.
        # We discard them, if they exist
        if pos < self.length_X:
            neighbours.pop('bottom_left') if 'bottom_left' in neighbours else None
            neighbours.pop('bottom_right') if 'bottom_right' in neighbours else None
        # Rightmost tiles have no right-adjacent tiles
        if (pos + 1) % self.length_X == 0:
            neighbours.pop('right')
        # If we're in Exception 2 on the rightmost tile,
        # then there won't be any tiles on neither the tile's top-right nor bottom-right position
        if pos > self.length_X and (pos // self.length_X) % 2 != 0:
            neighbours.pop('top_right')
            neighbours.pop('bottom_right')
        # On the top edge of the board, no top-adjacent tiles are to be found.
        # We discard them, if they exist
        if pos / self.length_X >= self.length_Y - 1:
            neighbours.pop('top_left') if 'top_left' in neighbours else None
            neighbours.pop('top_right') if 'top_right' in neighbours else None
        # Build a list of the final neighbour tile positions, and return it
        return [neighbours[key] for key in neighbours]

    def placeTile(self, value: int, state: List[Cell]) -> int:
        """Return the position of the most optimal position to place the new tile, according to the current strategy"""
        # Adjacent tiles that the player could occupy
        availableTiles = list(filter(lambda c: c.owner == self.pid, self.findNeighbours(state)))
        # All empty tiles in the board currently
        emptyTiles = list(filter(lambda c: c.owner == 0, state))
        # If the board is empty, place the tile at the center
        if availableTiles == [] and emptyTiles == state:
            position = self.length_X // 2 + (self.length_Y // 2) * self.length_X
            return position
        # optimalMove is initialized with -1 initial values for each key
        # so that it can be checked whether an optimal move was found or to place the tile at a random position
        optimalMove = {"position": -1, "conquer": -1, "empower": -1, "totalControl": -1, "totalGain": -1}
        for i, cell in enumerate(self.findNeighbours(state)):
            # If the cell is already occupied by the opponent or the player
            if cell.owner != self.pid or cell.value != 0:
                continue
            # All tiles adjacent to the current position in the iteration
            allNeighbours = self.findMyNeighbours(i)
            # Opponent tiles adjacent to current position in the iteration
            opponentNeighbours = list(filter(lambda c: state[c].owner not in [0, self.pid], allNeighbours))
            # Player tiles adjacent to current position in the iteration
            myNeighbours = list(filter(lambda c: state[c].owner == self.pid, allNeighbours))
            # Tiles to be conquered by the player, if the current position is played
            conquer = [state[i] for i in list(filter(lambda c: state[c].value < value, opponentNeighbours))]
            conquerTotal = len(conquer)
            # Tiles to be empowered by the player, if the current position is played
            empower = [state[i] for i in list(filter(lambda c: state[c].owner == self.pid, myNeighbours))]
            empowerTotal = len(empower)
            totalGain = sum(list(map(lambda a: a.value, conquer))) + len(empower)
            # If the total merits are higher than the previous most optimal move's
            if conquerTotal + empowerTotal > optimalMove['totalControl']:
                optimalMove['position'] = i
                optimalMove['conquer'] = conquerTotal
                optimalMove['empower'] = empowerTotal
                optimalMove['totalControl'] = conquerTotal + empowerTotal
                optimalMove['totalGain'] = totalGain
            # Or if they're the same, pick the position that earns the most points
            elif conquerTotal + empowerTotal == optimalMove['totalControl']:
                if totalGain > optimalMove['totalGain']:
                    optimalMove['position'] = i
                    optimalMove['conquer'] = conquerTotal
                    optimalMove['empower'] = empowerTotal
                    optimalMove['totalControl'] = conquerTotal + empowerTotal
                    optimalMove['totalGain'] = totalGain
        # If no optimal position was found, choose a random position of the empty tiles in the boards
        if optimalMove['position'] == -1:
            position = random.choice([i for i in range(len(state)) if state[i].owner == 0])
        else:
            position = optimalMove['position']
        return position

    def applyChanges(self, value: int, state: List[Cell]) -> List[Cell]:
        self.report = {
            "playerId": self.pid,
            "playerValueDrawn": value,
            "position": 0,
            "affected": 0,
            "opponentTilesConquered": 0,
            "ownTilesEmpowered": 0
        }
        # Get the position of the tile to be placed
        position = self.placeTile(value, state)
        # Update the board by placing the tile
        state[position] = Cell(value, self.pid)
        # state[position] \
        # .setOwner(self.pid) \
        # .setValue(value)
        # Evaluate every adjacent tile affected by the placement
        for pos in self.findMyNeighbours(position):
            # If the tile belongs to the opponent and its value is smaller than the current place tile's, change ownership to the player's
            if state[pos].value < value and state[pos].owner not in [0, self.pid]:
                state[pos].setOwner(self.pid)
                self.report['opponentTilesConquered'] += 1
                self.report['affected'] += 1
            # If the tile belongs to the player, increment its value by 1
            elif state[pos].owner == self.pid:
                state[pos].setValue(state[pos].value + 1)
                self.report['ownTilesEmpowered'] += 1
                self.report['affected'] += 1
        return state

    def playXTimes(self, iterations: int, boardSize: Union[Tuple[int], List[int]]) -> None:
        """Initialize and collect statistics of `iterations` number of games, with players whose style is defined in the parameters.
        Returns a list containing the results of each game in a dictionary."""
        playerIndex = random.choice([0, 1])
        prox = Proximity11(playerIndex, *boardSize)
        state = [Cell(0, 0) for _ in range(prox.length_X * prox.length_Y)]
        results = []
        for _ in range(iterations):
            while True:
                if len(list(filter(lambda c: c.value == 0, prox.findNeighbours(state)))) == 0:
                    player1Tiles = list(filter(lambda c: c.owner == 1, state))
                    player1Score = sum(list(map(lambda a: a.value, player1Tiles)))
                    player2Tiles = list(filter(lambda c: c.owner == 2, state))
                    player2Score = sum(list(map(lambda a: a.value, player2Tiles)))
                    winner = 'Tie' if player1Score == player2Score else ('Player 1' if player1Score > player2Score else 'Player 2')
                    results.append({
                        "winner": winner,
                        "player1": {
                            "tiles": len(player1Tiles),
                            "score": sum(list(map(lambda a: a.value, player1Tiles)))
                        },
                        "player2": {
                            "tiles": len(player2Tiles),
                            "score": sum(list(map(lambda a: a.value, player2Tiles)))
                        }
                    })
                    state = [Cell(0, 0) for _ in range(prox.length_X * prox.length_Y)]
                    break
                state = prox.applyChanges(random.randrange(1, 20, 1), state)
                if playerIndex == 0:
                    playerIndex = 1
                else:
                    playerIndex = 0
                prox.setPid(playerIndex)
        return results


# Normal game printing the table after each move
if __name__ == '__main__':
    # Initialize a random first player
    playerPids = [1, 2]
    playerIndex = random.choice(range(len(playerPids)))
    prox = Proximity11(playerPids[playerIndex], 5, 5)
    # Initialize the starting state of the board
    state = [Cell(0, 0) for _ in range(prox.length_X * prox.length_Y)]
    while True:
        # Game is over when all tiles are occupied
        if len(list(filter(lambda c: c.value == 0, prox.findNeighbours(state)))) == 0:
            print('\nGame over!\n')
            print('Results:')
            player1Tiles = list(filter(lambda c: c.owner == 1, state))
            player2Tiles = list(filter(lambda c: c.owner == 2, state))
            print('Player1: Tiles: {}, Score: {}'.format(len(player1Tiles), sum(list(map(lambda a: a.value, player1Tiles)))))
            print('Player2: Tiles: {}, Score: {}'.format(len(player2Tiles), sum(list(map(lambda a: a.value, player2Tiles)))))
            break
        # Choose a random number from 1 to 20, and update the board
        state = prox.applyChanges(random.randrange(1, 20, 1), state)
        print('Player {} drew {}'.format(playerPids[playerIndex], prox.report['playerValueDrawn']))
        print('Opponent tiles conquered: {} | Own tiles empowered:{}'.format(prox.report['opponentTilesConquered'], prox.report['ownTilesEmpowered']))
        print()
        for y in range(prox.length_Y):
            if y % 2 != False:
                print('', end=' ' * 6)
            for x in range(prox.length_X - 1, -1, -1):
                print(state[::-1][x + y * prox.length_X], end=' ')
            print()
            print()
        if playerIndex == 0:
            playerIndex = 1
        else:
            playerIndex = 0
        prox.setPid(playerPids[playerIndex])
        input('Press Enter to continue with the next move...')