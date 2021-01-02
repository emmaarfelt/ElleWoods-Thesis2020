from __future__ import absolute_import

from pynusmv.exception import *
from pynusmv.glob import prop_database, load, flatten_hierarchy, build_model, compute_model, load_from_file
from pynusmv.init import init_nusmv, deinit_nusmv
from pynusmv.mc import check_ctl_spec, check_ltl_spec, explain
from pynusmv.prop import propTypes


class State(object):
    def __init__(self, states, node_id, label, lane):
        self.node_id = node_id,
        self.label = label,
        self.lane = lane,
        self.states = states


class Module(object):
    def __init__(self, states):
        self.states = states


def indent(text, level) -> str:
    return '\t' * level + text


def print_state_module(file):
    print("MODULE state(inc,bound)", file=file)
    print("VAR", file=file)
    print(indent("duration: 0..bound;", 1), file=file)

    print("ASSIGN", file=file)
    print(indent("init(duration) := 0;", 1), file=file)
    print(indent("next(duration) := inc ? (duration + 1) mod (bound + 1) : duration;", 1), file=file)

    print("DEFINE", file=file)
    print(indent("limit := duration = bound;", 1), file=file)
    print("\n", file=file)


def print_specification_explanation(explanation):
    states = []
    loop=False
    for state, inputs in zip(explanation[::2], explanation[1::2]):
        if state == explanation[-1]:
            loop=True
        states.append(state.get_str_values()['STATE'])

    path = ' -> '.join(states) + '(loop)' if loop else ' -> '.join(states)
    print(path)

'''
Launch NuSMV with pynusmv library and print any specification/property that the model does not satisfy
'''


def run_model_in_nusmv(filename, get_path=False):
    init_nusmv()
    load_from_file(filename)
    compute_model(keep_single_enum=True)
    fsm = prop_database().master.bddFsm
    propDb = prop_database()

    for prop in propDb:
        spec = prop.expr
        status = check_ctl_spec(fsm, spec) if prop.type == propTypes['CTL'] else check_ltl_spec(spec)
        if status is False:
            print('Specification', str(spec), 'is', str(status))
            if get_path:
                explanation = explain(fsm, fsm.init, spec)
                print_specification_explanation(explanation)

    deinit_nusmv()


def create_smv_file(filename, bpmn):
    filepath = 'lib/nusmv/models/' + filename + '.smv'
    with open(filepath, 'w') as f:
        print("MODULE main", file=f)
        print("VAR", file=f)

        states_label = [s.label for s in bpmn.states.values()]
        states = ','.join(states_label)
        print(indent("STATE" + ' : {' + states + '};', 1), file=f)

        for c in bpmn.variables_library.get_collections():
            name = str(c[0]).upper()
            if name == 'ACCESS':
                var = 'requested, granted, None'
            elif name == 'DELETION':
                var = 'requested, done, None'
            elif name == 'OBJECTION':
                var = 'objected, None'
            elif name == 'RESTRICTION':
                var = 'requested, None'
            elif name == 'NOTIFICATION':
                var = 'ds,sa,done, None'
            elif name == 'TRANSFER_GROUNDS':
                var = 'bcr, appropriate_safeguards, adequacy_decision, None'
            elif name == 'BREACH' or name == 'TRANSFER':
                continue
            else:
                variable = [v for v in c[1].values()] + ['None']
                var = ','.join(variable)
            print(indent(name + ' : {' + var + '};', 1), file=f)

        if bpmn.variables_library.get_collection('transfer'):
            transfer_states = bpmn.variables_library.get_collection('transfer').keys()
            s = [("STATE = %s" % s) for s in transfer_states]
            v = "|".join(s)
            print('DEFINE TRANSFER := %s;' % v, file=f)

        if bpmn.variables_library.get_collection('breach'):
            breach_states = bpmn.variables_library.get_collection('breach').keys()
            s = [("STATE = %s" % s) for s in breach_states]
            v = "|".join(s)
            print('DEFINE BREACH := %s;' % v, file=f)

        print("ASSIGN", file=f)

        for c in bpmn.variables_library.get_collections():
            if c[0].upper() == 'TRANSFER' or c[0].upper() == 'BREACH':
                continue
            print(indent("init(%s) := None;" % str(c[0]).upper(), 1), file=f)

        print(indent("init(STATE) := %s;" % bpmn.start.label, 1), file=f)

        print(indent("next(STATE) :=", 1), file=f)
        print(indent("case", 2), file=f)

        for s in bpmn.states.values():
            transitions = ','.join([t for t in s.transitions])
            if transitions is not '':
                print(indent("STATE = %s : { %s };" % (s.label, transitions), 3), file=f)
            else:
                print(indent("STATE = %s : { %s };" % (s.label, s.label), 3), file=f)

        print(indent("esac;", 2), file=f)

        for c in bpmn.variables_library.get_all_non_empty_collection():
            name = str(c[0]).upper()
            if c[0].upper() == 'TRANSFER' or c[0].upper() == 'BREACH':
                continue
            variable = list(c[1].items())
            print(indent("next(%s) :=" % name, 1), file=f)
            print(indent("case", 2), file=f)

            for (s, v) in variable:
                print(indent("STATE = %s : %s;" % (s, v), 3), file=f)
            print(indent("TRUE: None;", 3), file=f)
            print(indent("esac;", 2), file=f)


        '''
        GDPR Specifications
        '''
        # Data minimisation
        collect_variables = bpmn.variables_library.get_collection('collect').values()
        for v in collect_variables:
            print('SPEC', file=f)
            print(indent('AG(COLLECT = %s -> EF USE = %s);' % (v, v), 1), file=f)

        # Storage limitation
        for v in collect_variables:
            print('LTLSPEC', file=f)
            print(indent('G (COLLECT = %s -> F DELETE = %s);' % (v, v), 1), file=f)

        # Lawful processing
        use_variables = bpmn.variables_library.get_collection('use').values()
        for v in use_variables:
            print('LTLSPEC', file=f)
            print(indent('G (USE = %s -> O ( CONSENT = %s | LEGAL_GROUNDS = %s ) );' % (v, v, v), 1), file=f)

        # Conditions on consent
        for v in use_variables:
            print('LTLSPEC', file=f)
            print(indent('G (USE = %s -> O LEGAL_GROUNDS = %s | ( REVOKE != %s S CONSENT = %s ) );' % (v, v, v, v), 1),
                  file=f)

        # Information on Collection
        for v in collect_variables:
            print('LTLSPEC', file=f)
            print(indent('G (COLLECT = %s -> X INFORM = %s | O INFORM = %s);' % (v, v, v), 1), file=f)

        # Right to erasure
        for v in use_variables:
            print('LTLSPEC', file=f)
            print(indent('G (USE = %s -> ! O DELETE = %s);' % (v, v), 1), file=f)

        if bpmn.variables_library.get_collection('deletion'):
            for v in collect_variables:
                print('LTLSPEC', file=f)
                print(indent('G (DELETION = requested -> F DELETE = %s);' % (v), 1), file=f)
            print('LTLSPEC', file=f)
            print(indent('G (DELETION = requested -> F DELETION = done);', 1), file=f)

            share_variables = bpmn.variables_library.get_collection('share').values()
            for v in share_variables:
                print('LTLSPEC', file=f)
                print(indent('G (DELETION = requested & O SHARE = %s -> F NOTIFICATION = done);' % v, 1), file=f)

        # Right to restriction
        if bpmn.variables_library.get_collection('restriction'):
            for v in use_variables:
                print('LTLSPEC', file=f)
                print(indent('G (USE = %s -> (RESTRICTION != requested S (LEGAL_GROUNDS = %s | CONSENT = %s));' % (v, v, v), 1), file=f)

        # Right to objection
        if bpmn.variables_library.get_collection('objection'):
            for v in use_variables:
                print('LTLSPEC', file=f)
                print(indent('G (USE = %s -> (OBJECTION != objected S LEGAL_GROUNDS = %s));' % (v, v), 1), file=f)

        # Right to access
        if bpmn.variables_library.get_collection('access'):
            print('LTLSPEC', file=f)
            print(indent('G (ACCESS = requested -> F ACCESS = granted);', 1), file=f)

        # Notification of Data Breach
        if bpmn.variables_library.get_collection('breach'):
            print('LTLSPEC', file=f)
            print(indent('G (BREACH = TRUE -> F NOTIFICATION = sa & F NOTIFICATION = ds );', 1), file=f)

        # General principles for transfers
        if bpmn.variables_library.get_collection('transfer'):
            print('LTLSPEC', file=f)
            print(indent('G (TRANSFER = TRUE -> O (TRANSFER_GROUNDS = adequacy_decision | TRANSFER_GROUNDS = bcr | TRANSFER_GROUNDS = appropriate_safeguards));', 1), file=f)

        return filepath


def run_nusmv(filename, bpmn, get_paths=False):
    filepath = create_smv_file(filename, bpmn)
    try:
        run_model_in_nusmv(filepath, get_paths)
    except NuSMVParsingError as error:
        print(error)
    except NuSMVCannotFlattenError as error:
        print(error)
