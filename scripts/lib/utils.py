import re
import sys
re_id_illegal = re.compile("[^a-z^\d^A-Z]+")

re_year = re.compile("^(\d\d\d\d)[^\d]*(.*)")
re_num = re.compile("(\d{1,2})[^\d]*(.*)")

def id_create(filename, type_,id_):
    if id_ is not None:
        if ":" in id_:
            values = id_.split(":")
            type_ = values[0]
            name = "_".join(values[1:])
        elif type_ is not None:
            name = id_
        else:
            raise Exception(filename+" "+id_+" has type and type is None")
    else:
        raise Exception(filename+" id is None")

    if type_ == "presentation":
        type_ = "media"

    if type_ == "person":
        if "__" in name or "," in name:
            if "__" in name:
                names = name.split("__")
            else:
                names = name.split(",")
            for i,name in enumerate(names):
                name = re_id_illegal.sub("_",name)
                names[i] = re.sub("_+$","",re.sub("^_+","",name))
        else:
            parts = name.split("_")
            for i,part in enumerate(parts):
                parts[i] = re_id_illegal.sub("_",part)
            
            if len(parts) > 1:
                names = [parts[0],"_".join(parts[1:])]
            else:
                names = parts
        name = "__".join(names)

    else:
        name = re_id_illegal.sub("_",name)
        name = re.sub("_+$","",re.sub("^_+","",name))
    return type_.lower()+":"+name.lower()


def date_parse(value):
    m = re_year.search(value)
    if m:
        year, rest = m.groups()
        mon, day = None, None
        m = re_num.search(rest)
        if m:
            mon, rest = m.groups()
            if len(mon) < 2:
                mon = "0"+mon
            m = re_num.search(rest)
            if m:
                day, rest = m.groups()
                if len(day) < 2:
                    day = "0"+day
                return year+"."+mon+"."+day
            else:
                return year+"."+mon
        else:
            return year
    return None
