import re


def get_event_duration(label):
    '''
    Parse the event name to calculate duration in seconds
    '''
    try:
        numbers = re.match(r"(?P<number>[\d-]+) (?P<time>[\D]+)", label)
    except AttributeError:
        return 0

    hours = re.compile('[hour\b | hours\b | hour(s)\b]*$')
    days = re.compile('[day\b | days\b | day(s)\b]*$')
    weeks = re.compile('[week\b | weeks\b | week(s)\b]*$')
    months = re.compile('[month\b | months\b | month(s)\b]*$')
    years = re.compile('[year\b | years\b | year(s)\b]*$')

    try:
        number = numbers.group('number').strip()
    except AttributeError:
        return 0

    if hours.match(numbers.group('time')):
        return int(number) * 60 * 60

    if days.match(numbers.group('time')):
        return int(number) * 24 * 60 * 60

    if weeks.match(numbers.group('time')):
        return int(number) * 7 * 24 * 60 * 60

    if months.match(numbers.group('time')):
        return int(number) * 30 * 24 * 60 * 60

    if years.match(numbers.group('time')):
        return int(number) * 365 * 24 * 60 * 60

    return 0


def get_event_type(event):
    event_types = dict((x, x) for x in ['bpmn_timerEventDefinition',
                                        'bpmn_messageEventDefinition',
                                        'bpmn_escalationEventDefinition',
                                        'bpmn_conditionalEventDefinition',
                                        'bpmn_linkEventDefinition',
                                        'bpmn_compensateEventDefinition'
                                        ])

    for c in event.children:
        try:
            return event_types[c._name]
        except KeyError:
            pass
