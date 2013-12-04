
def del_fragments(files, fragments):
    for fragment in fragments:
        try:
            if fragment.meta['active'] == False:
                fragments.remove(fragment)
        except:
            continue
