import string
import random
import untangle
import itertools


def get_task_label_groups(lst):
    groups = []
    lst.sort(key=lambda x: x['type'])
    for k, v in itertools.groupby(lst, key=lambda x: x['type']):
        groups.append((k, list(v)))
    return groups


def generate_task_data_files_no_violations(numbers):
    tree = untangle.parse('examples/performance/performance-taskdata-single-no-violations.xml')
    template = tree.children[0]

    for number in numbers:
        filepath = 'examples/performance/performance-taskdata-' + str(number) + '-no-violations.xml'
        variables = []
        n = len(template.TaskData)

        task_label_by_group = get_task_label_groups(template.TaskLabel)

        for i in range(0, number * n):
                variables.append(''.join((random.choices(string.ascii_uppercase + string.digits, k=5))) + str(i))

        set_var = [variables[i:i+number] for i in range(0, len(variables), number)] * n

        with open(filepath, 'w+') as f:
            print('<DataPoints>', file=f)
            for type,value in task_label_by_group:
                for (i,tasklabel) in enumerate(value):
                    print('<TaskLabel id="%s" name="%s" type="%s">' % (tasklabel['id'], tasklabel['name'], tasklabel['type']), file=f)
                    for v in set_var[i]:
                        print('     <Entry>%s</Entry>' % v, file=f)
                    print('</TaskLabel>', file=f)

            for (i,taskdata) in enumerate(template.TaskData):
                print('<TaskData id="%s" name="%s">' % (taskdata['id'], taskdata['name']), file=f)
                for v in set_var[i]:
                    print('     <Entry>%s</Entry>' % v, file=f)
                print('</TaskData>', file=f)

            for (i,datastore) in enumerate(template.DataStore):
                print('<DataStore id="%s" name="%s">' % (datastore['id'], datastore['name']), file=f)
                for v in set_var[i]:
                    print('     <Entry>%s</Entry>' % v, file=f)
                print('</DataStore>', file=f)
            print('</DataPoints>', file=f)


def generate_task_data_files_w_violations(numbers):
    tree = untangle.parse('examples/performance/performance-taskdata-single-no-violations.xml')
    template = tree.children[0]

    for number in numbers:
        filepath = 'examples/performance/performance-taskdata-' + str(number) + '-w-violations.xml'
        variables = []
        n = len(template)
        for i in range(0, number * n):
                variables.append(''.join((random.choices(string.ascii_uppercase + string.digits, k=5))) + str(i))

        with open(filepath, 'w+') as f:
            print('<DataPoints>', file=f)

            for (i,tasklabel) in enumerate(template.TaskLabel):
                print('<TaskLabel id="%s" name="%s" type="%s">' % (tasklabel['id'], tasklabel['name'], tasklabel['type']), file=f)
                for v in variables[:number]:
                    print('     <Entry>%s</Entry>' % v, file=f)
                    variables = variables[1:]
                print('</TaskLabel>', file=f)

            for (i,taskdata) in enumerate(template.TaskData):
                print('<TaskData id="%s" name="%s">' % (taskdata['id'], taskdata['name']), file=f)
                for v in variables[:number]:
                    print('     <Entry>%s</Entry>' % v, file=f)
                    variables = variables[1:]
                print('</TaskData>', file=f)

            for (i,datastore) in enumerate(template.DataStore):
                print('<DataStore id="%s" name="%s">' % (datastore['id'], datastore['name']), file=f)
                for v in variables[:number]:
                    print('     <Entry>%s</Entry>' % v, file=f)
                    variables = variables[1:]
                print('</DataStore>', file=f)
            print('</DataPoints>', file=f)