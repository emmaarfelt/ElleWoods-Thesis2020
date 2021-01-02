from __future__ import absolute_import
from __future__ import print_function

from src.helpers.transition_helpers import add_transitions_to_state_object

'''
Simple search algorithm
'''
def search(values, searchFor):
    for v in values.values():
        if searchFor in v.label:
            return v
    return None

'''
Parent function for union-find algorithm
'''
def findParent(unions, current):
    while(unions[current] != current):
        current = unions[current]

    return current

def create_compressed_graph(bpmn):
    initial = bpmn.start.label

    '''
    Removes any states without variables or transitions label. Relevant for compressing larger graphs. 
    Nice to have: introduce flag that will run this method. Perhaps also a flag for renaming states?  
    '''

    unions = dict([(s.label, s.label) for s in bpmn.states.values()])

    for s in bpmn.states.values():
        outgoing = [node for node in bpmn.transitions if node['source'] == s.label]

        if len(outgoing) == 1:
            try:
                if not s.variables:
                    unions[outgoing[0]['source']] = outgoing[0]['dest']
            except AttributeError:
                pass

    parents = {initial: initial}

    for k in unions.keys():
        parents[k] = findParent(unions, k)

    bpmn.states = {k:v for k,v in bpmn.states.items() if v.label in parents.values()}

    for trans in bpmn.transitions:
        trans['source'] = parents[trans['source']]
        trans['dest'] = parents[trans['dest']]

    bpmn.transitions = [t for t in bpmn.transitions if t['source'] != t['dest']]  # Remove loops and empty triggers
    add_transitions_to_state_object(bpmn.transitions, bpmn.states.values(), reset=True)