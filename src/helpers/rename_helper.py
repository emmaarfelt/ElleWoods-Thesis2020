from src.models.bpmn import EndEvent, StartEvent
from itertools import groupby


def find_all_paths(graph, start, end, path=[]):
        path = path + [start]
        if start == end:
            return [path]
        if start not in graph:
            return []
        paths = []
        for node in graph[start]:
            if node not in path:
                newpaths = find_all_paths(graph, node, end, path)
                for newpath in newpaths:
                    paths.append(newpath)
        return paths


def create_mapping_from_old_to_new_labels(states, order):
    states_by_name = {s.label: s for s in states}
    counter = 0
    var_counter = 0
    labels_map = {}
    for s in order:
        st = states_by_name[s]
        if isinstance(st, EndEvent) or isinstance(st, StartEvent):
            labels_map[st.label] = "s%s" % counter
            counter += 1
        else:
            if st.variables:
                labels_map[st.label] = "s%s_%s" % (counter, var_counter)
                var_counter += 1
            else:
                labels_map[st.label] = "s%s" % counter
                var_counter = 0
                counter += 1

    return labels_map


def rename_states(bpmn):
    start = bpmn.start.label
    end = bpmn.end.label
    states = bpmn.states.values()
    transitions = bpmn.transitions
    name_graph = {}

    for d in transitions:
        if d['source'] in name_graph:
            name_graph[d['source']].append(d['dest'])
        else:
            name_graph[d['source']] = [d['dest']]

    paths = sum(find_all_paths(name_graph, start, end), [])
    order = dict(groupby(paths)).keys()
    labels_map = create_mapping_from_old_to_new_labels(states, order)

    for t in bpmn.transitions:
        try:
            t['source'] = labels_map[t['source']]
            t['dest'] = labels_map[t['dest']]
        except KeyError:
            pass

    for s in bpmn.states.values():
        try:
            s.label = labels_map[s.label]
            s.transitions = [labels_map[t] for t in s.transitions]

        except KeyError:
            pass

    for c in bpmn.variables_library.get_all_non_empty_collection():
        try:
            variable = [(labels_map[s], v) for (s, v) in list(c[1].items())]
            bpmn.variables_library.replace_collection(c[0], dict(variable))
        except KeyError:
            pass

