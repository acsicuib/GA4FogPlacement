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


import weightedGA as wga
import SYSTEMMODEL as systemmodel
import pickle
from datetime import datetime
import os
import copy
import time
import CONFIG as config
import NSGA2 as nsga2
import MOEAD as moead

import subprocess



#numAppsArray = [1,2,3]
#numAppsArray = [3]
numAppsArray = [5,10,25]


#networkTopologyArray = ['scenario/lobster100.graphml','scenario/barabasi100.graphml','scenario/euclidean100.graphml']
networkTopologyArray = ['nxgenerated.100','nxgenerated.500','nxgenerated.1000']
#networkTopologyArray = ['scenario/euclidean100.graphml']
                        
gatypeArray = ['nsga2','weightedga','moead']
#gatypeArray = ['nsga2']
#gatypeArray = ['weightedga']
#gatypeArray = ['moead']


executionId= datetime.now().strftime('%Y%m%d%H%M%S')
file_path = "./"+executionId
    
    
for networkTopology in networkTopologyArray:
    for numApps in numAppsArray:
    
        networkTopologyStr = networkTopology[networkTopology.find("/")+1:networkTopology.find(".")]
        for gatype in gatypeArray:
        
            subprocess.call(['python', 'CLcallMainGA.py' , str(numApps), networkTopology, gatype, executionId])
            #print subprocess.check_output(['ls'])
            
