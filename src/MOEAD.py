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
import GAcore as gacore
import CONFIG as config



class MOEAD:
    
    
    
    def __init__(self, system,populationSeed,evolutionSeed,conf_):
        

        

        #self.cnf = config.CONFIG()
        self.cnf = conf_

        self.T = self.cnf.T
        self.Lamb,self.N=self.Initial(self.cnf.numberOfSubproblems)
        self.B=self.Neighbor(self.Lamb,self.T)
        self.z={}
        self.z["makespan"] = float('inf')
        self.z["spread"] = float('inf')
        self.z["resources"] = float('inf')
        #self.EP = pop.POPULATION(0)
        


        self.corega = gacore.GAcore(system,populationSeed,evolutionSeed,self.cnf,self.N)
        self.popN = self.corega.populationPt # self.popN hace de p (población con la mejor solución para cada vector de lambda)
        self.corega.populationPt = pop.POPULATION(0)  #self.corega.populationPt hace de EP, el conjunto de todas las soluciones 
        
        self.corega.generatePopulation(self.popN)
        
        self.BestValue()

#        self.t=0
        

    def calculateDominants(self,popT):
        
        for i in range(len(popT.population)):
            popT.dominatedBy[i] = set()
            popT.dominatesTo[i] = set()
            popT.fronts[i] = set()

        for p in range(len(popT.population)):
            for q in range(p+1,len(popT.population)):
                if self.corega.dominates(popT.fitness[p],popT.fitness[q]):
                    popT.dominatesTo[p].add(q)
                    popT.dominatedBy[q].add(p)
                if self.corega.dominates(popT.fitness[q],popT.fitness[p]):
                    popT.dominatedBy[p].add(q)
                    popT.dominatesTo[q].add(p)        

    def calculateFronts(self,popT):

        addedToFronts = set()
        
        i=0
        while len(addedToFronts)<len(popT.population):
            popT.fronts[i] = set([index for index,item in enumerate(popT.dominatedBy) if item==set()])
            addedToFronts = addedToFronts | popT.fronts[i]
            
            for index,item in enumerate(popT.dominatedBy):
                if index in popT.fronts[i]:
                    popT.dominatedBy[index].add(-1)
                else:
                    popT.dominatedBy[index] = popT.dominatedBy[index] - popT.fronts[i]
            i+=1        

    def calculateParetoFront(self,popT):

        addedToFronts = set()
        
        i=0

        popT.fronts[i] = set([index for index,item in enumerate(popT.dominatedBy) if item==set()])
        addedToFronts = addedToFronts | popT.fronts[i]
        
        for index,item in enumerate(popT.dominatedBy):
            if index in popT.fronts[i]:
                popT.dominatedBy[index].add(-1)
            else:
                popT.dominatedBy[index] = popT.dominatedBy[index] - popT.fronts[i]
      

            
    def fastNonDominatedSort(self,popT):
        
        self.calculateDominants(popT)
        self.calculateParetoFront(popT)
 


    def Initial(self,N):
        #initialize weight vector lambda list
  
        m = N

        Lamb = list()
        for i in xrange(m):
            for j in xrange(m):
                if i+j <= m:
                    k = m - i - j
                    try:
                        weight_scalars = [None] * 3
                        weight_scalars[0] = float(i) / (m)
                        weight_scalars[1] = float(j) / (m)
                        weight_scalars[2] = float(k) / (m)
                        Lamb.append(weight_scalars)
                    except Exception as e:
                        print "Error creating weight with 3 objectives at:"
                        print "i", i
                        print "j", j
                        print "k", k
                        raise e
        # Trim number of weights to fit population size YO fijo N mas pequeño para que me salga el tamaño bucado.
#        Lamb = sorted((x for x in Lamb), key=lambda x: sum(x), reverse=True)
#        Lamb = Lamb[:N]    
    
    
        return Lamb,len(Lamb)
    
    



    def Neighbor(self,Lamb,T):
        #Lambda list,numbers of neighbors is T
        B=[]
        for i in range(len(Lamb)):
            temp=[]
            for j in range(len(Lamb)):
                distance=np.sqrt((Lamb[i][0]-Lamb[j][0])**2+(Lamb[i][1]-Lamb[j][1])**2)
                temp.append(distance)
            l=np.argsort(temp)
            B.append(l[:T])
        return B
    
    
    def BestValue(self):
        #get the bestvalues of each function,which used as the reference point
        #if goal for function is minimazaton,z is the minimize values


        for solFitness in iter(self.popN.fitness):
            if solFitness['spread']<self.z['spread']:
                self.z['spread'] = solFitness['spread']
            if solFitness['makespan']<self.z['makespan']:
                self.z['makespan'] = solFitness['makespan']
            if solFitness['resources']<self.z['resources']:
                self.z['resources'] = solFitness['resources']
    
#    def dominates(self,a,b):
#        #checks if solution a dominates solution b, i.e. all the objectives are better in A than in B
#        Adominates = True
#        #### OJOOOOOO Hay un atributo en los dictionarios que no hay que tener en cuenta, el index!!!
#        for key in a:
#            if key!="index":  #por ese motivo está este if.
#                if b[key]<=a[key]:
#                    Adominates = False
#                    break
#        return Adominates        


    def Tchebycheff(self,fitness,lamb,z):
        #Tchebycheff approach operator
    
        temp=[]
        
        for i,obj in enumerate(['makespan','resources','spread']):
            temp.append(np.abs(fitness[obj]-z[obj])*lamb[i])
        return np.max(temp)


 

        
        
    def evolve(self):

        offspring = pop.POPULATION(self.N)
        offspring.population = []
        offspring.fitness = []

        
        
        for i in range(self.N):
            k = self.corega.rndEVOL.randint(0, self.T - 1)
            l = self.corega.rndEVOL.randint(0, self.T - 1)
            
            f1Id= self.B[i][k]
            f2Id= self.B[i][l]

            y1,y2 = self.corega.crossover(self.popN.population[f1Id],self.popN.population[f2Id])
            if self.corega.rndEVOL.uniform(0,1) < self.corega.mutationProbability:
                self.corega.mutate(y1)
            if self.corega.rndEVOL.uniform(0,1) < self.corega.mutationProbability:
                self.corega.mutate(y2)                

            
            fy1 = self.corega.calculateFitnessObjectives(y1)
            fy2 = self.corega.calculateFitnessObjectives(y2)
            
            if self.corega.dominates(fy1,fy2):
                y=y1
                del y2
                y1 = None
                yfitness = fy1
            else:
                y=y2
                del y1
                y2 = None
                yfitness = fy2
                

            
            if yfitness['spread']<self.z['spread']:
                self.z['spread'] = yfitness['spread']
            if yfitness['makespan']<self.z['makespan']:
                self.z['makespan'] = yfitness['makespan']
            if yfitness['resources']<self.z['resources']:
                self.z['resources'] = yfitness['resources']            
            
#            t=self.cnf.getTime()
            #la nueva solucion creada reemplaza a la solucion del vector correspondiente si su distancia de tchebycheff es menor
            for j in range(len(self.B[i])):
                idSol = self.B[i][j]
                Ta = self.Tchebycheff(self.popN.fitness[idSol], self.Lamb[idSol], self.z)
                Tb = self.Tchebycheff(yfitness, self.Lamb[idSol], self.z)
                if Tb < Ta: 
                    poptmp_ = self.popN.population[idSol]
                    self.popN.population[idSol] = y
                    del poptmp_
                    self.popN.fitness[idSol] = yfitness

#            self.cnf.printTime(t,"Distancia tchebycheff: ")


#            t=self.cnf.getTime()
#            #la nueva solucion creada solo se incluye en el conjunto de soluciones si no es dominada por nadie.
#            if len(self.corega.populationPt.population) == 0:
#                self.corega.populationPt= self.corega.populationPt.populationUnion(self.corega.populationPt,oneSolPop)
#            else:
#                dominateY = False
#                rmlist=[]
#                for j in range(len(self.corega.populationPt.population)):
#                    if self.corega.dominates(yfitness, self.corega.populationPt.fitness[0]):
#                        rmlist.append(j)
#                    elif self.corega.dominates(self.corega.populationPt.fitness[0],yfitness):
#                        dominateY = True
#                        break
#
#                if dominateY == False:
#                    for index in sorted(rmlist, reverse=True):
#                        self.corega.populationPt.remove(index)     
#                    self.corega.populationPt= self.corega.populationPt.populationUnion(self.corega.populationPt,oneSolPop)
#            self.cnf.printTime(t,"Incluirlo en los dominantes: ")
            
            
            offspring.population.append(y)
            offspring.fitness.append(yfitness)
            
        populationRt = offspring.populationUnion(self.corega.populationPt,offspring)
        
        del offspring
        del self.corega.populationPt
        
        self.fastNonDominatedSort(populationRt)
        

        
        self.corega.populationPt = pop.POPULATION(len(populationRt.fronts[0]))
        self.corega.populationPt.population = []
        self.corega.populationPt.fitness = []
        

            



        for idxSol in populationRt.fronts[0]:
            self.corega.populationPt.population.append(copy.deepcopy(populationRt.population[idxSol]))
            self.corega.populationPt.fitness.append(copy.deepcopy(populationRt.fitness[idxSol]))


        if self.cnf.retailEPmoead:
            tempPopulationPt = self.corega.populationPt
            popSize = min(len(populationRt.fronts[0]),self.cnf.EPlimit)
            self.corega.populationPt = pop.POPULATION(popSize)
            orderedElements = self.corega.orderPopulation(tempPopulationPt)
            for i in range(popSize):
                self.corega.populationPt.population[i] = copy.deepcopy(tempPopulationPt.population[orderedElements[i]["index"]])
                self.corega.populationPt.fitness[i] = copy.deepcopy(tempPopulationPt.fitness[orderedElements[i]["index"]])
    
            for i,v in enumerate(self.corega.populationPt.fitness):
                self.corega.populationPt.fitness[i]["index"]=i          
        
        del tempPopulationPt
        del populationRt
         

