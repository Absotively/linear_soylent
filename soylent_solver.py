import fileinput
import json
from lpsolve55 import *
import sys
import StringIO

s = ''
for line in fileinput.input():
  s += line

recipe = json.loads(s, 'iso-8859-15')

lp = lpsolve('make_lp',0,len(recipe["ingredients"]))

lpsolve('set_presolve', lp, 0, 0)

cost = []

for ing in recipe["ingredients"]:
	if ing["container_size"]:
		cost.append(float(ing["item_cost"])/ing["container_size"])
	else:
		cost.append(0)

lpsolve('set_obj_fn', lp, cost)

nutrient_formulae = {}

target_list = []

for name, value in recipe["nutrientTargets"].iteritems():
	if name == "calories_max" and value == 0:
		value = recipe["nutrientTargets"]["calories"]
		recipe["nutrientTargets"]["calories_max"] = value

	if value == 0 or name == "name":
		continue

	target_list.append(name)

	nutrient = name
	dir = GE
	if name.endswith("_max"):
		nutrient = name[0:-4]
		dir = LE

	if nutrient not in nutrient_formulae:
		formula = []
		for ing in recipe["ingredients"]:
			ing["name"] = ing["name"].encode('ascii','backslashreplace')
			if ing["serving"] == 0:
				print("\nWARNING: Serving size not set, assuming 1 for {0}".format(ing["name"]))
				ing["serving"] = 1
			formula.append(float(ing[nutrient])/ing["serving"])
		nutrient_formulae[nutrient] = formula

	lpsolve('add_constraint', lp, nutrient_formulae[nutrient], dir, value)

real_stdout = sys.stdout
sys.stdout = StringIO.StringIO()

result = lpsolve('solve', lp)

ingredient_count = len(recipe["ingredients"])

for i in range(ingredient_count):
	lpsolve('set_col_name', lp, i+1, recipe["ingredients"][i]["name"][0:9])
for i in range(len(target_list)):
	lpsolve('set_row_name', lp, i+1, target_list[i])

if (result == INFEASIBLE):
	column_temp = [0.0 for x in range(len(target_list)+1)]
	blank_obj = [0.0 for x in range(ingredient_count)]
	print blank_obj
	lpsolve('set_obj_fn', lp, blank_obj)
	for i in range(len(target_list)):
		column_temp[0] = 1.0/recipe["nutrientTargets"][target_list[i]]
		column_temp[i+1] = 1
		if target_list[i].endswith("_max"):
			column_temp[i+1] = -1
		lpsolve('add_column', lp, column_temp)
		column_temp[i+1] = 0
	lpsolve('solve', lp)

sys.stdout = real_stdout

lpsolve('write_lp', lp, 'test_data.lp')

amounts = lpsolve('get_variables', lp)[0]
nutrient_amounts = lpsolve('get_constraints', lp)[0]

print("\ncost\tamount\tingredient\n")
cost_total = 0
for i in range(ingredient_count):
	if recipe["ingredients"][i]["container_size"]:
		ing_cost = round(amounts[i]*recipe["ingredients"][i]["item_cost"]/recipe["ingredients"][i]["container_size"],2)
		print("{0}\t{1}\t{2}".format(ing_cost,round(amounts[i],3),recipe["ingredients"][i]["name"]))
		cost_total += ing_cost
	else:
		print("\t{0}\t{1}".format(round(amounts[i],3),recipe["ingredients"][i]["name"]))
print("\nTOTAL DAILY COST: {0}".format(round(cost_total,2)) )

problems = {}
deviation = 0
if len(amounts) > ingredient_count:
	for i in range(len(amounts) - ingredient_count):
		if amounts[i + ingredient_count]:
			if target_list[i].endswith("_max"):
				problems[target_list[i][0:-4]] = "OVER"
				nutrient_amounts[i] -= amounts[i + ingredient_count]
			else:
				problems[target_list[i]] = "UNDER"
				nutrient_amounts[i] -= amounts[i + ingredient_count]
			deviation += 100.0 * amounts[i + ingredient_count] / recipe["nutrientTargets"][target_list[i]]

if deviation:
	print("\n\namount\tnutrient\tstatus\n")
else:
	print("\n\namount\tnutrient\n")
printed = []
for i in range(len(target_list)):
	name = target_list[i]
	if name.endswith("_max"):
		name = name[0:-4]
	if name in printed:
		continue
	if name in problems:
		print("{0}\t{1}\t\t{2}".format(round(nutrient_amounts[i],3), name, problems[name]))
	else:
		print("{0}\t{1}".format(round(nutrient_amounts[i],3), name))
	printed.append(name)

if deviation:
	print("\nDEVIATION: {0}".format(round(deviation,2)))
