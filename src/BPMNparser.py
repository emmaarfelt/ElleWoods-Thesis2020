from __future__ import absolute_import
import untangle
from src.helpers.event_helpers import *
from src.helpers.transition_helpers import *

'''
Parse data associations from database to tasks and vice versa. Stored in the supplementary *.xml file.
'''

def parse_task_data_associations(task_data):
    task_data_entries = {}
    try:
        task_data = untangle.parse(task_data).children[0].TaskData
        for td in task_data:
            task_data_entries[td['id']] = [e.cdata for e in td.children]
    except AttributeError:
        pass
    return task_data_entries


'''
Parse BPMN datastore objects and add to models database dictionary
'''
def parse_database(model, process, task_data):
    # Parse Data outputs and associations
    try:
        for data in process.bpmn_dataStoreReference:
            database = DataBase(node_id=data['id'], db_name=data['name'])
            model.add_database(data['id'], database)
        datastores = untangle.parse(task_data).children[0].DataStore
        for ds in datastores:
            data = [
                sanitize_label(e.cdata) for e in ds.children]
            model.databases.get(ds['id']).entries = data
    except AttributeError:
        pass


'''
For sequences going to or from Data Storage objects, create additional states or convert the data store object into a states, and 
label the appropriate 'use' or 'collect' action.
'''
def create_data_associations(model, task, bpmn_task, task_data_entries):
    for c in task.children:
        current_target = bpmn_task
        if c._name == 'bpmn_dataInputAssociation':
            try:
                datause = task_data_entries[task['id']]
            except KeyError:
                datause = {}

            # use variable
            for d in datause:
                d = sanitize_label(d)
                newTask = DataUsage(
                    node_id=c['id'] + '_data' + d,
                    label=c['id'] + "_use_" + str(d).strip(' '),
                    variables={'use': d})

                model.add_variable(state_id=newTask.label, collection='use', var=d)

                dat = DataAssociation(
                    sourceref=current_target,
                    targetref=newTask,
                    task_id=task['id'],
                    node_id=c['id'] + str(d))

                model.add_state(newTask.node_id, newTask)
                model.add_sequence(dat.node_id, dat)
                current_target = newTask

        elif c._name == 'bpmn_dataOutputAssociation':
            database = model.databases[c.bpmn_targetRef.cdata]
            datause = database.entries

            current_target = bpmn_task
            for d in datause:
                d = sanitize_label(d)
                newTask = DataUsage(
                    node_id=c.bpmn_targetRef.cdata + str(d),
                    label=sanitize_label(str(database.db_name)) + "_collect_" + str(d).strip(' '),
                    variables={'collect': d}
                )

                model.add_variable(state_id=newTask.label, collection='collect', var=d)

                dat = DataAssociation(
                    sourceref=current_target,
                    targetref=newTask,
                    task_id=task['id'],
                    node_id=c['id'] + str(d))

                model.add_state(newTask.node_id, newTask)
                model.add_sequence(dat.node_id, dat)
                current_target = newTask


'''
Parse the BPMN lanes and add to the model's lane dictionary
'''
def parse_lanes(model, process):
    # Parse Lanes and associate tasks and events to lanes
    try:
        for lane in process.bpmn_laneSet.bpmn_lane:
            for c in lane.children:
                model.lanes[c.cdata] = lane['name']
    except AttributeError:
        pass


'''
Get the name of the lane the given task id is associated with
'''
def get_lane(model, taskid):
    try:
        return model.lanes[taskid]
    except KeyError:
        return ''


'''
Parse BPMN sequenceflows and preserve choice labels for exclusive gateways if present
'''

def parse_sequences(model, sequenceflows, parsedxml):
    transitions = sequenceflows
    try:
        transitions = transitions + parsedxml.bpmn_collaboration.bpmn_messageFlow
    except AttributeError:
        pass

    # Parse connections between tasks as Sequence flows
    for sequences in transitions:
        sourceRef = model.lookup_task(sequences['sourceRef'])
        targetRef = model.lookup_task(sequences['targetRef'])

        seq = SequenceFlow(
            sourceref=sourceRef,
            targetref=targetRef,
            seq_id=sequences['id'],
            label=sequences['name']
        )

        if isinstance(sourceRef, Exclusive):
            sourceRef = model.states[sourceRef.node_id]
            if not model.states[sourceRef.node_id].choice_labels:
                sourceRef.choice_labels = [str(sequences['name']).strip()]
            else:
                sourceRef.choice_labels.append(str(sequences['name']).strip())

        model.add_sequence(sequences['id'], seq)


'''
Parse InclusiveGateways, ParallelGateways and ExclusiveGateways into seperate states and saving their associated outgoing sequenceflow ids
'''
def parse_gateways(model, process):
    # Parse exclusives
    gateways = []
    try:
        gateways = gateways + [i for i in process.bpmn_inclusiveGateway]
    except AttributeError:
        pass

    try:
        gateways = gateways + [i for i in process.bpmn_parallelGateway]
    except AttributeError:
        pass

    try:
        gateways = gateways + [i for i in process.bpmn_eventBasedGateway]
    except AttributeError:
        pass

    try:
        gateways = gateways + [i for i in process.bpmn_exclusiveGateway]
    except AttributeError:
        pass

    for e in gateways:
        outgoings = []
        for c in e.children:
            if c._name == 'bpmn_outgoing':
                outgoings.append(c)

        exclusive = Exclusive(
            node_id=e['id'],
            label=e['id'],
            choice_labels=None,
            outgoing=outgoings
        )

        model.add_state(e['id'], exclusive)


'''
Parse intermediateThrowEvents and intermediateCatchEvents if present in the graph. Each event is associated with a type and duration. 
'''


def parse_events(model, process, task_data_entries):
    # Parse events and set type
    events = []

    try:
        events = events + [i for i in process.bpmn_intermediateThrowEvent]
    except AttributeError:
        pass

    try:
        events = events + [i for i in process.bpmn_intermediateCatchEvent]
    except AttributeError:
        pass

    for e in events:
        event_type = get_event_type(e)
        duration = get_event_duration(e['name'])

        event = Event(
            node_id=e['id'],
            label=sanitize_label(e['name']),
            event_type=event_type,
            duration=duration
        )

        model.add_state(e['id'], event)
        create_data_associations(model, e, event, task_data_entries)


'''
Parse BPMN tasks and create states. A task might use data, and if so, the variables attribute contains this data.
'''


def parse_task(model, process, task_data_entries):
    tasks = process.bpmn_task

    try:
        tasks = tasks + [i for i in process.bpmn_userTask]
    except AttributeError:
        pass

    try:
        tasks = tasks + [i for i in process.bpmn_sendTask]
    except AttributeError:
        pass

    try:
        tasks = tasks + [i for i in process.bpmn_receiveTask]
    except AttributeError:
        pass

    try:
        tasks = tasks + [i for i in process.bpmn_manualTask]
    except AttributeError:
        pass

    # Parse tasks
    for task in tasks:
        try:
            datause = task_data_entries[task['id']]
        except (KeyError, TypeError):
            datause = []

        t = Task(
            node_id=task['id'],
            label=sanitize_label(task['name']),
            variables=datause
        )

        model.add_state(task['id'], t)
        create_data_associations(model, task, t, task_data_entries)


'''
Create a dictionary of {process_id : element} to look_up which process, if multiple, a element belongs to. 
'''


def create_elements_map(parsed_xml):
    elements_map = {}
    for p in parsed_xml.bpmn_process:
        for c in p.children:
            elements_map[c['id']] = p['id']

    return elements_map


'''
Create the main end event based on the chosen start event, such that the belong to the same process. 
Also return a list of the remaining end events to be transformed into regular tasks. 
'''


def get_end_events(process, elements_map, start):
    end_events = []

    if isinstance(process.bpmn_endEvent, list):
        main_end = process.bpmn_endEvent[0]
        for end in process.bpmn_endEvent:
            if elements_map[end['id']] == elements_map[start.node_id]:
                main_end = end
            else:
                end_events.append(end)
    else:
        main_end = process.bpmn_endEvent

    main_end_event = EndEvent(
        incoming=main_end.bpmn_incoming,
        node_id=main_end['id'],
        label=sanitize_label(main_end['name']) if main_end['name'] else "End",
    )
    main_end_event.transitions.append(main_end_event.label)

    return (main_end_event, end_events)


'''
Create the main start event based the type of the present start events. The start event without triggers
is chosen as the main start event.  
Also return a list of the remaining start events to be transformed into regular tasks. 
'''


def get_start_events(process):
    start_events = []

    if isinstance(process.bpmn_startEvent, list):
        main_start = process.bpmn_startEvent[0]
        for start in process.bpmn_startEvent:
            if not get_event_type(start):
                main_start = start
            else:
                start_events.append(start)
    else:
        main_start = process.bpmn_startEvent

    main_start_event = StartEvent(
        outgoing=main_start.bpmn_outgoing,
        node_id=main_start['id'],
        label=sanitize_label(main_start['name']) if main_start['name'] else 'Start')

    return (main_start_event, start_events)


'''
Add the given node or list of nodes to the model as a state
'''


def add_state_to_model(model, node):
    if isinstance(node, list):
        for n in node:
            try:
                if n._name == 'bpmn_endEvent':
                    t = EndEvent(
                        node_id=n['id'],
                        label=sanitize_label(n['name']) if n['name'] else n['id'],
                        incoming=[]
                    )
                    t.transitions.append(model.end.label)
                    model.add_state(n['id'], t)
                else:
                    t = Task(
                        node_id=n['id'],
                        label=sanitize_label(n['name']) if n['name'] else n['id'],
                    )
                    model.add_state(n['id'], t)
            except AttributeError:
                t = Task(
                    node_id=n['id'],
                    label=sanitize_label(n['name']) if n['name'] else n['id'],
                )
                model.add_state(n['id'], t)

    elif isinstance(node, Node):
        model.add_state(node.node_id, node)
    else:
        t = Task(
            node_id=node['id'],
            label=sanitize_label(node['name']),
        )
        model.add_state(node['id'], t)


'''
Parse the given .bpmn of BPMN and supplementary taskdata *.xml file. 
If more than one bpmn_process, merge them into one.
Returns a BPMN model
'''


def parseXML_u(xmlfile, taskdata) -> BPMN:
    tree = untangle.parse(xmlfile)
    parsedXML = tree.children[0]
    process = parsedXML.bpmn_process
    elements_map = create_elements_map(parsedXML)

    if isinstance(process, list):
        main_process = process[0]
        for p in process[1:]:
            for c in p.children:
                main_process.add_child(c)
        process = main_process
    else:
        process = parsedXML.bpmn_process

    (main_start_event, start_events) = get_start_events(process)
    (main_end_event, end_events) = get_end_events(process, elements_map, main_start_event)

    model = BPMN(start=main_start_event, end=main_end_event, variables_library=Variables())

    parse_lanes(model, process)

    add_state_to_model(model, main_start_event)
    add_state_to_model(model, main_end_event)
    add_state_to_model(model, end_events)
    add_state_to_model(model, start_events)

    task_data_entries = parse_task_data_associations(taskdata)
    parse_database(model, process, taskdata)

    parse_events(model, process, task_data_entries)
    parse_task(model, process, task_data_entries)
    parse_gateways(model, process)
    parse_sequences(model, process.bpmn_sequenceFlow, parsedXML)


    return model
