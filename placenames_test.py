import time

with open("placenames.txt") as f:
    names = set(l[:-1] for l in f)

start = time.clock()
test = False
for text in ["a near-level shallow, natural depression or basin, usually containing an intermittent lake, pond, or pool", "a break in a mountain range or other high obstruction, used for transportation from one side to the other [See also gap]", "an elongate area of land projecting into a body of water and nearly surrounded by water", "a pointed elevation atop a mountain, ridge, or other hypsographic feature", "pointed elevations atop a mountain, ridge, or other hypsographic features", "an elevated plain with steep slopes on one or more sides, and often with incised streams", "an area reclaimed from the sea by diking and draining", "an extensive area of comparatively level to gently undulating land, lacking surface irregularities, and usually adjacent to a higher area", "a bluff or prominent hill overlooking or projecting into a lowland"]:
    test = any(n in text for n in names)
print time.clock() - start
