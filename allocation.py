import pandas as pd
import copy

FILE_NAME = 'random_pref_list.xlsx'

pref_table = pd.read_excel(FILE_NAME, index_col=0)
pref_table = pref_table.sample(frac=1)

topics = list(pref_table.columns)
topic_num = len(topics)
names = list(pref_table.index)

# Set min and max number of teachers per topic
t_min, t_max = (1, 3)

spec = {topic: [] for topic in topics}

def fitness(spec):
    """Returns fitness for current spec
    
    Arguments:
        specs {dict} -- current specs
    """
    fitness = 0
    for topic, value in spec.items():
        for name in value:
            if len(value) >= t_min and len(value) <= t_max:
                fitness += topic_num + 1 - pref_table[topic][name]
    return fitness

def move(specs, name, topic):
    """Moves name to topic
    
    Arguments:
        specs {dict} -- current specs dictionary
        name {str} -- name to move
        topic {str} -- a topic to move name to
    """
    for i in specs.values():
        if name in i:
            i.remove(name)
            specs[topic].append(name)
    return specs

def initial_spec(pref):
    """Creates initial spec list
    
    Arguments:
        pref {DataFrame} -- DF of preferences
    """
    global spec
    for name, topic in pref.iterrows():
        for i in topic.iteritems():
            if i[1] == 1:
                spec[i[0]].append(name)
    return spec

spec = initial_spec(pref_table)

def make_smol_ok(spec, topic):
    """Improve topics with not enough people
    
    Arguments:
        spec {dict} -- current spec
        topic {string} -- target topic
    """
    already_there = False
    new_spec = copy.deepcopy(spec)
    dict_of_pref = pref_table.to_dict()
    target_dict = dict_of_pref[topic]
    best = topic_num + 1
    sec_best = topic_num + 1
    person_to_move = ''
    for name, prio in target_dict.items():
        if prio < best and name not in spec[topic]:            
            for i in spec.values():
                if name in i and len(i) - 1 >= t_min:
                    best = prio
                    person_to_move = name
    new_spec = move(spec, person_to_move, topic)

    return new_spec

def how_bad(spec):
    """Number of smol topics
    
    Arguments:
        spec {dict} -- current spec
    """
    num = 0
    for topic, value in spec.items():
        if len(value) < t_min:
            num += 1
    return num

def improvement_move(spec, priority):
    """Moves people from topics with too many people to topics with not enough people
    
    Arguments:
        spec {dict} -- current spec dict
        priority {int} -- current priority level
    
    Returns:
        new_spec {dict} -- spec after improvement
    """
    not_enough = []
    too_many = []
    new_spec = copy.deepcopy(spec)
    all_good = True
    good_topic = ''
    for topic, value in spec.items():
        if not value:
            not_enough.append(topic)
            all_good = False
    for topic, value in spec.items():
        if len(value) > t_max:
            too_many.append(topic)
            all_good = False
        for thetopic in too_many:
            if len(spec[thetopic]) <= t_max:
                too_many.remove(thetopic)
                break
            for name in spec[thetopic]:
                for atopic in topics:
                    if len(spec[atopic]) >= t_min and atopic in not_enough and not too_many:
                        not_enough.remove(atopic)
                    if pref_table.loc[name][atopic] == priority:
                        good_topic = atopic
                if good_topic in not_enough:
                    new_spec = move(spec, name, good_topic)
                    break
    if not all_good and fitness(new_spec) > fitness(spec):
        return new_spec
    else:
        return spec

print(1, spec, fitness(spec))

if topic_num > 2:
    for priority in range(2, topic_num + 1):
        spec = improvement_move(spec, priority)
        print('Priority LVL:', priority, '\nAllocation:', spec, '\nFitness:', fitness(spec), '\n')


if len(names) >= t_min * topic_num:
    print('Fixing small topics if possible\n')
    prev_how_bad = how_bad(spec)
    while how_bad(spec) != 0:
        for topic, value in spec.items():
            if len(value) < t_min:
                prev_how_bad = how_bad(spec)
                spec = make_smol_ok(spec, topic)
        if prev_how_bad == how_bad(spec):
                break

print('Optimal allocation:', spec, '\nFitness:', fitness(spec))
