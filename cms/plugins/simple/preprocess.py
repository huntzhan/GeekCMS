
def del_fragments(data_set):
    for fragment in data_set.fragments:
        try:
            if not fragment.meta['active']:
                data_set.fragments.remove(fragment)
        except:
            continue
