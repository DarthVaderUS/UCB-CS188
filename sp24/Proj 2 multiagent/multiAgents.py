# multiAgents.py
# --------------
# Licensing Information:  You are free to use or extend these projects for
# educational purposes provided that (1) you do not distribute or publish
# solutions, (2) you retain this notice, and (3) you provide clear
# attribution to UC Berkeley, including a link to http://ai.berkeley.edu.
# 
# Attribution Information: The Pacman AI projects were developed at UC Berkeley.
# The core projects and autograders were primarily created by John DeNero
# (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# Student side autograding was added by Brad Miller, Nick Hay, and
# Pieter Abbeel (pabbeel@cs.berkeley.edu).


from util import manhattanDistance
from game import Directions
import random, util

from game import Agent
from pacman import GameState

class ReflexAgent(Agent):
    """
    A reflex agent chooses an action at each choice point by examining
    its alternatives via a state evaluation function.

    The code below is provided as a guide.  You are welcome to change
    it in any way you see fit, so long as you don't touch our method
    headers.
    """


    def getAction(self, gameState: GameState):
        """
        You do not need to change this method, but you're welcome to.

        getAction chooses among the best options according to the evaluation function.

        Just like in the previous project, getAction takes a GameState and returns
        some Directions.X for some X in the set {NORTH, SOUTH, WEST, EAST, STOP}
        """
        # Collect legal moves and successor states
        legalMoves = gameState.getLegalActions()

        # Choose one of the best actions
        scores = [self.evaluationFunction(gameState, action) for action in legalMoves]
        bestScore = max(scores)
        bestIndices = [index for index in range(len(scores)) if scores[index] == bestScore]
        chosenIndex = random.choice(bestIndices) # Pick randomly among the best

        "Add more of your code here if you want to"

        return legalMoves[chosenIndex]

    def evaluationFunction(self, currentGameState: GameState, action):
        """
        Design a better evaluation function here.

        The evaluation function takes in the current and proposed successor
        GameStates (pacman.py) and returns a number, where higher numbers are better.

        The code below extracts some useful information from the state, like the
        remaining food (newFood) and Pacman position after moving (newPos).
        newScaredTimes holds the number of moves that each ghost will remain
        scared because of Pacman having eaten a power pellet.

        Print out these variables to see what you're getting, then combine them
        to create a masterful evaluation function.
        """
        # Useful information you can extract from a GameState (pacman.py)
        successorGameState = currentGameState.generatePacmanSuccessor(action)
        newPos = successorGameState.getPacmanPosition()
        newFood = successorGameState.getFood()
        newGhostStates = successorGameState.getGhostStates()
        newScaredTimes = [ghostState.scaredTimer for ghostState in newGhostStates]
        foodList = newFood.asList()
        ghostPositions = successorGameState.getGhostPositions()
        capsules = successorGameState.getCapsules()

        "*** YOUR CODE HERE ***"
        # base score from the game state

        score = successorGameState.getScore()

        # 1) food-related: prefer closer food and fewer remaining foods
        if foodList:
            # distance to nearest food (Manhattan)
            minFoodDist = min(util.manhattanDistance(newPos, f) for f in foodList)
            foodDistFeature = 1.0 / (minFoodDist + 1)   # larger if nearer food
        else:
            # no food left -> very good
            foodDistFeature = 1.0

        # penalize remaining food count (encourages eating)
        remainingFoodFeature = -0.25 * len(foodList)
 
        # 2) capsule-related: penalize having many capsules left (encourage eating them when useful)
        capsuleFeature = -1.5 * len(capsules)

        # 3) ghosts: large negative if too close to an active (non-scared) ghost,
        #           encourage approaching scared ghosts (to eat them) moderately
        ghostFeature = 0.0
        for i, gpos in enumerate(ghostPositions):
            dist = util.manhattanDistance(newPos, gpos)
            scaredTime = newScaredTimes[i]
            if scaredTime == 0:
                # active ghost: heavy penalty for being very close
                if dist <= 1:
                    # immediate death/lose situation — return very bad score
                    return -999999 + score
                # farther ghosts contribute small negative term (inverse distance)
                ghostFeature += -2.0 / (dist + 0.1)
            else:
                # scared ghost: encourage getting closer to eat it (but not too strong)
                ghostFeature += (scaredTime) / (dist + 1)

        # combine all features with tuned weights
        final_value = score \
                  + 8.0 * foodDistFeature \
                  + remainingFoodFeature \
                  + capsuleFeature \
                  + ghostFeature

        return final_value

def scoreEvaluationFunction(currentGameState: GameState):
    """
    This default evaluation function just returns the score of the state.
    The score is the same one displayed in the Pacman GUI.

    This evaluation function is meant for use with adversarial search agents
    (not reflex agents).
    """
    return currentGameState.getScore()

class MultiAgentSearchAgent(Agent):
    """
    This class provides some common elements to all of your
    multi-agent searchers.  Any methods defined here will be available
    to the MinimaxPacmanAgent, AlphaBetaPacmanAgent & ExpectimaxPacmanAgent.

    You *do not* need to make any changes here, but you can if you want to
    add functionality to all your adversarial search agents.  Please do not
    remove anything, however.

    Note: this is an abstract class: one that should not be instantiated.  It's
    only partially specified, and designed to be extended.  Agent (game.py)
    is another abstract class.
    """

    def __init__(self, evalFn = 'scoreEvaluationFunction', depth = '2'):
        self.index = 0 # Pacman is always agent index 0
        self.evaluationFunction = util.lookup(evalFn, globals())
        self.depth = int(depth)

class MinimaxAgent(MultiAgentSearchAgent):
    """
    Your minimax agent (question 2)
    """

    def getAction(self, gameState: GameState):
        """
        Returns the minimax action from the current gameState using self.depth
        and self.evaluationFunction.

        Here are some method calls that might be useful when implementing minimax.

        gameState.getLegalActions(agentIndex):
        Returns a list of legal actions for an agent
        agentIndex=0 means Pacman, ghosts are >= 1

        gameState.generateSuccessor(agentIndex, action):
        Returns the successor game state after an agent takes an action

        gameState.getNumAgents():
        Returns the total number of agents in the game

        gameState.isWin():
        Returns whether or not the game state is a winning state

        gameState.isLose():
        Returns whether or not the game state is a losing state
        """
        "*** YOUR CODE HERE ***"

        numAgents=gameState.getNumAgents()
        maxDepth = self.depth

        def minimax(agentIndex, depth, gameState):
            # terminal or depth reached
            if depth == maxDepth or gameState.isWin() or gameState.isLose():
                return self.evaluationFunction(gameState)
            
            legalActions = gameState.getLegalActions(agentIndex)
            if not legalActions:
                return self.evaluationFunction(gameState)
            
            # Pacman's turn (maximizing player)
            if agentIndex == 0:
                maxEval = float('-inf')
                for action in legalActions:
                    successor = gameState.generateSuccessor(agentIndex, action)
                    # next agent is the first ghost if we have ghosts
                    if numAgents > 1:
                        eval = minimax(1, depth, successor)
                    else:
                        eval = minimax(0, depth + 1,successor)
                    maxEval = max(maxEval, eval)
                return maxEval
            
            # Ghosts' turn (minimizing players)
            else:
                minEval = float('inf')
                if agentIndex == numAgents - 1:
                    nextAgent = 0
                    nextDepth = depth + 1
                else:
                    nextAgent = agentIndex + 1
                    nextDepth = depth
                for action in legalActions:
                    successor = gameState.generateSuccessor(agentIndex, action)
                    eval = minimax(nextAgent, nextDepth, successor)
                    minEval = min(minEval, eval)
                return minEval
        
        # Root: choose the action gives the best minimax value
        bestAction = None
        bestScore = float('-inf')
        legalActions = gameState.getLegalActions()
        if not legalActions:
            return Directions.STOP
        for action in legalActions:
            successor = gameState.generateSuccessor(0, action)
            # If there are ghosts, next to evaluate is ghost 1 at same depth.
            # If no ghosts, we consider Pacman moved and depth advanced.
            if numAgents > 1:
                score = minimax(1, 0, successor)
            else:
                score = minimax(0, 1, successor)
            if score > bestScore:
                bestScore = score
                bestAction = action
    
        return bestAction
    
            

class AlphaBetaAgent(MultiAgentSearchAgent):
    """
    Your minimax agent with alpha-beta pruning (question 3)
    """

    def getAction(self, gameState: GameState):
        """
        Returns the minimax action using self.depth and self.evaluationFunction
        """
        "*** YOUR CODE HERE ***"

        # alpha: best value that the maximizer currently can guarantee at that level or above
        # beta: best value that the minimizer currently can guarantee at that level or above
        def Max(state, depth, alpha, beta):
            # terminal test or depth reached
            if depth == self.depth or state.isWin() or state.isLose():
                return self.evaluationFunction(state)
            v = float('-inf')
            for action in state.getLegalActions(0):
                v = max(v, Min(state.generateSuccessor(0, action), depth, 1, alpha, beta))
                # if v is greater than beta, prune
                if v > beta:
                    return v
                alpha = max(alpha, v)
            return v
        
        # min function for ghosts
        def Min(state, depth, agentIndex, alpha, beta):
            # terminal test or depth reached
            if depth == self.depth or state.isWin() or state.isLose():
                return self.evaluationFunction(state)
            v = float('inf')
            for action in state.getLegalActions(agentIndex):
                # if last ghost, go to max level next
                if agentIndex == state.getNumAgents() - 1:
                    v = min(v, Max(state.generateSuccessor(agentIndex, action), depth + 1, alpha, beta))
                # else, go to next ghost
                else:
                    v = min(v, Min(state.generateSuccessor(agentIndex, action), depth, agentIndex + 1, alpha, beta))
                # if v is less than alpha, prune
                if v < alpha:
                    return v
                beta = min(beta, v)
            return v
        
        bestAction = None
        bestScore = float('-inf')
        alpha = float('-inf')
        beta = float('inf')
        for action in gameState.getLegalActions(0):
            # first ghost is next
            score = Min(gameState.generateSuccessor(0, action), 0, 1, alpha, beta)
            if score > bestScore:
                bestScore = score
                bestAction = action
            if bestScore > beta:
                return bestAction
            alpha = max(alpha, bestScore)
        return bestAction
    

class ExpectimaxAgent(MultiAgentSearchAgent):
    """
      Your expectimax agent (question 4)
    """

    def getAction(self, gameState: GameState):
        """
        Returns the expectimax action using self.depth and self.evaluationFunction

        All ghosts should be modeled as choosing uniformly at random from their
        legal moves.
        """
        "*** YOUR CODE HERE ***"
        def expectimax(agentIndex, depth, gameState):
            # terminal or depth reached
            if depth == self.depth or gameState.isWin() or gameState.isLose():
                return self.evaluationFunction(gameState)
            
            legalActions = gameState.getLegalActions(agentIndex)
            if not legalActions:
                return self.evaluationFunction(gameState)
            
            # Pacman's turn (maximizing player)
            if agentIndex == 0:
                # Pacman always chooses the best action
                maxEval = float('-inf')
                for action in legalActions:
                    successor = gameState.generateSuccessor(agentIndex, action)
                    # next agent is the first ghost if we have ghosts
                    if gameState.getNumAgents() > 1:
                        eval = expectimax(1, depth, successor)
                    # next is pacman, depth increased
                    else:
                        eval = expectimax(0, depth + 1,successor)
                    maxEval = max(maxEval, eval)
                return maxEval
            
            # Ghosts' turn (expectation)
            else:
                expectedValue = 0.0
                numGhosts = gameState.getNumAgents()

                for action in legalActions:
                    successor = gameState.generateSuccessor(agentIndex, action)
                    # if last ghost, next is pacman at increased depth
                    if agentIndex == numGhosts - 1:
                        eval = expectimax(0, depth + 1, successor)
                    # else next ghost
                    else:
                        eval = expectimax(agentIndex + 1, depth, successor)
                    expectedValue += eval
                expectedValue /= len(legalActions)  # average over all actions
                return expectedValue
            
        # Root: choose the action gives the best expectimax value
        bestAction = None 
        bestScore = float('-inf')
        legalActions = gameState.getLegalActions()
        if not legalActions:
            return Directions.STOP
        
        for action in legalActions:
            successor = gameState.generateSuccessor(0, action)
            # If there are ghosts, next to evaluate is ghost 1 at same depth.
            # If no ghosts, we consider Pacman moved and depth advanced.
            if gameState.getNumAgents() > 1:
                score = expectimax(1, 0, successor)
            else:
                score = expectimax(0, 1, successor)
            if score > bestScore:
                bestScore = score
                bestAction = action
        
        return bestAction

def betterEvaluationFunction(currentGameState: GameState):
    """
    Your extreme ghost-hunting, pellet-nabbing, food-gobbling, unstoppable
    evaluation function (question 5).

    DESCRIPTION: <write something here so we know what you did>
    """
    "*** YOUR CODE HERE ***"
    # current base score from the game state
    score = currentGameState.getScore()

    pacmanPos = currentGameState.getPacmanPosition()
    foodList = currentGameState.getFood().asList()
    ghostStates = currentGameState.getGhostStates()
    ghostPositions = currentGameState.getGhostPositions()
    capsules = currentGameState.getCapsules()
    scaredTimes = [ghostState.scaredTimer for ghostState in ghostStates]

    # Feature 1: food-related: prefer closer food and fewer remaining foods
    # using 1 / (dist+1) to evaluate distance to closest food
    if foodList:
        closestFoodDist = min(manhattanDistance(pacmanPos, food) for food in foodList)
        foodDistanceFeature = 1.0 / (closestFoodDist + 1)  # larger if nearer food
    else:
        foodDistanceFeature = 1.0  # no food left -> very good
    
    # Feature 2: remaining food count (encourages eating)
    remainingFoodFeature = -0.5 * len(foodList)

    # Feature 3: capsule-related: penalize having many capsules left
    # We can adjust the weight a bit low to avoid over-prioritizing capsules
    capsuleFeature = -2.0 * len(capsules)

    # Feature 4: ghosts
    # large negative if too close to an active (non-scared) ghost,
    # encourage approaching scared ghosts moderately
    ghostFeature = 0.0
    for i, pos in enumerate(ghostPositions):
        dist = manhattanDistance(pacmanPos, pos)
        scaredTimes = scaredTimes[i]

        if scaredTimes > 0:
            # scared ghost: encourage getting closer to eat it (but not too strong)
            ghostFeature += 2 * (scaredTimes) / (dist + 1)
        else:
            # active ghost: heavy penalty for being very close
            if dist <= 1:
                return -999999 + score  # immediate death/lose situation
            ghostFeature += -3.0 / (dist + 0.1)  # farther ghosts contribute small negative term
    
    finalScore = score \
               + 10.0 * foodDistanceFeature \
               + remainingFoodFeature \
               + capsuleFeature \
               + ghostFeature
    
    return finalScore

# Abbreviation
better = betterEvaluationFunction
