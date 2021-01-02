class Node(object):
    def __init__(self, incoming, outgoing, node_id, label):
        self.incoming = incoming
        self.outgoing = outgoing
        self.node_id = node_id
        self.label = label
        self.transitions = []
        self.duration = 0


class StartEvent(Node):
    def __init__(self, outgoing, node_id, label='Start'):
        super(StartEvent, self).__init__(incoming=[], outgoing=outgoing, node_id=node_id, label=label)


class EndEvent(Node):
    def __init__(self, incoming, node_id, label='End'):
        super(EndEvent, self).__init__(incoming=incoming, outgoing=[], node_id=node_id, label=label)


class Process(object):
    def __init__(self, name, process_id, elements):
        self.name = name
        self.process_id = process_id
        self.elements = elements


class Connection(object):
    def __init__(self, sourceref, targetref):
        self.sourceref = sourceref
        self.targetref = targetref


class SequenceFlow(Connection):
    def __init__(self, seq_id, sourceref, targetref, label=None):
        super(SequenceFlow, self).__init__(sourceref=sourceref, targetref=targetref)
        self.seq_id = seq_id
        if not label:
            self.label = ''
        else:
            self.label = label


class DataAssociation(Connection):
    def __init__(self, sourceref, targetref, task_id, node_id):
        super(DataAssociation, self).__init__(sourceref=sourceref, targetref=targetref)
        self.task_id = task_id
        self.node_id = node_id


class DataBase():
    def __init__(self, node_id, db_name, entries=[]):
        self.node_id = node_id
        self.db_name = db_name
        self.entries = entries


class States(object):
    def __init__(self, node_id, label, lane='', variables={}, duration=0):
        self.node_id = node_id
        self.label = str(label)
        self.lane = lane
        self.variables = variables
        self.duration = duration
        self.transitions = []


class Task(States):
    pass


class Event(Task):
    def __init__(self, node_id, label, event_type=None, duration=0):
        super(Event, self).__init__(node_id=node_id, label=label, variables={})
        self.duration = duration
        self.event_type = event_type


class Parallel(States):
    pass


class Exclusive(States):
    def __init__(self, node_id, label, choice_labels=[], outgoing=None):
        super(Exclusive, self).__init__(node_id=node_id, label=label, variables={}, duration=0)
        self.choice_labels = choice_labels
        self.outgoing = outgoing


class DataUsage(States):
    pass


class Variables(object):
    def __init__(self):
        self.collect = {}  # 's0':x, 's1':y
        self.use = {}
        self.delete = {}
        self.consent = {}
        self.revoke = {}
        self.access = {}
        self.deletion = {}
        self.objection = {}
        self.share = {}
        self.legal_grounds = {}
        self.restrictions = {}
        self.inform = {}
        self.breach = {}
        self.notification = {}
        self.transfer = {}
        self.transfer_grounds = {}

    def get_collections(self):
        return [('collect', self.collect),
                ('use', self.use),
                ('delete', self.delete),
                ('consent', self.consent),
                ('revoke', self.revoke),
                ('access', self.access),
                ('deletion', self.deletion),
                ('objection', self.objection),
                ('share', self.share),
                ('legal_grounds', self.legal_grounds),
                ('restriction', self.restrictions),
                ('inform', self.inform),
                ('notification', self.notification),
                ('transfer', self.transfer),
                ('breach', self.breach),
                ('transfer_grounds', self.transfer_grounds)
                ]

    def get_collection(self, name):
        collections = dict(self.get_collections())
        return collections[name]

    def replace_collection(self, collection, new_collection):
        if collection == 'collect':
            self.collect = new_collection
        elif collection == 'use':
            self.use = new_collection
        elif collection == 'delete':
            self.delete = new_collection
        elif collection == 'consent':
            self.consent = new_collection
        elif collection == 'revoke':
            self.revoke = new_collection
        elif collection == 'access':
            self.access = new_collection
        elif collection == 'deletion':
            self.deletion = new_collection
        elif collection == 'objection':
            self.objection = new_collection
        elif collection == 'share':
            self.share = new_collection
        elif collection == 'legal_grounds':
            self.legal_grounds = new_collection
        elif collection == 'restriction':
            self.restrictions = new_collection
        elif collection == 'inform':
            self.inform = new_collection
        elif collection == 'breach':
            self.breach = new_collection
        elif collection == 'notification':
            self.notification = new_collection
        elif collection == 'transfer':
            self.transfer = new_collection
        elif collection == 'transfer_grounds':
            self.transfer_grounds = new_collection
        else:
            pass

    def get_all_non_empty_collection(self):
        collections = self.get_collections()
        return [(n, c) for (n, c) in collections if c]


class BPMN:
    def __init__(self, start, end, variables_library):
        self.lanes = {}
        self.start = start
        self.end = end
        self.states = {}
        self.sequences = {}
        self.databases = {}
        self.transitions = []
        self.variables_library = variables_library

    def add_state(self, state_id, state):
        self.states[state_id] = state

    def add_sequence(self, seqid, seq):
        self.sequences[seqid] = seq

    def lookup_task(self, task_id):
        if self.start.node_id == task_id:
            return self.start
        elif self.end.node_id == task_id:
            return self.end
        else:
            try:
                return self.states[task_id]
            except KeyError:
                return None

    def add_database(self, dbname, database):
        self.databases[dbname] = database

    def add_variable(self, state_id, collection, var):
        if collection == 'collect':
            self.variables_library.collect[state_id] = var
        elif collection == 'use':
            self.variables_library.use[state_id] = var
        elif collection == 'delete':
            self.variables_library.delete[state_id] = var
        elif collection == 'consent':
            self.variables_library.consent[state_id] = var
        elif collection == 'revoke':
            self.variables_library.revoke[state_id] = var
        elif collection == 'access':
            self.variables_library.access[state_id] = var
        elif collection == 'deletion':
            self.variables_library.deletion[state_id] = var
        elif collection == 'objection':
            self.variables_library.objection[state_id] = var
        elif collection == 'share':
            self.variables_library.share[state_id] = var
        elif collection == 'legal_grounds':
            self.variables_library.legal_grounds[state_id] = var
        elif collection == 'restriction':
            self.variables_library.restrictions[state_id] = var
        elif collection == 'inform':
            self.variables_library.inform[state_id] = var
        elif collection == 'breach':
            self.variables_library.breach[state_id] = var
        elif collection == 'notification':
            self.variables_library.notification[state_id] = var
        elif collection == 'transfer':
            self.variables_library.transfer[state_id] = var
        elif collection == 'transfer_grounds':
            self.variables_library.transfer_grounds[state_id] = var
        else:
            pass
