from __future__ import absolute_import

import os
import pathlib
import sys
import timeit
import cProfile
from datetime import datetime

from src.BPMNparser import parseXML_u
from src.KSembedding import create_ks_from_model
from src.NuSMV import run_nusmv
from src.helpers.performance_helper import generate_task_data_files_no_violations, \
    generate_task_data_files_w_violations


def create_test_files():
    generate_task_data_files_no_violations([1,10,20,30,40,50])
    generate_task_data_files_w_violations([1,10,20,30,40,50])

def run_nusmv_themis(bpmn_xml, task_data_xml):
    bpmn = parseXML_u(bpmn_xml, task_data_xml)
    ks = create_ks_from_model(bpmn, task_data_xml)
    model_name = pathlib.PurePath(bpmn_xml).name
    sys.stdout = open(os.devnull, 'w')
    run_nusmv(model_name, ks)
    sys.stdout = sys.__stdout__


def get_test_cases():
    tasks = [10,20,30,40,50]
    task_variables = [1,10,20,30,40,50]

    test = []
    for no_tasks in tasks:
        for no_task_variables in task_variables:
            no_violations_case = ('No violations', 'examples/performance/performance-%d-tasks.bpmn' % no_tasks, 'examples/performance/performance-taskdata-%d-no-violations.xml' % no_task_variables, no_tasks, no_task_variables)
            with_violations_case = ('With violations', 'examples/performance/performance-%d-tasks.bpmn' % no_tasks,
                                     'examples/performance/performance-taskdata-%d-w-violations.xml' % no_task_variables,
                                     no_tasks, no_task_variables)
            test.append(no_violations_case)
            test.append(with_violations_case)
    return test


'''
Running with 10 tasks results in a kripke structure with 22 states.
'''
def time_themis(bpmn_xml, task_data_xml):
    result = timeit.Timer(stmt=lambda: run_nusmv_themis(bpmn_xml=bpmn_xml, task_data_xml=task_data_xml)).timeit(number=1)
    return result

def run():
    print("Running...")
    test_cases = get_test_cases()

    dato = datetime.now().strftime("%d-%m-%H:%M")
    filepath = 'lib/performance/result-' + dato + '.txt'
    with open(filepath, 'w+') as f:
        for (desc, bpmn, taskdata, no_of_tasks, no_of_variables) in test_cases:
            print('%s with %s tasks and %s task data variables:' % (desc, no_of_tasks, no_of_variables), file=f)
            print('%s with %s tasks and %s task data variables...' % (desc, no_of_tasks, no_of_variables))
            # cProfile.runctx('run_nusmv_themis(bpmn_xml=bpmn, task_data_xml=taskdata)', {'bpmn': bpmn, 'taskdata':taskdata, 'run_nusmv_themis': run_nusmv_themis}, {})
            result = time_themis(bpmn_xml=bpmn, task_data_xml=taskdata)
            print('Result: %s' % (result), file=f)
            print('%s,%s,%s,%s' % (desc, no_of_tasks, no_of_variables, result), file=f)
            print('\n', file=f)

if __name__ == '__main__':
    run()
