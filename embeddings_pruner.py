from constants import WORD_VECTORS_N, DRY_RUN

remove_old = True # this is the only way atm
if DRY_RUN:
    vectors_to_leave = 5000
else:
    vectors_to_leave = WORD_VECTORS_N

def prune(filename):
    file = open(filename, "r", encoding = "utf-8")
    header = file.readline()
    dim = header.split(" ")[1].strip()

    vex = []
    vex.append(" ".join([str(vectors_to_leave), dim]))
    counter = 0

    while counter < vectors_to_leave:
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
