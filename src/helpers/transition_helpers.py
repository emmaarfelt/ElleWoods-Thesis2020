from src.models.bpmn import *

'''
Add each transition from parsed BPMN model to associated state.transition attribute
'''


def add_transitions_to_state_object(transitions, states, reset=False):
    for s in states:
        if reset and not isinstance(s, EndEvent):
            s.transitions = []
        for t in transitions:
            if t['source'] == s.label:
                s.transitions.append(t['dest'])
                s.transitions = list(set(s.transitions))

def dataassociation_transition(data_association, transitions):
    source = data_association.sourceref
    dest = data_association.targetref

    sourceref = source.label

    # remove any previous outgoing edges from source, and replace with datastore as source
    for n, t in enumerate(transitions):
        if t['source'] == sourceref:
            transitions[n] = {'trigger': t['trigger'], 'source': dest.label, 'dest': t['dest']}

    transitions.append({
        'trigger': '',
        'source': sourceref,
        'dest': dest.label
    })


def exclusive_transistion(source, dest, transitions, bpmn):
    sourceref = source.label
    targetref = dest.label

    if isinstance(dest, Exclusive):
        transitions.append({'trigger': '', 'source': sourceref, 'dest': targetref})

        triggers = dest.choice_labels
        triggers.reverse()  # Align transitions and labels
        try:
            targetrefs = [bpmn.sequences[out.cdata].targetref.label for out in dest.outgoing]
        except AttributeError:
            targetrefs = []

        if len(triggers) == len(targetrefs):
            for i, t in enumerate(targetrefs):
                transitions.append(
                    {'trigger': triggers[i], 'source': targetref, 'dest': t}
                )


def create_transitions(bpmn):
    transitions = []
    data_associations = []

    for t in bpmn.sequences.values():
        source = t.sourceref
        dest = t.targetref

        if isinstance(t, DataAssociation):
            data_associations.append(t)

        elif isinstance(dest, Exclusive):
            exclusive_transistion(source, dest, transitions, bpmn)

        elif isinstance(source, Exclusive):
            try:
                sourceref = source.label
                targetref = dest.label
                transitions.append({'trigger': '', 'source': sourceref, 'dest': targetref})
            except AttributeError:
                pass

        elif isinstance(source, StartEvent) and isinstance(dest, Task):
            sourceref = source.label
            targetref = dest.label

            transitions.append({'trigger': '', 'source': sourceref, 'dest': targetref})

        elif isinstance(source, Task) and isinstance(dest, StartEvent):
            sourceref = source.label
            targetref = dest.label

            transitions.append({'trigger': '', 'source': sourceref, 'dest': targetref})

        elif isinstance(dest, EndEvent):
            sourceref = source.label
            targetref = dest.label
            transitions.append({'trigger': '', 'source': sourceref, 'dest': targetref})

        elif isinstance(source, Task) and isinstance(dest, Task):
            sourceref = source.label
            targetref = dest.label

            transitions.append({'trigger': '', 'source': sourceref, 'dest': targetref})
        else:
            pass

    for l in data_associations:
        if isinstance(l, DataAssociation):
            dataassociation_transition(l, transitions)

    transitions = [t for t in transitions if t['trigger'] != 'None']
    return transitions


def sanitize_label(label):
    if label[0].isdigit():
        label = '_' + label
    text = label.strip().replace('\\', '\\\\').replace('&', '').replace(' ', '').replace('`', '').replace('*', '').replace('{', '').replace('}', '').replace('[', '').replace(']', '').replace('(', '').replace(')', '').replace('>', '').replace('#', '').replace('+', '').replace('-', '').replace('.', '').replace('!', '').replace('$', '').replace('?', '').replace('/', '').replace(',', '')
    return text