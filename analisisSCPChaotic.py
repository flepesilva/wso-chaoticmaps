import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import os
import seaborn as sns
from scipy.stats import mannwhitneyu
from util import util
from BD.sqlite import BD
bd = BD()
tablas = True
graficos = True
diversidad = True
testEstadistico = True
dirResultado = './Resultados/'

instancias = bd.obtenerInstanciasEjecutadas('SCP')
mhs = bd.obtenerTecnicas()

if tablas:

    archivoResumenFitness = open(f'{dirResultado}resumen_fitness_SCP.csv', 'w')

    archivoResumenFitness.write(',')

    for instancia in instancias:
        archivoResumenFitness.write(f' ,{instancia[0]}, ,')

    archivoResumenFitness.write(' \n')

    archivoResumenFitness.write('experiment ')

    for instancia in instancias:
        archivoResumenFitness.write(f',best, avg. , RPD')

    archivoResumenFitness.write(' \n')

    for mh in mhs:
        
        experimentos = bd.obtenerExperimentos('SCP', mh[0])
        
        for experimento in experimentos:
            
            archivoResumenFitness.write(f'{experimento[0]}')
            
            for instancia in instancias:
                ejecuciones = bd.obtenerEjecuciones(instancia[0], mh[0], experimento[0])
                
                tiempos         = []
                rendimiento     = []
                exploracion     = []
                explotacion     = []
                optimo          = bd.obtenerOptimoInstancia(instancia[0])
                optimo = float(optimo[0][0])
                
                print(f'Analizando experimento {experimento[0]} asociado a la instancia {instancia[0]} metaheuristica {mh[0]} -- optimo: {optimo}')
                
                for ejecucion in ejecuciones:
                    id                  = ejecucion[0]
                    nombre_archivo      = ejecucion[2]
                    archivo             = ejecucion[3]
                    tiempo_ejecucion    = ejecucion[5]
                    
                    direccionDestiono = './Resultados/Transitorio/'+nombre_archivo+'.csv'
                    # print("-------------------------------------------------------------------------------")
                    util.writeTofile(archivo,direccionDestiono)
                    
                    data = pd.read_csv(direccionDestiono, on_bad_lines='skip')
                    
                    iteraciones = data['iter']
                    fitness     = data['fitness']
                    time        = data['time']
                    xpl         = data['XPL']
                    xpt         = data['XPT']
                    
                    ultimo = len(iteraciones) - 1
                    
                    rendimiento.append(fitness[ultimo])
                    exploracion.append(np.round(np.mean(xpl), decimals=2))
                    explotacion.append(np.round(np.mean(xpt), decimals=2))
                    tiempos.append(tiempo_ejecucion)
                
                    if diversidad:
                        
                        if not os.path.exists(f'{dirResultado}/Graficos/SCP/{experimento[0]}/{instancia[0]}'):
                            os.makedirs(f'{dirResultado}/Graficos/SCP/{experimento[0]}/{instancia[0]}')
                        
                        figPER, axPER = plt.subplots()
                        axPER.plot(iteraciones, xpl, color="r", label=r"$\overline{XPL}$"+": "+str(np.round(np.mean(xpl), decimals=2))+"%")
                        axPER.plot(iteraciones, xpt, color="b", label=r"$\overline{XPT}$"+": "+str(np.round(np.mean(xpt), decimals=2))+"%")
                        axPER.set_title(f'XPL% - XPT% {mh[0]} {experimento[0].split("-")[1]} {instancia[0]}')
                        axPER.set_ylabel("Percentage")
                        axPER.set_xlabel("Iteration")
                        axPER.legend(loc = 'upper right')
                        plt.savefig(f'{dirResultado}/Graficos/SCP/{experimento[0]}/{instancia[0]}/Percentage_{instancia[0]}_{experimento[0]}_{id}.pdf')
                        plt.close('all')
                        print(f'Grafico de exploracion y explotacion realizado para {experimento[0]}, id: {id}, instancia: {instancia[0]}')
                    
                    os.remove('./Resultados/Transitorio/'+nombre_archivo+'.csv')
                
                rpd = np.round( ( (100 * ( np.min(rendimiento) - optimo ) ) / optimo), 3 )
                
                archivoResumenFitness.write(f',{np.min(rendimiento)},{np.round(np.average(rendimiento),3)},{rpd}')

            archivoResumenFitness.write(' \n')

    archivoResumenFitness.close()
    
if graficos:
    iteraciones     = []
    rendimientos    = dict()
    
    if not os.path.exists(f'{dirResultado}/Best/SCP'):
        os.makedirs(f'{dirResultado}/Best/SCP')    
    for mh in mhs:
        print('asdsadasdasd')
        experimentos = bd.obtenerExperimentosEspecial('SCP', mh[0], 'STD')
        for instancia in instancias:
            figSTD, axSTD = plt.subplots()
            noGraficar = False
            for experimento in experimentos:
                mejor = bd.obtenerMejoresEjecucionesSCP(instancia[0], mh[0], experimento[0])
                print(f'Analizando experimento {experimento[0]} asociado a la instancia {instancia[0]} metaheuristica {mh[0]}')
                for m in mejor:
                    id                  = m[0]
                    nombre_archivo      = m[2]
                    archivo             = m[3]
                    direccionDestiono = './Resultados/Transitorio/'+nombre_archivo+'.csv'
                    # print("-------------------------------------------------------------------------------")
                    util.writeTofile(archivo,direccionDestiono)                        
                    data = pd.read_csv(direccionDestiono, on_bad_lines='skip')
                    print(len(data['iter']))
                    if len(data['iter']) == 501:
                        iteraciones = data['iter']
                    fitness     = data['fitness']
                    rendimientos[f'{experimento[0]} - {instancia[0]}'] = fitness
                        
                    os.remove('./Resultados/Transitorio/'+nombre_archivo+'.csv')
            for clave in rendimientos:
                etiqueta = f'{clave.split("-")[1]}'
                if mh[0] in clave and instancia[0] in clave and 'STD' in clave:        
                    if len(rendimientos[clave]) == 501:
                        axSTD.plot(iteraciones, rendimientos[clave], label=etiqueta)
                    else: 
                        noGraficar = True
            if not noGraficar:
                axSTD.set_title(f'Coverage {instancia[0]} - {mh[0]} - STD')
                axSTD.set_ylabel("Fitness")
                axSTD.set_xlabel("Iteration")
                axSTD.legend(loc = 'upper right')
                plt.savefig(f'{dirResultado}/Best/SCP/fitness_{instancia[0]}_{mh[0]}_STD.pdf')
                plt.close('all')
                print(f'Grafico de fitness realizado {instancia[0]} - {mh[0]} - STD')     
                
                
    for mh in mhs:
        experimentos = bd.obtenerExperimentosEspecial('SCP', mh[0], 'COM')
        for instancia in instancias:
            figSTD, axSTD = plt.subplots()
            noGraficar = False
            for experimento in experimentos:
                mejor = bd.obtenerMejoresEjecucionesSCP(instancia[0], mh[0], experimento[0])
                print(f'Analizando experimento {experimento[0]} asociado a la instancia {instancia[0]} metaheuristica {mh[0]}')
                for m in mejor:
                    id                  = m[0]
                    nombre_archivo      = m[2]
                    archivo             = m[3]
                    direccionDestiono = './Resultados/Transitorio/'+nombre_archivo+'.csv'
                    # print("-------------------------------------------------------------------------------")
                    util.writeTofile(archivo,direccionDestiono)                        
                    data = pd.read_csv(direccionDestiono, on_bad_lines='skip')
                    if len(data['iter']) == 501:
                        iteraciones = data['iter']
                    fitness     = data['fitness']
                    rendimientos[f'{experimento[0]} - {instancia[0]}'] = fitness
                    
                    os.remove('./Resultados/Transitorio/'+nombre_archivo+'.csv')
            for clave in rendimientos:
                etiqueta = f'{clave.split("-")[1]}'
                if mh[0] in clave and instancia[0] in clave and 'COM' in clave:        
                    if len(rendimientos[clave]) == 501:
                        axSTD.plot(iteraciones, rendimientos[clave], label=etiqueta)
                    else: 
                        noGraficar = True
            if not noGraficar:
                axSTD.set_title(f'Coverage {instancia[0]} - {mh[0]} - COM')
                axSTD.set_ylabel("Fitness")
                axSTD.set_xlabel("Iteration")
                axSTD.legend(loc = 'upper right')
                plt.savefig(f'{dirResultado}/Best/SCP/fitness_{instancia[0]}_{mh[0]}_COM.pdf')
                plt.close('all')
                print(f'Grafico de fitness realizado {instancia[0]} - {mh[0]} - COM') 
                
    for mh in mhs:
        experimentos = bd.obtenerExperimentosEspecial('SCP', mh[0], 'ELIT')
        for instancia in instancias:
            figSTD, axSTD = plt.subplots()
            noGraficar = False
            for experimento in experimentos:
                mejor = bd.obtenerMejoresEjecucionesSCP(instancia[0], mh[0], experimento[0])
                print(f'Analizando experimento {experimento[0]} asociado a la instancia {instancia[0]} metaheuristica {mh[0]}')
                for m in mejor:
                    id                  = m[0]
                    nombre_archivo      = m[2]
                    archivo             = m[3]
                    direccionDestiono = './Resultados/Transitorio/'+nombre_archivo+'.csv'
                    # print("-------------------------------------------------------------------------------")
                    util.writeTofile(archivo,direccionDestiono)                        
                    data = pd.read_csv(direccionDestiono, on_bad_lines='skip')
                    if len(data['iter']) == 501:
                        iteraciones = data['iter']
                    fitness     = data['fitness']
                    rendimientos[f'{experimento[0]} - {instancia[0]}'] = fitness
                    
                    os.remove('./Resultados/Transitorio/'+nombre_archivo+'.csv')
            for clave in rendimientos:
                etiqueta = f'{clave.split("-")[1]}'
                if mh[0] in clave and instancia[0] in clave and 'ELIT' in clave:        
                    if len(rendimientos[clave]) == 501:
                        axSTD.plot(iteraciones, rendimientos[clave], label=etiqueta)
                    else: 
                        noGraficar = True
            if not noGraficar:
                axSTD.set_title(f'Coverage {instancia[0]} - {mh[0]} - ELIT')
                axSTD.set_ylabel("Fitness")
                axSTD.set_xlabel("Iteration")
                axSTD.legend(loc = 'upper right')
                plt.savefig(f'{dirResultado}/Best/SCP/fitness_{instancia[0]}_{mh[0]}_ELIT.pdf')
                plt.close('all')
                print(f'Grafico de fitness realizado {instancia[0]} - {mh[0]} - ELIT') 
    
    
if testEstadistico:
    for instancia in instancias:
        for mh in mhs:
            if not os.path.exists(f'{dirResultado}/Test_Estadistico/SCP/{mh[0]}/instancias'):
                os.makedirs(f'{dirResultado}/Test_Estadistico/SCP/{mh[0]}/instancias')
            archivoTransitorio = open(f'{dirResultado}/Test_Estadistico/SCP/{mh[0]}/instancias/{instancia[0]}.csv', 'w')
            archivoTransitorio.write('MH,FITNESS\n')
            experimentos = bd.obtenerExperimentos('SCP', mh[0])
            for experimento in experimentos:
                
                ejecuciones = bd.obtenerEjecuciones(instancia[0], mh[0], experimento[0])
                rendimiento     = []
                
                print(f'Analizando experimento {experimento[0]} asociado a la instancia {instancia[0]} metaheuristica {mh[0]}')
                
                for ejecucion in ejecuciones:
                    id                  = ejecucion[0]
                    nombre_archivo      = ejecucion[2]
                    archivo             = ejecucion[3]
                    tiempo_ejecucion    = ejecucion[5]
                    
                    direccionDestiono = './Resultados/Transitorio/'+nombre_archivo+'.csv'
                    # print("-------------------------------------------------------------------------------")
                    util.writeTofile(archivo,direccionDestiono)
                    
                    data = pd.read_csv(direccionDestiono, on_bad_lines='skip')
                    
                    iteraciones = data['iter']
                    fitness     = data['fitness']
                    time        = data['time']
                    xpl         = data['XPL']
                    xpt         = data['XPT']
                    
                    ultimo = len(iteraciones) - 1
                    
                    rendimiento.append(fitness[ultimo])
                    archivoTransitorio.write(f'{experimento[0].split("-")[1]},{fitness[ultimo]}\n')

                    os.remove('./Resultados/Transitorio/'+nombre_archivo+'.csv')
            archivoTransitorio.close()
    
    for instancia in instancias:
        for mh in mhs:
            if not os.path.exists(f'{dirResultado}/Test_Estadistico/SCP/{mh[0]}/Test_instancias'):
                os.makedirs(f'{dirResultado}/Test_Estadistico/SCP/{mh[0]}/Test_instancias')
            test_estadistico = open(f'{dirResultado}Test_Estadistico/SCP/{mh[0]}/Test_instancias/test_estadistico_{mh[0]}_{instancia[0]}.csv', 'w')
            test_estadistico.write(f' , ')
            experimentos = bd.obtenerExperimentos('SCP', mh[0])
            i = 1
            for tecnica in experimentos:
                test_estadistico.write(f' {tecnica[0].split("-")[1]} ')
                if i < len(experimentos):
                    test_estadistico.write(f' , ')
                else:
                    test_estadistico.write(f' \n ')
                i += 1

            datos = pd.read_csv(f'{dirResultado}Test_Estadistico/SCP/{mh[0]}/instancias/{instancia[0]}.csv')
            for tecnica in experimentos:
                data_x = datos[datos['MH'].isin([tecnica[0].split("-")[1]])]
                x = data_x['FITNESS']
                test_estadistico.write(f' {tecnica[0].split("-")[1]} ')
                for t in experimentos:
                    if t[0] != tecnica[0]:
                        data_y = datos[datos['MH'].isin([t[0].split("-")[1]])]
                        y = data_y['FITNESS']
                        p_value = mannwhitneyu(x,y, alternative='less')
                        print(f'Comparando', f'{tecnica[0]}', f'contra', f'{t[0]}', f'en la instancia', f'{instancia[0]}:', f'{np.round(p_value[1],3)}',)
                        if not os.path.exists(f'{dirResultado}/Test_Estadistico/SCP/{mh[0]}/Transitorio'):
                            os.makedirs(f'{dirResultado}/Test_Estadistico/SCP/{mh[0]}/Transitorio')
                        archivo = open(f'{dirResultado}Test_Estadistico/SCP/{mh[0]}/Transitorio/{tecnica[0]}_contra_{t[0]}.csv', 'a')
                        archivo.write(f'{np.round(p_value[1],3)}\n')
                        test_estadistico.write(f' , {np.round(p_value[1],3)} ')
                    else:
                        test_estadistico.write(f' , X ')
                test_estadistico.write(f' \n ')
            test_estadistico.close()
    
    for mh in mhs:
        if not os.path.exists(f'{dirResultado}/Test_Estadistico/SCP/{mh[0]}/Test'):
            os.makedirs(f'{dirResultado}/Test_Estadistico/SCP/{mh[0]}/Test')
        test = open(f'{dirResultado}Test_Estadistico/SCP/{mh[0]}/Test/test_estadistico_{mh[0]}.csv', 'w')
        test.write(f' , ')
        experimentos = bd.obtenerExperimentos('SCP', mh[0])
        i = 1
        for tecnica in experimentos:
            test.write(f' {tecnica[0].split("-")[1]} ')
            if i < len(experimentos):
                test.write(f' , ')
            else:
                test.write(f' \n ')
            i += 1
            
        for tecnica in experimentos:
            test.write(f' {tecnica[0].split("-")[1]} ')
            print(f'Analizando experimento {tecnica[0]} mh: {mh[0]}')
            for t in experimentos:
                if t[0] != tecnica[0]:
                    archivo = pd.read_csv(f'./Resultados/Test_Estadistico/SCP/{mh[0]}/Transitorio/{tecnica[0]}_contra_{t[0]}.csv')
                    test.write(f' , {np.round(np.average(archivo.iloc[:, 0 ]),3)} ')
                    os.remove(f'./Resultados/Test_Estadistico/SCP/{mh[0]}/Transitorio/{tecnica[0]}_contra_{t[0]}.csv')
                else:
                    test.write(f' , X ')
            test.write(f' \n ')
        test.close()