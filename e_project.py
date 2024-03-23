#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Mar 22 15:04:50 2024

@author: charlesdelforge
"""
from pyomo.environ import *

# Ouvrir et lire le fichier texte
with open('donnees.txt', 'r') as file:
    data = file.readlines()

# Extraire les données du fichier texte
load = []
lf_pv = []
for line in data:
    values = line.split(',')
    load.append(float(values[0]))
    lf_pv.append(float(values[1]))

# Créer un modèle d'optimisation
model = ConcreteModel()

# Définir les ensembles
N = len(load)
model.T = RangeSet(1, N)

# Définir les variables de décision
model.battery_storage = Var(model.T, within=NonNegativeReals)
model.solar_panel_capacity = Var(within=NonNegativeReals)

# Définir la fonction objectif
battery_cost_per_GWh = 1500
solar_panel_cost_per_kW = 700

model.cost = Objective(expr=sum(battery_cost_per_GWh * model.battery_storage[t] for t in model.T) +
                         solar_panel_cost_per_kW * model.solar_panel_capacity, sense=minimize)

# Définir les contraintes
def demand_constraint_rule(model, t):
    return model.battery_storage[t] + lf_pv[t-1] * model.solar_panel_capacity >= load[t-1]

model.demand_constraint = Constraint(model.T, rule=demand_constraint_rule)

# Résoudre le problème d'optimisation
solver = SolverFactory('gurobi')
solver.solve(model)

# Afficher les résultats
print("Capacité de la batterie optimale :")
for t in model.T:
    print(f"Temps {t}: {model.battery_storage[t].value} GWh")

print("\nCapacité des panneaux solaires optimale :")
print(f"{model.solar_panel_capacity.value} kW")

