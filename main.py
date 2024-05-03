from Solver.solverSCP import solverSCP
from Solver.solverSCP_ChaoticMaps import solverSCP_ChaoticMaps

from BD.sqlite import BD
import json
# problems = ['ionosphere.data']
bd = BD()

data = bd.obtenerExperimento()

id              = 0
experimento     = ''
instancia       = ''
problema        = ''
mh              = ''
parametrosMH    = ''
maxIter         = 0
pop             = 0
ds              = []
clasificador    = ''
parametrosC     = '' 

pruebas = 1
while len(data) > 0: 
# while pruebas == 1:
    print("-------------------------------------------------------------------------------------------------------")
    print(data)
    
    id = int(data[0][0])
    id_instancia = int(data[0][9])
    datosInstancia = bd.obtenerInstancia(id_instancia)
    print(datosInstancia)
    
    problema = datosInstancia[0][1]
    instancia = datosInstancia[0][2]
    parametrosInstancia = datosInstancia[0][4]
    experimento = data[0][1]
    mh = data[0][2]
    parametrosMH = data[0][3]
    ml = data[0][4]

    
    maxIter = int(parametrosMH.split(",")[0].split(":")[1])
    pop = int(parametrosMH.split(",")[1].split(":")[1])
    ds = []
    
    if problema == 'SCP':
        bd.actualizarExperimento(id, 'ejecutando')
        print("-------------------------------------------------------------------------------------------------------")
        print(f"Ejecutando el experimento: {experimento} - id: {str(id)}")
        print("-------------------------------------------------------------------------------------------------------")
        repair = parametrosMH.split(",")[3].split(":")[1]
        ds.append(parametrosMH.split(",")[2].split(":")[1].split("-")[0])
        ds.append(parametrosMH.split(",")[2].split(":")[1].split("-")[1])
        
        parMH = parametrosMH.split(",")[4]
        
        separacion = ds[1].split("_")
        
        if len(separacion) > 1:
            solverSCP_ChaoticMaps(id, mh, maxIter, pop, instancia, ds, repair, parMH)
        else:
            solverSCP(id, mh, maxIter, pop, instancia, ds, repair, parMH)
        
    data = bd.obtenerExperimento()
    
    print(data)
    
    
    pruebas += 1
    
print("-------------------------------------------------------")
print("-------------------------------------------------------")
print("Se han ejecutado todos los experimentos pendientes.")
print("-------------------------------------------------------")
print("-------------------------------------------------------")