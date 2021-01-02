from __future__ import absolute_import
from transitions.extensions import GraphMachine as Machine


class Graph(object):
    def __init__(self, transitions, states, initial):
        self.transitions = transitions
        self.states = states
        self.initial = initial
        self.machine = Machine(
            model=self,
            states=self.states,
            initial=self.initial,
            transitions=self.transitions
        )

    def draw_machine(self, output):
        self.machine.get_graph().draw(output, prog='dot')


def create_states_for_visual_graph(states):
    states = [s.label for s in states]
    return states

def create_visual_graph_from_model(bpmn):
    initial = str(bpmn.start.label)
    states = create_states_for_visual_graph(bpmn.states.values())

    graph = Graph(transitions=bpmn.transitions, states=states, initial=initial)

    return graph
