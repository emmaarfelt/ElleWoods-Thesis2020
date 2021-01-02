from __future__ import absolute_import

import pathlib
import sys
from src.BPMNparser import parseXML_u
from src.KSembedding import create_ks_from_model
from src.helpers.visual_graph_helpers import create_compressed_graph
from src.models.graph import create_visual_graph_from_model
from src.NuSMV import *
from src.helpers.rename_helper import rename_states


def main(bpmn_xml, task_data_xml, rename_flag_set=False, compress_flag_set=False, show_paths=False):
    bpmn = parseXML_u(bpmn_xml, task_data_xml)
    ks = create_ks_from_model(bpmn, task_data_xml)
    if rename_flag_set:
        rename_states(ks)
    if compress_flag_set:
        create_compressed_graph(ks)
    visual_graph = create_visual_graph_from_model(ks)
    model_name = pathlib.PurePath(bpmn_xml).name
    visual_graph.draw_machine('lib/graphdiagrams/' + model_name + '.png')
    run_nusmv(model_name, ks, show_paths)

if __name__ == "__main__":
    bpmnxml = taskdataxml = ''
    rename_flag_set = compress_flag_set = show_paths = False

    for i, arg in enumerate(sys.argv):
        if arg == '--bpmnxml':
            bpmnxml = sys.argv[i+1]
        if arg == '--taskdataxml':
            taskdataxml = sys.argv[i+1]
        if arg == '--rename-states':
            rename_flag_set = True
        if arg == '--compress-graph':
            compress_flag_set = True
        if arg == '--show-paths':
            show_paths = True

    main(bpmnxml, taskdataxml, rename_flag_set, compress_flag_set, show_paths)

