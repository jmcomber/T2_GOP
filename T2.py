from gurobipy import *


# INICIO DATOS

demandas = """23756	26009	21481	25723	22079	21337	26072	23545	29733	28493	22698	23380	27039	20511	21907	21817	28811	23976	23867	22041	22409	27790	21098	20529	33000	26956	26608	32776	31021	32609	30495	34675	31655	26377	30241	27398	25345	29365	33615	25230	29036	30616	31016	25777	31940	26644	30267	29317																							
14150	14411	12816	11115	14030	11490	10645	11745	12380	10718	13355	11358	11934	13745	14522	13251	11405	12785	13184	13585	12099	11488	13745	14285	16800	13900	16206	14837	17996	13780	14657	12358	17593	16350	16558	10117	15463	15676	15633	13692	16563	10782	11484	15657	16503	13920	13376	17806""".split("\t")


d_A = "23756	26009	21481	25723	22079	21337	26072	23545	29733	28493	22698	23380	27039	20511	21907	21817	28811	23976	23867	22041	22409	27790	21098	20529".split("\t")
																							
d_B = "33000	26956	26608	32776	31021	32609	30495	34675	31655	26377	30241	27398	25345	29365	33615	25230	29036	30616	31016	25777	31940	26644	30267	29317".split("\t")

d_C = "14150	14411	12816	11115	14030	11490	10645	11745	12380	10718	13355	11358	11934	13745	14522	13251	11405	12785	13184	13585	12099	11488	13745	14285".split("\t")

d_D = "16800	13900	16206	14837	17996	13780	14657	12358	17593	16350	16558	10117	15463	15676	15633	13692	16563	10782	11484	15657	16503	13920	13376	17806".split("\t")

LINES = [1, 2]

DAYS = [i for i in range(24 * 7, 48 * 7)]

# WEEKS = ["S" + str(i) for i in range(24, 48)]
WEEKS = [i for i in range(24, 48)]
D_semanal = {"A": {}, "B": {}, "C": {}, "D": {}}

for i in range(len(WEEKS)):
	D_semanal["A"][WEEKS[i]] = int(d_A[i])
	D_semanal["B"][WEEKS[i]] = int(d_B[i])
	D_semanal["C"][WEEKS[i]] = int(d_C[i])
	D_semanal["D"][WEEKS[i]] = int(d_D[i])


# PRODUCTOS Y SUBPRODUCTOS
PRODS = ["A", "B", "C", "D"]
SUBS = ["L", "M", "N", "O"]
CV_p = {"A": 5.2, "B": 5.5, "C": 4.2, "D": 3.2}
CV_s = {"L": 1.8, "M": 0.8, "N": 0.8, "O": 1.95}
K_s = {("L", 1): 3153, ("L", 2): 2786, ("M", 1): 3423, ("M", 2): 2867, ("N", 1): 3416, ("N", 2): 2951, ("O", 1): 3284, ("O", 2): 2808}
LT_s = {("L", 1): 4, ("L", 2): 4, ("M", 1): 5, ("M", 2): 3, ("N", 1): 2, ("N", 2): 2, ("O", 1): 3, ("O", 2): 5}
K_p = {("A", 1): 2102, ("A", 2): 2143, ("B", 1): 2282, ("B", 2): 2205, ("C", 1): 2277, ("C", 2): 2270, ("D", 1): 2189, ("D", 2): 2160}
LT_p = {("A", 1): 2, ("A", 2): 1, ("B", 1): 4, ("B", 2): 3, ("C", 1): 3, ("C", 2): 3, ("D", 1): 1, ("D", 2): 2}
CF_p = {"A": 3000, "B": 3500, "C": 2500, "D": 4000}
K3_p = {"A": 2123, "B": 2244, "C": 2274, "D": 2175}
LT3_p = {"A": 4, "B": 8, "C": 6, "D": 2}
CV3_p = {"A": 3000, "B": 3500, "C": 2500, "D": 4000} 

# MATERIAS PRIMAS
MP = [i for i in range(5)]
CV_mp = [0.2, 0.3, 0.3, 0.15, 0.5]
I0_mp = [47892, 69951, 48527, 61415, 40826]
KE_mp = [45000, 60000, 55000, 35000, 45000]
KB_mp = [60000, 60000, 50000, 45000, 45000]
LT_mp = [10, 6, 10, 2, 9]
CF_mp = [3816, 4271, 5571, 2625, 9358]
C_NH_mp = [0.4, 0.6, 0.6, 0.3, 1]  #Costos no habitual
CB_mp = [0.0006, 0.0008, 0.0008, 0.0004, 0.0014]
CB3_mp = [0.0007, 0.0011, 0.0011, 0.0005, 0.0018] #Costos indiv. MP en bodega tercerizada


#ALPHA ES CUÁNTOS DE CADA SUBPROD. PARA PRODUCIR PROD.
ALPHA = {"A": {"L": 2, "M": 1, "N": 1, "O": 0}, "B": {"L": 0, "M": 1, "N": 1, "O": 2}, "C": {"L": 1, "M": 2, "N": 1, "O": 0}, "D": {"L": 0, "M": 2, "N": 2, "O": 0}}

#BETA ES CUÁNTAS DE CADA MATERIA PRIMA PARA PRODUCIR SUBPROD.
BETA = {"L": [1, 1, 1, 1, 0], "M": [1, 1, 1, 0, 0], "N": [1, 1, 0, 2, 0], "O": [0, 2, 4, 1, 0]}

CVB_s = {s: sum(BETA[s][i] * CB_mp[i] for i in range(len(CB_mp))) for s in SUBS}


#COSTO TOTAL DE BODEGA POR CADA PRODUCTO
ALPHA_BETA = {p: sum(ALPHA[p][s] * CB_mp[i] * BETA[s][i] for i in MP for s in SUBS) for p in PRODS}


# FIN DATOS

model = Model("Producción")

# VARS

x = model.addVars(DAYS, LINES, PRODS, vtype=GRB.INTEGER, lb=0, name="prod_p")

y = model.addVars(DAYS, LINES, SUBS, vtype=GRB.INTEGER, lb=0, name="prod_s")

z_p = model.addVars(DAYS, LINES, PRODS, vtype=GRB.BINARY, name="bin_prod_p")

z_s = model.addVars(DAYS, LINES, SUBS, vtype=GRB.BINARY, name="bin_prod_s")

w = model.addVars(DAYS, PRODS, vtype=GRB.INTEGER, lb=0, name="prod_p_3izada")

I = model.addVars(DAYS, MP, vtype=GRB.INTEGER, lb=0, name="Inv_MP")

I3 = model.addVars(DAYS, MP, vtype=GRB.INTEGER, lb=0, name="Inv_MP_3izado")

N = model.addVars(DAYS, SUBS, vtype=GRB.INTEGER, lb=0, name="Inv_SUBS")

LAMBDA = model.addVars(DAYS, PRODS, vtype=GRB.INTEGER, lb=0, name="Inv_P")

D = model.addVars(DAYS, PRODS, vtype=GRB.INTEGER, lb=0, name="Demanda_dia")

PEDIDO = model.addVars(DAYS, MP, vtype=GRB.INTEGER, lb=0, name="pedido_MP")

SALIDA_MP = model.addVars(DAYS, MP, vtype=GRB.INTEGER, lb=0, name="salidas_MP")


# RESTRICCCIONES

model.addConstrs((quicksum(D[7 * w + t, p] for t in range(7)) == D_semanal[p][w] for w in WEEKS for p in PRODS), name="demandas diarias de la semana son la semanal")

model.addConstrs((x[t, k, p] >= 2000 * z_p[t, k, p] for t in DAYS for k in LINES for p in PRODS), name="lote mínimo")

model.addConstrs((x[t, k, p] <= 2000000 * z_p[t, k, p] for t in DAYS for k in LINES for p in PRODS), name="relación variables")

model.addConstrs((quicksum(ALPHA[p][s] * x[t, k, p] for p in PRODS) == y[t, k, s] for t in DAYS for k in LINES for s in SUBS), name="salida SE = entrada PT")

model.addConstrs((SALIDA_MP[t, mp] == I[t, mp] - I[t-1, mp] + I3[t, mp] - I3[t-1, mp] + PEDIDO[t, mp] for t in range(24*7 + 1, 48*7) for mp in MP), name="entrada MP")

model.addConstrs((SALIDA_MP[t, mp] == quicksum(BETA[s][mp] * y[t, k, s] for k in LINES for s in SUBS) for t in DAYS for mp in MP), name="salida MP == entrada SE")

model.addConstrs((y[t, k, s] <= K_s[s, k] * z_s[t, k, s] for t in DAYS for k in LINES for s in SUBS), name="límite capacidad línea subprods")

model.addConstrs((LAMBDA[t+1, p] ==  LAMBDA[t, p] + quicksum(x[t, k, p] for k in LINES) - D[t, p] for p in PRODS for t in range(24 * 7, 48 * 7 - 1)), name="salida PT")

model.addConstrs((quicksum(z_s[t, k, s] for s in SUBS) <= 1 for t in DAYS for k in LINES), name="solo un subprod en cada línea")


# ESTA RESTRICCIÓN ESTÁ MAL!
#  z_s[t, k, s] == 1 -> z_s[t + x, k, s] == 0 forall x in [t+1, t+LT_s[s, k]]
# model.addConstrs((z_s[t + r, k, s] <= 1 - z_s[t, k, s] for r in range(LT_s[s, k]) for t in range(24 * 7, 48 * 7 - LT_s[s, k]) for k in LINES for s in SUBS), name="Respetar lead times: si produzco en t, no puedo producir lo mismo en los siguientes dias? es realmennte eso???")

model.addConstrs((I[t, mp] <= KB_mp[mp] for t in DAYS for mp in MP), name="capacidad bodega")

model.addConstrs((I[24*7, mp] + I3[24*7, mp] == I0_mp[mp] for mp in MP), name="stocks iniciales MP")

model.addConstrs(((I[t+1, mp] - I[t, mp]) + (I3[t+1, mp] - I3[t, mp]) <= KE_mp[mp] for mp in MP for t in range(24 * 7, 48 * 7 - 1)), name="capacidad entrega MP")

# model.addConstrs((), name="")

# model.addConstrs((), name="")





obj = quicksum(CV_p[p] * x[t, k, p] for t in DAYS for k in LINES for p in PRODS) + quicksum(CV3_p[p] * w[t, p] for t in DAYS for p in PRODS) + \
quicksum(CB_mp[m] * I[t, m] for t in DAYS for m in MP) + quicksum(CF_p[p] * z_p[t, k, p] for t in DAYS for k in LINES for p in PRODS) + \
quicksum(CB3_mp[m] * I3[t, m] for t in DAYS for m in MP) + quicksum(ALPHA_BETA[p] * LAMBDA[t, p] for t in DAYS for p in PRODS) + \
quicksum(CVB_s[s] * N[t, s] for t in DAYS for s in SUBS)


model.setObjective(obj, GRB.MINIMIZE)

model.optimize()

# for v in model.getVars():
# 	if v.X != 0:
# 		print("{} {}".format(v.Varname, v.X))


