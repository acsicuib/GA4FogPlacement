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
from datetime import datetime
import GAcore as gacore



class NSGA2:
    
    
    
    def __init__(self, system,populationSeed,evolutionSeed,conf_):
        
        
        self.corega = gacore.GAcore(system,populationSeed,evolutionSeed,conf_)
        
        self.corega.generatePopulation(self.corega.populationPt)



#******************************************************************************************
#   NSGA-II Algorithm
#******************************************************************************************

            
   

        
    def crowdingDistancesAssigments(self,popT,front):
        
        for i in front:
            popT.crowdingDistances[i] = float(0)
            
        frontFitness = [popT.fitness[i] for i in front]
        #OJOOOOOO hay un atributo en el listado que es index, que no se tiene que tener en cuenta.
        for key in popT.fitness[0]:
            if key!="index":   #por ese motivo está este if.
                orderedList = sorted(frontFitness, key=lambda k: k[key])
                
                popT.crowdingDistances[orderedList[0]["index"]] = float('inf')
                minObj = orderedList[0][key]
                popT.crowdingDistances[orderedList[len(orderedList)-1]["index"]] = float('inf')
                maxObj = orderedList[len(orderedList)-1][key]
                
                normalizedDenominator = float(maxObj-minObj)
                if normalizedDenominator==0.0:
                    normalizedDenominator = float('inf')
        
                for i in range(1, len(orderedList)-1):
                    popT.crowdingDistances[orderedList[i]["index"]] += (orderedList[i+1][key] - orderedList[i-1][key])/normalizedDenominator

    def calculateCrowdingDistances(self,popT):
        
        i=0
        while len(popT.fronts[i])!=0:
            self.crowdingDistancesAssigments(popT,popT.fronts[i])
            i+=1


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
            
    def fastNonDominatedSort(self,popT):
        
        self.calculateDominants(popT)
        self.calculateFronts(popT)
             
                
#******************************************************************************************
#   END NSGA-II Algorithm
#******************************************************************************************


#******************************************************************************************
#   Evolution based on NSGA-II 
#******************************************************************************************

#    def generateRoundRobin1D(self, mylistsize, mylistrange):
#        
#        mylist = []
#        rangelist = range(0,mylistrange)
#        while len(mylist)<mylistsize:
#            mylist += rangelist
#        mylist=mylist[0:mylistsize]
#        return mylist
#
#
#    def generateRoundRobin2Dshuffle(self, mylistsize, piecesize, mylistrange):
#        
#        mylist = self.generateRoundRobin1D(mylistsize,mylistrange)
#
#
#        i=0
#        mylist2=[]
#        while i<len(mylist):
#            tmppiece=mylist[i:i+piecesize]
#            self.rndPOP.shuffle(tmppiece)
#            mylist2.append(tmppiece)
#            i+=piecesize
#        self.rndPOP.shuffle(mylist2)
#        return mylist2
#
#    def serialize2D(self, mylist2):
#        
#        finallist=[]
#        for i in mylist2:
#            for j in i:
#                finallist.append(j)
#        return finallist
#    
#    
#
#
#    def generatePopulation(self,popT):
#        
#        for individual in range(self.populationSize):
#            chromosome = {}
#        
#        
#            if self.experimentScenario=='BOTH': 
#                #vmNumber = self.system.vmNumber 
#                vmNumber = max(self.rndPOP.randint(1,self.system.vmNumber),self.system.pmNumber)
#                #TODO habria que pensar si fijamos el numero minimo de VM de otra forma
#                #vmNumber = min(self.rnd.randint(1,vmNumber),self.system.pmNumber)
#
#
#            if self.experimentScenario=='VM':
#                vmNumber = max(self.rndPOP.randint(1,self.system.vmNumber),self.system.pmNumber)
#
#
#            #if the optimization is done only by managing the blocks, the number of vms
#            #is equal to the number of pms and there is a 1:1 mapping between pms and vms
#
#            if self.experimentScenario=='BLOCK':
#                vmNumber = self.system.pmNumber
#
#            block = []
#
#            if self.experimentScenario=='VM':
#                block = self.generateRoundRobin1D(self.system.replicaNumber,vmNumber)
#            
#            if self.experimentScenario=='BLOCK' or self.experimentScenario=='BOTH':   
#                block = self.generateRoundRobin2Dshuffle(self.system.replicaNumber,self.system.replicationFactor,vmNumber)
#                block = self.serialize2D(block)
#            
#            #Si en lugar de round robin queremos aleatorio, descomentar la siguiente linea
#            #block = [random.randint(0,vmNumber-1) for i in range(0,self.system.replicaNumber) ]
#            
#            vm = []
#            vm = self.generateRoundRobin1D(vmNumber,self.system.pmNumber)
#            
#            
#            
#            vmtype = []
#            vmtype = self.generateRoundRobin1D(vmNumber,len(self.system.vmTemplate))
#
#
#            if self.experimentScenario=='BOTH':
#                self.rndPOP.shuffle(vm)
#                self.rndPOP.shuffle(vmtype)
#                
#               
#            if self.experimentScenario=='VM':
#                self.rndPOP.shuffle(vmtype)            
#                self.rndPOP.shuffle(vm)            
#            
#            chromosome['block']=block
#            chromosome['vm']=vm
#            chromosome['vmtype']=vmtype
#            
#            self.removeEmptyVms(chromosome)
#            
#            popT.population[individual]=chromosome
#            popT.dominatedBy[individual]=set()
#            popT.dominatesTo[individual]=set()
#            popT.fronts[individual]=set()
#            popT.crowdingDistances[individual]=float(0)
#            
#        self.calculateSolutionsWorkload(popT)
#        self.calculatePopulationFitnessObjectives(popT)
##        self.fastNonDominatedSort(popT)
##        self.calculateCrowdingDistances(popT)
#
#    def tournamentSelection(self,k,popSize):
#        selected = sys.maxint 
#        for i in range(k):
#            selected = min(selected,self.rndEVOL.randint(0,popSize-1))
#        return selected
#           
#    def fatherSelection(self, orderedFathers): #TODO
#        i = self.tournamentSelection(2,len(orderedFathers))
#        return  orderedFathers[i]["index"]
#        
#



    def evolveToOffspring(self):
        
        offspring = pop.POPULATION(self.corega.populationSize)
        offspring.population = []

        orderedFathers = self.crowdedComparisonOrder(self.corega.populationPt)
        

        #offspring generation

        while len(offspring.population)<(self.corega.populationSize):
            father1 = self.corega.fatherSelection(orderedFathers)
            father2 = father1
            while father1 == father2:
                father2 = self.corega.fatherSelection(orderedFathers)
            #print "[Father selection]: Father1: %i **********************" % father1
            #print "[Father selection]: Father1: %i **********************" % father2
            
            self.corega.crossover(self.corega.populationPt.population[father1],self.corega.populationPt.population[father2],offspring.population)
        
        #offspring mutation
        
        for index,children in enumerate(offspring.population):
            if self.corega.rndEVOL.uniform(0,1) < self.corega.mutationProbability:
                self.corega.mutate(children)
                #print "[Offsrping generation]: Children %i MUTATED **********************" % index
            
        #print "[Offsrping generation]: Population GENERATED **********************"  
        
        return offspring

        
    def crowdedComparisonOrder(self,popT):
        valuesToOrder=[]
        for i,v in enumerate(popT.crowdingDistances):
            citizen = {}
            citizen["index"] = i
            citizen["distance"] = v
            citizen["rank"] = 0
            valuesToOrder.append(citizen)
        
        f=0    
        while len(popT.fronts[f])!=0:
            for i,v in enumerate(popT.fronts[f]):
                valuesToOrder[v]["rank"]=f
            f+=1
             
        return sorted(valuesToOrder, key=lambda k: (k["rank"],-k["distance"]))




        
       
    def evolve(self):
        
        offspring = pop.POPULATION(self.corega.populationSize)
        offspring.population = []

        pre=datetime.now()
        offspring = self.evolveToOffspring()
       
        
        pre=datetime.now()

       
        self.corega.calculatePopulationFitnessObjectives(offspring)
        
       
        
        populationRt = offspring.populationUnion(self.corega.populationPt,offspring)
        print len(self.corega.populationPt.population)
        print len(offspring.population)
        print len(populationRt.population)
        del self.corega.populationPt
        del offspring
        
        pre=datetime.now()
        self.fastNonDominatedSort(populationRt)
        self.calculateCrowdingDistances(populationRt)
        
        
        orderedElements = self.crowdedComparisonOrder(populationRt)
       
        
        finalPopulation = pop.POPULATION(self.corega.populationSize)
        
        print len(finalPopulation.population)
        
        for i in range(self.corega.populationSize):
            finalPopulation.population[i] = copy.deepcopy(populationRt.population[orderedElements[i]["index"]])
            finalPopulation.fitness[i] = copy.deepcopy(populationRt.fitness[orderedElements[i]["index"]])
            finalPopulation.vmsUsages[i] = copy.deepcopy(populationRt.vmsUsages[orderedElements[i]["index"]])
            
        del populationRt

        

        for i,v in enumerate(finalPopulation.fitness):
            finalPopulation.fitness[i]["index"]=i        
        
        self.corega.populationPt = finalPopulation
        
        
        self.fastNonDominatedSort(self.corega.populationPt)
        self.calculateCrowdingDistances(self.corega.populationPt)
        


        
       
        

#******************************************************************************************
#  END Evolution based on NSGA-II 
#******************************************************************************************



