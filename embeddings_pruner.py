size = 300000
remove_old = True # this is the only way atm

def prune(filename):
    file = open(filename, "r", encoding = "utf-8")
    header = file.readline()
    dim = header.split(" ")[1].strip()

    vex = []
    vex.append(" ".join([str(size), dim]))
    counter = 0

    while counter < size:
        line = file.readline()
        line = line.strip()
        vex.append(line)
        counter += 1
    file.close()
    if remove_old:
        file = open(filename, "w", encoding = "utf-8")
        newvex = "\n".join(vex)
        if vex[-1] == "":
            newvex += "\n"
        del vex
        file.write(newvex)
        file.close()
