# ElleWoods
Fall 2020, IT University of Copenhagen

## Description
ElleWoods is an automated-tool tailored for GDPR compliance that can assist companies in their audit of existing business processes. Themis transforms any given BPMN diagram into a finite state machine and determine compliance with the GDPR using model checking techniques. 

### Dependencies
ElleWoods is built with pytransitions: https://github.com/pytransitions/transitions, and PyNuSMV (https://pypi.org/project/pynusmv/)

## Quick start 
To run ElleWoods, we must provide an BPMN model in .bpmn-format, and a XML-file data that specific task use. 

```shell
python themis.py --bpmnxml bpmnmodel.bpmn --taskdataxml taskdata.xml
```

## Options
| Option      | param |
| ----------- | ----------- |
| `--bpmnxml` filepath | Path to *.xml-file representing the BPMN 
| `--taskdataxml` filepath | Path to *.xml-file matching tasks with data processing |
| `--rename-states` | - |
| `--compress-graph` | - |
| `--show-paths` | - |
| `--create-dot-graph` | - |


## Examples 
### Airtravel
![Airtravel BPMN diagram](examples/airtravel/airtravel.svg)

### Pizza
![Pizza BPMN diagram](examples/pizza/order-pizza.svg)

### Nobelprize
![Nobelprize BPMN diagram](examples/nobelprize/nobel-prize-multi-process.svg)

### Order fulfillment
![Order fulfillment BPMN diagram](examples/orderfulfillment/order_fulfillment.svg)

### Monthly Invoicing
![Monthly Invoicing BPMN diagram](examples/monthlyinvoicing/monthly_invoicing.svg)

### Hardware Retailer
![Hardware BPMN diagram](examples/hardwareretailer/hardware_retailer.svg)

