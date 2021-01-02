import untangle
from src.helpers.transition_helpers import create_transitions, add_transitions_to_state_object, sanitize_label
from src.models.bpmn import DataUsage, DataAssociation

'''
Create additional states for each distinct variable that are consented, deleted etc. based on the task labels added in the supplementary *.xml file.
'''
def create_variables_states(model, task_label_entry):
    tl = task_label_entry
    var = tl.children
    current_target = model.lookup_task(tl['id'])

    for v in var:
        if current_target:
            d = sanitize_label(v.cdata)
            newTask = DataUsage(
                node_id=tl['id'] + '_data' + str(d),
                label=tl['id'] + "_" + tl['type'] + "_" + str(d).strip(' '),
                variables={tl['type']: d})

            model.add_variable(state_id=newTask.label, collection=tl['type'], var=d)

            dat = DataAssociation(
                sourceref=current_target,
                targetref=newTask,
                task_id=tl['id'],
                node_id=tl['id'] + str(d))

            model.add_state(newTask.node_id, newTask)
            model.add_sequence(dat.node_id, dat)
            current_target = newTask


def parse_task_labels(task_data, model):
    try:
        task_data = untangle.parse(task_data).children[0].TaskLabel
        for tl in task_data:
            create_variables_states(model, tl)
    except AttributeError:
        pass

def create_ks_from_model(model, taskdata):
    parse_task_labels(taskdata, model)

    transitions = create_transitions(model)
    model.transitions = transitions

    add_transitions_to_state_object(transitions, model.states.values())

    return model
