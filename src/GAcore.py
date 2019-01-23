#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Copyright 2018 Carlos Guerrero, Isaac Lera.
Created on September 2018
@authors:
    Carlos Guerrero
    carlos ( dot ) guerrero  uib ( dot ) es
    Isaac Lera
    isaac ( dot ) lera  uib ( dot ) es
This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.
This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.
You should have received a copy of the GNU General Public License
along with this program. If not, see <http://www.gnu.org/licenses/>.


This program has been implemented for the research presented in 
the article "Evaluation and Efficiency Comparison of Evolutionary 
Algorithms for Service Placement Optimization in Fog Architectures",
submitted for evaluation in the journal "Future Generation Computer
Systems".
"""

import numpy as np
import random as random
import sys
import POPULATION as pop
import matplotlib.pyplot as plt3d
import SYSTEMMODEL as systemmodel
import copy
import CONFIG as config
import math as math


class GAcore:
    
    
    
    def __init__(self, system,populationSeed,evolutionSeed,conf_,popSize=-1):
        
        
        
        self.system = system
        #self.cnf = config.CONFIG()
        self.cnf = conf_
        
        if popSize == -1:
            self.populationSize = self.cnf.populationSize
        else:
            self.populationSize = popSize
        self.populationPt = pop.POPULATION(self.populationSize)
        self.mutationProbability = self.cnf.mutationProbability

        self.rndPOP = random.Random()
        self.rndEVOL = random.Random()
        
        self.rndPOP.seed(populationSeed)
        self.rndEVOL.seed(evolutionSeed)
        
#        self.autoAjustedWeight = True
        self.spreadWeight = 1.0/3.0
        self.makespanWeight = 1.0/3.0
        self.resourcesWeight = 1.0/3.0
#        self.spreadMax = 0
#        self.makespanMin = float('inf')
#        self.TMPspreadMax = 0
#        self.TMPmakespanMin = float('inf')
        
 #       self.system.FGCSmodel(self.rndPOP)
        
        


#******************************************************************************************
#   Solution adaptation
#******************************************************************************************


    def placeReplicasInCloud(self,chromosome):
        
        for i in iter(chromosome):
            i[self.system.cloudDeviceId]=1


#******************************************************************************************
#   END Solution adaptation
#******************************************************************************************



#******************************************************************************************
#   MUTATIONS
#******************************************************************************************


#    def replicaIncreseValue(self,child,myvalue):
#        
#        for i in iter(child):
#            if self.rndEVOL.random() > 0.5:
#                startingPoint = self.rndEVOL.randint(0,self.system.fogNumber-1)
#                indx = startingPoint
#                indx = (indx + 1) % self.system.fogNumber
#                while (i[indx]==myvalue) and (indx!=startingPoint):
#                    indx = (indx + 1) % self.system.fogNumber
#                i[indx]=myvalue
#                
#        self.placeReplicasInCloud(child)


    def replicaIncreseValue(self,child,myvalue,numChanges):

        for i in iter(child):
            if self.rndEVOL.random() > 0.5:        
                for j in range(numChanges):
                    indx=self.rndEVOL.randint(0,self.system.fogNumber-1)
                    i[indx]=myvalue

        
    def replicaGrowth(self,child):
        self.replicaIncreseValue(child,1,1)
        self.placeReplicasInCloud(child)
          
    def replicaShrink(self,child):
        self.replicaIncreseValue(child,0,1)
        self.placeReplicasInCloud(child)
           
        
    def serviceShuffle(self,child):
#        for i in range(0,self.system.serviceNumber/2):
#            self.serviceReplace(child)
        self.rndEVOL.shuffle(child)    
        self.placeReplicasInCloud(child)
        
        

    def serviceReplace(self,child):
        
        firstPoint = self.rndEVOL.randint(0,self.system.serviceNumber-1)
        secondPoint = self.rndEVOL.randint(0,self.system.serviceNumber-1)
        child[firstPoint],child[secondPoint] = child[secondPoint],child[firstPoint]
        
        
        self.placeReplicasInCloud(child)


    def sendToCloudAggresive(self,child):
        
        for i in range(len(child)):
            if self.rndEVOL.random() > 0.25:
                child[i] = [0 for j in xrange(self.system.fogNumber)]
                
        self.placeReplicasInCloud(child)
        
    def sendToCloudSoft(self,child):
        
        for i in range(len(child)):
            if self.rndEVOL.random() < 0.25:
                for j in range(len(child[i])):
                    if self.rndEVOL.random() < 0.05:
                        child[i][j]=0
                
        self.placeReplicasInCloud(child)        

    def spreadToFogAgressive(self,child):
        
        for i in range(len(child)):
            if self.rndEVOL.random() > 0.25:
                child[i] = [1 for j in xrange(self.system.fogNumber)]

        self.placeReplicasInCloud(child)

    def spreadToFogSoft(self,child):
        
        for i in range(len(child)):
            if self.rndEVOL.random() < 0.25:
                for j in range(len(child[i])):
                    if self.rndEVOL.random() < 0.05:
                        child[i][j]=1

        self.placeReplicasInCloud(child)
        

      
    
    def mutate(self,child):
        
        mutationOperators = [] 
        mutationOperators.append(self.replicaGrowth)
        mutationOperators.append(self.replicaShrink)
        mutationOperators.append(self.serviceShuffle)
        #mutationOperators.append(self.serviceReplace)
#        mutationOperators.append(self.sendToCloudAggresive)
        mutationOperators.append(self.sendToCloudSoft)
#        mutationOperators.append(self.spreadToFogAgressive)
        mutationOperators.append(self.spreadToFogSoft)
        
        mutationOperators[self.rndEVOL.randint(0,len(mutationOperators)-1)](child)

        self.placeReplicasInCloud(child)

        
        
        
        

#******************************************************************************************
#   END MUTATIONS
#******************************************************************************************


#******************************************************************************************
#   CROSSOVER
#******************************************************************************************

#population[k][i][j]
    #k num de soluciones en la poblacion    
    # i num de servicios
    #j num de devices
    
    

    def crossoverMIO(self,f1,f2,offs):

        
        c1 = list()
        c2 = list()
        
        for i in range(0,self.system.serviceNumber):
            cuttingPoint = self.rndEVOL.randint(1,self.system.fogNumber-1)
            c1.append(f1[i][:cuttingPoint] + f2[i][cuttingPoint:])
            c2.append(f2[i][:cuttingPoint] + f1[i][cuttingPoint:])

        self.placeReplicasInCloud(c1)
        self.placeReplicasInCloud(c2)

        offs.append(c1)
        offs.append(c2)

        return c1,c2


    def crossoverMIO2(self,f1,f2,offs):

        
        c1 = list()
        c2 = list()
        cuttingPoint = self.rndEVOL.randint(1,self.system.fogNumber-1)
        for i in range(0,self.system.serviceNumber):
            c1.append(f1[i][:cuttingPoint] + f2[i][cuttingPoint:])
            c2.append(f2[i][:cuttingPoint] + f1[i][cuttingPoint:])

        self.placeReplicasInCloud(c1)
        self.placeReplicasInCloud(c2)

        offs.append(c1)
        offs.append(c2)

        return c1,c2


              
        
        
    def crossover(self,f1,f2,offs=list()):
        
        return self.crossoverMIO2(f1,f2,offs)




#******************************************************************************************
#   END CROSSOVER
#******************************************************************************************


    def dominates(self,a,b):
        #checks if solution a dominates solution b, i.e. all the objectives are better in A than in B
        Adominates = True
        #### OJOOOOOO Hay un atributo en los dictionarios que no hay que tener en cuenta, el index!!!
        for key in a:
            
            noObjectivesKeys = ["index","total","wspr","wmak","wres"]
            if not (key in noObjectivesKeys):  #por ese motivo está este if.
                if b[key]<=a[key]:
                    Adominates = False
                    break
        return Adominates     

#******************************************************************************************
#   Model constraints
#******************************************************************************************

    def notEnoughResourceFogDeviceWithOUTRepair(self,chromosome,fogId):
        
        fogConsumResource = 0
        allocatedServices = list()
        for servId in range(0,self.system.serviceNumber):
            if chromosome[servId][fogId]==1:
                allocatedServices.append(servId)
                fogConsumResource = fogConsumResource + self.system.serviceResources[servId]
        if fogConsumResource > self.system.fogResources[fogId]:
            return True

        return False



    def notEnoughResourceFogDeviceWithRepair(self,chromosome,fogId):
        
        fogConsumResource = 0
        allocatedServices = list()
        for servId in range(0,self.system.serviceNumber):
            if chromosome[servId][fogId]==1:
                allocatedServices.append(servId)
                fogConsumResource = fogConsumResource + self.system.serviceResources[servId]
#        if fogConsumResource > self.system.fogResources[fogId]:
#            return True
        while fogConsumResource > self.system.fogResources[fogId]:
            removeServId = allocatedServices[self.rndEVOL.randint(0,len(allocatedServices)-1)] #cogemos el valor que hay guardado en allocatedservices, que es el id del service que tiene alojado un servicio
            chromosome[removeServId][fogId]=0
            fogConsumResource = fogConsumResource - self.system.serviceResources[removeServId]
            allocatedServices.remove(removeServId) #elimina las ocurrencias en el list que tengan valor removeServId
            if len(allocatedServices) ==0:
                return True
        return False

    
    def notEnoughResource(self,chromosome):
        
        
        
        for fogId in range(0,self.system.fogNumber):
            if self.notEnoughResourceFogDeviceWithOUTRepair(chromosome,fogId):
                return True
            #TODO si quiero normalizar las soluciones, es aquí que debería cambiar el placement para que ucmpla la constraint
        return False
                    
            


        
    def checkConstraints(self,chromosome):
             
#        if self.duplicatedReplicaInVM(pop.population[index]['block'],index):
#            print("duplicatedReplica")
#            return False
        if self.notEnoughResource(chromosome):
            #print("resourceUsages")
            return False
        return True



    



#******************************************************************************************
#   END Model constraints
#******************************************************************************************



#******************************************************************************************
#   Service spread calculation
#******************************************************************************************


    
    
    def calculateServiceSpread(self,chromosome):
        
        totalSpread = 0
        for servPlace in iter(chromosome):
            elements = list()
            for idx,val in enumerate(servPlace):
                if (val==1):
                    elements.append(idx)
            if len(elements)>1: #TODO cual es el numero minimo de replicas por servicio
                allTheValues = list()
                for i in range(0,len(elements)-1):
                    for j in range(i+1,len(elements)):
                        allTheValues.append(self.system.devDistanceMatrix[elements[i]][elements[j]])

                
                servSpread = math.sqrt(np.var(allTheValues)) / np.mean(allTheValues) # calculation of the Coefficient of variation

            else:
                #servSpread = float('inf') #TODO que valor le pongo en el caso de que solo hay un elemento, es decir solo esta en cloud?
                servSpread = 1.0
            totalSpread = totalSpread + servSpread
            
            
        return totalSpread / len(chromosome)




#******************************************************************************************
#   END Service spread calculation
#******************************************************************************************


#******************************************************************************************
#   Service makespan calculation
#******************************************************************************************


    def calculateRecursiveMakespan(self, currentService, currentDevice,chromosome):
        
        servicePlacement = chromosome[currentService] #get the placement list of the current service
        if servicePlacement[currentDevice]==1:
            netTime = 0
            cpuTime = 0 #TODO execution time of the currentService in the current device
            closestDevice = currentDevice
        else:
            deviceDistances = self.system.devDistanceMatrix[currentDevice] # get the distances of the currentDevice with the other devices
            mask = [a*b for a,b in zip(servicePlacement,deviceDistances)] #select the distances of the devices where the service is placed
            #print mask
            netTime = min(i for i in mask if i > 0) # get the min value bigger than 0
            closestDevice = mask.index(netTime)
            #SI peta aquí diciendo que min() arg is an empty sequence es que hay una solucion que no considera emplazamiento en cloud y eso debería de no estar permitido.
                    
        #print "netTime:"+str(netTime)
         # get the device with the min distance value
        
        cpuTime = 0 #TODO execution time of the currentService in the closest device
        delayTime = netTime + cpuTime
        
        consumedServices = self.system.serviceMatrix[currentService] #get the services that need to be requested from the current service
        for idx,cServ in enumerate(consumedServices):  # calculate the makespan of the services to be requested for the case of having the current service placed in the closest device
            if (cServ==1):
                #print "recursive calculating "+str(idx)+" service for "+str(closestDevice)+" ggateway"
                delayTime = delayTime + self.calculateRecursiveMakespan(idx,closestDevice,chromosome)
        
        return delayTime

 


#    def calculateServiceMakespan(self,chromosome):
#        
#        totMakeSpan = 0
#        for servId,mobPlace in enumerate(self.system.mobilePlacementMatrix):
#            for gatewayId in iter(mobPlace):
#                #print "calculating "+str(servId)+" service for "+str(gatewayId)+" ggateway"
#                totMakeSpan = totMakeSpan + self.calculateRecursiveMakespan(servId,gatewayId,chromosome)
#        
#        return totMakeSpan
# 

    def calculateServiceMakespan(self,chromosome):
        self.XAA = chromosome
        #Calculo la media para cada servicio, y luego la media de dichas medias
        
        totDistance = 0.0
        for iServ in range(0,len(self.system.serviceMatrix)):   #recorro todos los servicios
            consumedServices = list()
            for jServ in range(0,len(self.system.serviceMatrix[iServ])):  #creo una lista con todos los servicios consumidos por el servicio actual
                if self.system.serviceMatrix[iServ][jServ]==1:
                    consumedServices.append(jServ)
            allocatedDevices = list() #creo una lista con todos los dispositivos donde se encuentra allocated el servicio actual
            for kDev in range(0,len(chromosome[iServ])):
                if chromosome[iServ][kDev]==1:
                    allocatedDevices.append(kDev)
            
            if len(consumedServices)>0:
                totalServDist = 0.0
                numServDist = 0
                for idServ in consumedServices: #recorro los servicios que consume el servicio actual
                    consumedAllocation = list()
                    for kDev in range(0,len(chromosome[idServ])): # miro los allocations del consumed service actual
                        if chromosome[idServ][kDev]==1:
                            consumedAllocation.append(kDev)
                    for idFog in allocatedDevices: # para cada instancia del servicio actual, busco el que tiene más cerca y lo considero para su media
                        minDist = float('inf')
                        for idFogCon in consumedAllocation:
                            minDist = min(minDist,self.system.devDistanceMatrix[idFog][idFogCon])
                        totalServDist= totalServDist + minDist
                        numServDist = numServDist +1
                #try:
                totDistance = totDistance + (totalServDist/numServDist) #aqui se calcula la media de als distancias para un servicio con todos los servicios que consume teniendo en cuenta todos sus emplazamientos
                #    break
                #except ZeroDivisionError:
                #    self.XAA = chromosome
                #    print chromosome
                    

        #falta calcular las distancias entre sources y primeros servicios consumidos
        numSources = 0

        for servId,mobPlace in enumerate(self.system.mobilePlacementMatrix):
            allocatedDevices = list()
            totalServDist = 0.0
            numServDist = 0
            if len(mobPlace)>0:
                for kDev in range(0,len(chromosome[servId])):
                    if chromosome[servId][kDev]==1:
                        allocatedDevices.append(kDev)
                for gatewayId in iter(mobPlace):
                    minDist = float('inf')
                    for idFog in allocatedDevices:
                        minDist = min(minDist,self.system.devDistanceMatrix[idFog][gatewayId])
                    totalServDist= totalServDist + minDist
                    numServDist = numServDist + 1
                totDistance = totDistance + (totalServDist/numServDist) #aqui se calcula la media de als distancias para un servicio con todos los servicios que consume teniendo en cuenta todos sus emplazamientos
                numSources = numSources + 1

        
        return totDistance / (len(self.system.serviceMatrix) + numSources)
            
       
            
            
            
#            for jServ in range(iServ+1,len(self.system.serviceMatrix)):
#                if self.system.serviceMatrix[iServ][jServ]==1:
#                    numDistance = numDistance+1
#                    totDistance = totDistance + 
#                
#        for servId,mobPlace in enumerate(self.system.mobilePlacementMatrix):
#            for gatewayId in iter(mobPlace):
#                #print "calculating "+str(servId)+" service for "+str(gatewayId)+" ggateway"
#                totMakeSpan = totMakeSpan + self.calculateRecursiveMakespan(servId,gatewayId,chromosome)
#        
#        return totMakeSpan
       
    
   

#******************************************************************************************
#   END Service makespan calculation
#******************************************************************************************




#******************************************************************************************
#   Total resources calculation
#******************************************************************************************

    def calculateTotalResources(self,chromosome):
        
        totalSolResources = 0
        for idx,servPlace in enumerate(chromosome):
            numReplicas = np.sum(servPlace)
            #tenemos que descontar una replica pues es la que está en el cloud y este no se ha de considerar
            totalSolResources = totalSolResources + (numReplicas-1) * self.system.serviceResources[idx]

#        return totalSolResources
        return (self.system.totalResources - totalSolResources) / self.system.totalResources



#******************************************************************************************
#   END Total resources calculation
#******************************************************************************************




#******************************************************************************************
#   Objectives and fitness calculation
#******************************************************************************************


    def calculateFitnessObjectives(self, chromosome):
        chr_fitness = {}
        
        
        if self.checkConstraints(chromosome):
            chr_fitness["makespan"] = self.calculateServiceMakespan(chromosome)
            chr_fitness["spread"] = self.calculateServiceSpread(chromosome)
            chr_fitness["resources"] = self.calculateTotalResources(chromosome)
            
#            self.spreadMax = max(self.spreadMax,chr_fitness["spread"])
#            self.makespanMin = min(self.makespanMin,chr_fitness["makespan"])
            
            normalizedSpread = chr_fitness["spread"] #El coeficiente de variación ya es un valor entre 0 y 1
            normalizedMakespan = chr_fitness["makespan"] / self.system.averagePathLength
            #normalizedResources = chr_fitness["resources"] / self.system.totalResources
            normalizedResources = chr_fitness["resources"]
            chr_fitness["total"] = self.makespanWeight * normalizedMakespan + self.spreadWeight * normalizedSpread + self.resourcesWeight * normalizedResources #minimizamos makespan y maximizamos spread
            chr_fitness["wspr"] = normalizedSpread
            chr_fitness["wmak"] = normalizedMakespan
            chr_fitness["wres"] = normalizedResources
     
        else:
#            print ("not constraints")
            chr_fitness["makespan"] = float('inf')
            chr_fitness["spread"] = float('inf')
            chr_fitness["resources"] = float('inf')
            chr_fitness["total"] = float('inf')
            chr_fitness["wspr"] = float('inf')
            chr_fitness["wmak"] = float('inf')
            chr_fitness["wres"] = float('inf')
            
        return chr_fitness
    
#    def normalizeTotalFitness(self,pop):
#        for index,chr_fitness in enumerate(pop.fitness):
#            chr_fitness["total"] = chr_fitness["makespan"] - (self.makespanMin/self.spreadMax) * chr_fitness["spread"] #minimizamos makespan y maximizamos spread

    def calculatePopulationFitnessObjectives(self,pop):   
        for index,citizen in enumerate(pop.population):
            cit_fitness = self.calculateFitnessObjectives(citizen)
            cit_fitness["index"] = index
            pop.fitness[index] = cit_fitness
#        if self.autoAjustedWeight:
#            self.normalizeTotalFitness(pop)
            
        
         
    
#******************************************************************************************
#   END Objectives and fitness calculation
#******************************************************************************************

  
            



    def generatePopulation(self,popT):
        
        for individual in range(self.populationSize):
            chromosome = [[0 for j in xrange(self.system.fogNumber)] for i in xrange(self.system.serviceNumber)]
        
#            for iService in iter(chromosome):
#                iService[self.rndPOP.randint(0,len(iService)-1)] = 1
#                iService[self.rndPOP.randint(0,len(iService)-1)] = 1
#                iService[self.rndPOP.randint(0,len(iService)-1)] = 1
#                iService[self.rndPOP.randint(0,len(iService)-1)] = 1
            for iDevice in range(self.system.fogNumber):
                chromosome[self.rndPOP.randint(0,self.system.serviceNumber-1)][iDevice]=1
#
                
            self.placeReplicasInCloud(chromosome)
        
            popT.population[individual]=chromosome
            
        self.calculatePopulationFitnessObjectives(popT)
            
#        self.calculateSolutionsWorkload(popT)
#        self.calculatePopulationFitnessObjectives(popT)


    def tournamentSelection(self,k,popSize):
        selected = sys.maxint 
        for i in range(k):
            selected = min(selected,self.rndEVOL.randint(0,popSize-1))
        return selected
           
    def fatherSelection(self, orderedFathers): #TODO
        i = self.tournamentSelection(2,len(orderedFathers))
        return  orderedFathers[i]["index"]
        

    def orderPopulation(self,popT):
        valuesToOrder=[]
        for i,v in enumerate(popT.fitness):
            citizen = {}
            citizen["index"] = i
            citizen["fitness"] = v["total"]
            valuesToOrder.append(citizen)
        
             
        return sorted(valuesToOrder, key=lambda k: (k["fitness"]))



