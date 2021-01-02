import numpy as np
import time
from numpy.lib.stride_tricks import as_strided
import copy

from radcad import Model, Simulation, Experiment
from radcad.engine import Engine, Backend


def grid_nD(arr):
    assert all(_len>2 for _len in arr.shape)
    
    nDims = len(arr.shape)
    newShape = [_len-2 for _len in arr.shape]
    newShape.extend([3] * nDims)
    
    newStrides = arr.strides + arr.strides
    return as_strided(arr, shape=newShape, strides=newStrides)

def loop(params, substep, state_history, previous_state):        
    ruleOfLifeAlive = params['ruleOfLifeAlive']
    ruleOfLifeDead = params['ruleOfLifeDead']
    dims = params['dims']
    nd_slice = params['nd_slice']
    
    full = copy.deepcopy(previous_state['full'])
    board = full[nd_slice]
    
    neighborhoods = grid_nD(full)
    sumOver = tuple(-(i+1) for i in range(dims))
    neighborCt = np.sum(neighborhoods, sumOver) - board
    
    board[:] = np.where(board, 
                        ruleOfLifeAlive[neighborCt], 
                        ruleOfLifeDead[neighborCt])

    return {'board': board, 'full': full}

def state_update_full(params, substep, state_history, previous_state, policy_input):
    return 'full', policy_input['full']
    
def state_update_board(params, substep, state_history, previous_state, policy_input):
    return 'board', policy_input['board']
