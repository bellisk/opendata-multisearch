places = set()

with open("allCountries.txt") as f:
    for l in f:
        if l.split("\t")[6] in ["A", "P"]:#, "T", "V"]: No mountains or forests
            for n in l.split("\t")[3].split(","):# Don't just use 1st name
            #n = l.split("\t")[1]
                if len(n) > 0 and not n in places:
                    places.add(n)
                    print n
