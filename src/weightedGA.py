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



class weightedGA:
    
    
    
    def __init__(self, system,populationSeed,evolutionSeed,conf_):
        

        self.corega = gacore.GAcore(system,populationSeed,evolutionSeed,conf_)
        
        self.corega.generatePopulation(self.corega.populationPt)
        

    def evolveToOffspring(self):
        
        offspring = pop.POPULATION(self.corega.populationSize)
        offspring.population = []

        orderedFathers = self.corega.orderPopulation(self.corega.populationPt)
        

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

 
    def evolve(self):
        
        offspring = pop.POPULATION(self.corega.populationSize)
        offspring.population = []

        offspring = self.evolveToOffspring()
        
#        if self.autoAjustedWeight:
#            populationRt = offspring.populationUnion(self.populationPt,offspring)
#            self.calculatePopulationFitnessObjectives(populationRt)
#        else:
        self.corega.calculatePopulationFitnessObjectives(offspring)
        populationRt = offspring.populationUnion(self.corega.populationPt,offspring)
        
        del self.corega.populationPt
        del offspring
        
       
        orderedElements = self.corega.orderPopulation(populationRt)
        
        finalPopulation = pop.POPULATION(self.corega.populationSize)
        
        for i in range(self.corega.populationSize):
            finalPopulation.population[i] = copy.deepcopy(populationRt.population[orderedElements[i]["index"]])
            finalPopulation.fitness[i] = copy.deepcopy(populationRt.fitness[orderedElements[i]["index"]])
        
        del populationRt

        for i,v in enumerate(finalPopulation.fitness):
            finalPopulation.fitness[i]["index"]=i        
        
        self.corega.populationPt = finalPopulation
        

