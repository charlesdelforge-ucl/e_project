from pyomo.environ import *
import matplotlib.pyplot as plt
import numpy as np

# Lire les données du fichier texte
load = [99,93, 88, 87, 87, 88, 109, 127, 140, 142, 142, 140, 140, 140, 137, 139, 146, 148, 148, 142, 134, 123, 108, 93]
lf_pv = [0.00E+00,
         0.00E+00,
         0.00E+00,
         0.00E+00,
         9.80E-04,
         2.47E-02,
         9.51E-02,
         1.50E-01,
         2.29E-01,
         2.98E-01,
         3.52E-01,
         4.15E-01,
         4.58E-01,
         3.73E-01,
         2.60E-01,
         2.19E-01,
         1.99E-01,
         8.80E-02,
         7.03E-02,
         3.90E-02,
         9.92E-03,
         1.39E-06,
         0.00E+00,
         0.00E+00]

# Créer un modèle d'optimisation
model = ConcreteModel()

# Définir les ensembles
N = len(load)
model.T = range(N)

# Définir les variables de décision
model.battery_storage_capacity = Var(within=NonNegativeReals)
model.battery_charge_state = Var(model.T, within=NonNegativeReals)
model.solar_panel_capacity = Var(within=NonNegativeReals)

# Définir la fonction objectif
battery_cost_per_kWh = 1500
solar_panel_cost_per_kW = 700

model.cost = Objective(expr=battery_cost_per_kWh * model.battery_storage_capacity +
                         solar_panel_cost_per_kW * model.solar_panel_capacity, sense=minimize)

# Définir les contraintes
model.constraints = ConstraintList()
model.constraints.add(model.battery_charge_state[0] == model.battery_charge_state[N-1])

for t in model.T:
    model.constraints.add(model.battery_charge_state[t] <= model.battery_storage_capacity)
    if t != 0:
        model.constraints.add(model.battery_charge_state[t] == model.battery_charge_state[t-1] +
                          lf_pv[t-1] * model.solar_panel_capacity - load[t-1])

# Résoudre le problème d'optimisation
solver = SolverFactory('gurobi')
solver.solve(model)

# Afficher les résultats
print("Capacité de stockage de la batterie optimale:", model.battery_storage_capacity.value)
print("Capacité des panneaux solaires optimale:", model.solar_panel_capacity.value)

# Trace des courbes
plt.figure(figsize=(10, 5))

# Courbe de demande et de charge
plt.plot(range(1, N+1), load, label='Demand')
plt.plot(range(1, N+1), np.array(lf_pv)*model.solar_panel_capacity.value, label='Production')
plt.fill_between(range(1, N+1), np.array(lf_pv)*model.solar_panel_capacity.value, load, where=(np.array(lf_pv)*model.solar_panel_capacity.value >= load), interpolate=True, color='blue', alpha=0.12, label='Charging energy')
plt.fill_between(range(1, N+1), np.array(lf_pv)*model.solar_panel_capacity.value, load, where=(np.array(lf_pv)*model.solar_panel_capacity.value < load), interpolate=True, color='red', alpha=0.12, label='Delivering energy')
#plt.plot(range(1, N+1), -np.array(load) + np.array(lf_pv)*model.solar_panel_capacity.value, label='Storage')
plt.xlabel('Time [h]')
plt.ylabel('Power [kW]')
plt.legend()
plt.title('Solar panel installation needed is '+str(round(model.solar_panel_capacity.value, 2))+" kW")
plt.savefig("plots_exercise/power.pdf", bbox_inches='tight')
plt.show()

# Courbe d'état de charge de la batterie
plt.figure(figsize=(10, 5))
plt.plot(range(1, N+1), [model.battery_charge_state[t].value for t in model.T], label='Charge state')
plt.xlabel('Time [h]')
plt.ylabel('Charge state [kWh]')
plt.title('Storage capacity needed is '+str(round(model.battery_storage_capacity.value, 2))+" kWh")
plt.savefig("plots_exercise/energy.pdf", bbox_inches='tight')
plt.show()
