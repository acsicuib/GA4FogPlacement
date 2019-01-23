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

import copy
import random as random
import CONFIG as config
from topology import Entity, Topology
import json
import networkx as nx
import numpy as np
import copy
import operator


class SYSTEMMODEL:
    
    def __init__(self, conf_):
        
        
        self.fogNumber = 0 #numero de fog devices en la arquitectura
        self.serviceNumber = 0 #numero de servicios en las aplicaciones
        self.cnf = conf_





    def FGCSmodel3(self,populationSeed):
        
        
        
        
        
        fogResources = "self.rnd.randint(4,10)"
        servResources = "self.rnd.randint(1,4)"
        cloudResources = float('inf')
        netLatency = "self.rnd.randint(75,125)"
        cloudLatency = 100.0
        fogSpeed = 100
        cloudSpeed = 1000
#        cnf = config.CONFIG()
        self.rnd = random.Random()
        self.rnd.seed(populationSeed)
#        with open(cnf.topologyJson,'r') as json_data:
#            myjson = json.load(json_data)
#            json_data.close()
# 


#******************************************************************************************
#   Topology definition
#******************************************************************************************



        if self.cnf.topologyGraphml.startswith('nxgenerated'):
            tmp, numNodes = self.cnf.topologyGraphml.split('.')
            self.cnf.numberOfIoTGateways = int(int(numNodes) * 0.2)
            G = nx.barabasi_albert_graph(n=int(numNodes), m=2)
        else:
            G = nx.read_graphml(self.cnf.topologyGraphml)
            G = nx.convert_node_labels_to_integers(G, first_label=0, ordering='default', label_attribute=None)
        

        centralityMeasure = nx.betweenness_centrality(G)
        sorted_clustMeasure = sorted(centralityMeasure.items(), key=operator.itemgetter(1),reverse=True)


        
        
        
        
        
        self.fogNumber = len(G.nodes)
        self.devDistanceMatrix = [[0 for j in xrange(self.fogNumber)] for i in xrange(self.fogNumber)]
        self.fogResources = list()
        self.fogSpeedCPU = list()
        centralityBoundary = sorted_clustMeasure[self.cnf.numberOfIoTGateways * -1][1]
        gatewayCandidates = list()
        for i in list(G.nodes):
            if i == sorted_clustMeasure[0][0]:
                self.cloudDeviceId = i
                self.fogResources.append(cloudResources) #cantidad de recursos para el cloud
                self.fogSpeedCPU.append(cloudSpeed) #velocidad de CPU para el cloud
            else:
                self.fogResources.append(eval(fogResources)) #cantidad de recursos para los fog devices
                self.fogSpeedCPU.append(fogSpeed) #velocidad de CPU para los fog devices
            if centralityMeasure[i]<=centralityBoundary:
                gatewayCandidates.append(i)
                
        self.rnd.shuffle(gatewayCandidates)
        gatewayList = gatewayCandidates[:self.cnf.numberOfIoTGateways]
        
        #print gatewayList
        
        nx.set_node_attributes(G, 'fog', 'nodetype')
        for i in gatewayList:
            G.node[i]['nodetype']='gateway'
        G.node[self.cloudDeviceId]['nodetype']='cloud'
        nx.write_graphml(G, self.cnf.topologyGraphml+'.labelled')

        for s,t in list(G.edges):
            if s==self.cloudDeviceId or t==self.cloudDeviceId:
                G[s][t]['weight'] = cloudLatency #network latency for the connections with the cloud
            else:
                G[s][t]['weight'] = eval(netLatency) #network latency between fog devices
                
        for i in range(0, len(G.nodes)):
            for j in range(i,len(G.nodes)):       
        
                
                mylength = nx.shortest_path_length(G, source=i, target=j, weight="weight")
                self.devDistanceMatrix[i][j]=mylength
                self.devDistanceMatrix[j][i]=mylength
        
        
        #TODO pensar en mejorar como calcular la normalizacion del tiempo de makespan
        #quizás sería interesante pensar en usar la distancia media entre los dispositivos y el cloud, que 
        #se puede calcular con la siguiente instruccion 
        #DISTs = nx.single_source_dijkstra_path_length(G,self.cloudDeviceId)
        #d = float(sum(DISTs.values())) / (len(DISTs)-1) #Tengo que hacerlo menos 1 porque uno de ellos es el propio cloud que la distancia vale 0
        #o quizas hacerlo con el maximo con max(DISTs.values())
        
        #y la isguiente linea si queremos la distancia minima entre todos los nodos
        #self.averagePathLength = nx.average_shortest_path_length(G, weight="weight")-cloudLatency
        
        DISTs = nx.single_source_dijkstra_path_length(G,self.cloudDeviceId)
        d = max(DISTs.values())
        self.averagePathLength = d-cloudLatency
        self.totalResources = np.sum(self.fogResources[0:self.cloudDeviceId]+self.fogResources[self.cloudDeviceId+1:])    
        
#******************************************************************************************
#   Applicaiton definition
#******************************************************************************************

       
        f = open (self.cnf.applicationJson,'r')
        txtjson = f.read()
        f.close() 
        myjson = json.loads(txtjson)       
        

        self.serviceResources = list()
        for appInst in myjson:
            for moduleInst in appInst["module"]:
#TODO                self.serviceResources.append(moduleInst["RAM"])
#Si queremos que sean los valores del json, hay que borrar la siguiente linea y descomentar la anterior. 
                self.serviceResources.append(eval(servResources))
                
                
        self.serviceNumber = len(self.serviceResources)
        self.serviceMatrix = [[0 for j in xrange(self.serviceNumber*self.cnf.numberOfReplicatedApps)] for i in xrange(self.serviceNumber*self.cnf.numberOfReplicatedApps)]
 
       
        for appInst in myjson:
            for messageInst in appInst["message"]:
                for shift in range(0,self.cnf.numberOfReplicatedApps):
                    st = shift * self.serviceNumber
                    self.serviceMatrix[st+messageInst["s"]][st+messageInst["d"]]=1
        
#******************************************************************************************
#   User connection/gateways definition
#******************************************************************************************


        f = open (self.cnf.userJson,'r')
        txtjson = f.read()
        f.close() 
        myjson = json.loads(txtjson)  

        requestedServicesSet = set()
        self.mobilePlacementMatrix = [list() for i in xrange(self.serviceNumber)]
        for appInst in myjson:
            for mobileInst in appInst["mobile"]:
                self.mobilePlacementMatrix[mobileInst["serviceId"]].append(mobileInst["gatewayId"])
                requestedServicesSet.add(mobileInst["serviceId"])

        userRequestedServicesTemp = list(requestedServicesSet)
        userRequestedServices = list()
        for shift in range(0,self.cnf.numberOfReplicatedApps):
            for i in iter(userRequestedServicesTemp):
                userRequestedServices.append(i+(shift*self.serviceNumber))


        #cogemos aleatoriamente un nodo de los que son gateway y asignamos ahi el primer IoTdevice
        #a partir de ahi buscamos tantos nodos mas cercanos como iotdevices de ese servicio tengamos
        #que desplegar                
        self.mobilePlacementMatrix = [list() for i in xrange(self.serviceNumber*self.cnf.numberOfReplicatedApps)]
        numberOfRepeatedIoTDevices = self.cnf.numberOfIoTGateways*self.cnf.numberofIoTDevicesPerGw /self.cnf.numberOfReplicatedApps
        for idServ in iter(userRequestedServices):
            gwId = gatewayList[self.rnd.randint(0,len(gatewayList)-1)]
            self.mobilePlacementMatrix[idServ].append(gwId)
            candidateNeighbords = copy.copy(gatewayList)
            candidateNeighbords.remove(gwId)
            for i in range(0,numberOfRepeatedIoTDevices-1):
                minDist = float('inf')
                neighbordId = -1
                for jGw in iter(candidateNeighbords):
                    if self.devDistanceMatrix[jGw][gwId]<minDist:
                        minDist=self.devDistanceMatrix[jGw][gwId]
                        neighbordId = jGw
                self.mobilePlacementMatrix[idServ].append(neighbordId)
                candidateNeighbords.remove(neighbordId)
                        
        tmpServiceResources = copy.copy(self.serviceResources)
        self.serviceNumber=self.serviceNumber*self.cnf.numberOfReplicatedApps         
        for i in range(0,self.cnf.numberOfReplicatedApps-1):
            self.serviceResources = self.serviceResources + copy.copy(tmpServiceResources)

#******************************************************************************************
#******************************************************************************************
#******************************************************************************************
#******************************************************************************************
#   Definicion desde archivo json
#******************************************************************************************
#******************************************************************************************
#******************************************************************************************
#******************************************************************************************


    def FGCSmodel2(self,populationSeed):

#        cnf = config.CONFIG()
#        with open(cnf.topologyJson,'r') as json_data:
#            myjson = json.load(json_data)
#            json_data.close()
# 


#******************************************************************************************
#   Topology definition
#******************************************************************************************


                   
        f = open (self.cnf.topologyJson,'r')
        txtjson = f.read()
        f.close() 
        myjson = json.loads(txtjson)


        t = Topology()
        t.load(myjson)

        self.fogNumber = len(t.G.nodes)
        self.devDistanceMatrix = [[0 for j in xrange(self.fogNumber)] for i in xrange(self.fogNumber)]

        self.fogResources = list()
        self.fogSpeedCPU = list()
        
        for i in range(0,len(t.G.nodes)):
            
            if str(t.G.nodes[i]["type"]) == Entity.ENTITY_CLUSTER:
                self.cloudDeviceId = i
                self.fogResources.append(float('inf'))
                self.fogSpeedCPU.append(float(myjson["entity"][i]["IPT"])) #TODO que valor ponerle al cluster te IPTs?
            else:
                self.fogResources.append(float(myjson["entity"][i]["RAM"]))
                self.fogSpeedCPU.append(float(myjson["entity"][i]["IPT"]))
                
                
        for i in range(0, len(t.G.nodes)):
            for j in range(i,len(t.G.nodes)):       
        
                
                mylength = nx.shortest_path_length(t.G, source=i, target=j, weight="weight")
                self.devDistanceMatrix[i][j]=mylength
                self.devDistanceMatrix[j][i]=mylength
        
        self.averagePathLength = nx.average_shortest_path_length(t.G, weight="weight")
        self.totalResources = np.sum(self.fogResources[0:self.cloudDeviceId]+self.fogResources[self.cloudDeviceId+1:])    
        
#******************************************************************************************
#   Applicaiton definition
#******************************************************************************************

       
        f = open (self.cnf.applicationJson,'r')
        txtjson = f.read()
        f.close() 
        myjson = json.loads(txtjson)       
        
        
        self.serviceResources = list()
        for appInst in myjson:
            for moduleInst in appInst["module"]:
                self.serviceResources.append(moduleInst["RAM"])
                
        self.serviceNumber = len(self.serviceResources)
        self.serviceMatrix = [[0 for j in xrange(self.serviceNumber)] for i in xrange(self.serviceNumber)]
        
        for appInst in myjson:
            for messageInst in appInst["message"]:
                self.serviceMatrix[messageInst["s"]][messageInst["d"]]=1
        
#******************************************************************************************
#   User connection/gateways definition
#******************************************************************************************


        f = open (self.cnf.userJson,'r')
        txtjson = f.read()
        f.close() 
        myjson = json.loads(txtjson)  


        self.mobilePlacementMatrix = [list() for i in xrange(self.serviceNumber)]
        for appInst in myjson:
            for mobileInst in appInst["mobile"]:
                self.mobilePlacementMatrix[mobileInst["serviceId"]].append(mobileInst["gatewayId"])





#******************************************************************************************
#******************************************************************************************
#******************************************************************************************
#******************************************************************************************
#   Definicion sin archivo json
#******************************************************************************************
#******************************************************************************************
#******************************************************************************************
#******************************************************************************************
        
    def FGCSmodel(self,populationSeed):

        self.fogNumber = 5 #numero de fog devices en la arquitectura
        self.serviceNumber = 10 #numero de servicios en las aplicaciones
        
        self.rnd = random.Random()
        self.rnd.seed(populationSeed)
        
        self.cloudDeviceId = 4
        
        self.serviceMatrix = [[0 for j in xrange(self.serviceNumber)] for i in xrange(self.serviceNumber)]
        
        self.serviceMatrix[0][1]=1
        self.serviceMatrix[0][2]=1
        self.serviceMatrix[2][3]=1
        self.serviceMatrix[3][4]=1
        self.serviceMatrix[1][4]=1
        self.serviceMatrix[5][6]=1
        self.serviceMatrix[6][7]=1
        self.serviceMatrix[7][8]=1
        self.serviceMatrix[7][9]=1
        
        self.devDistanceMatrix = [[0 for j in xrange(self.fogNumber)] for i in xrange(self.fogNumber)]
        
        self.devDistanceMatrix = [[j+i for j in xrange(self.fogNumber)] for i in xrange(self.fogNumber)]
        
        self.mobilePlacementMatrix = [list() for i in xrange(self.serviceNumber)]
        
        self.mobilePlacementMatrix[0].append(2)
        
        self.mobilePlacementMatrix[5].append(0)
        self.mobilePlacementMatrix[5].append(1)
        self.mobilePlacementMatrix[5].append(2)
        
        self.fogResources = [i for i in xrange(self.fogNumber)]
        self.fogSpeedCPU = [i for i in xrange(self.fogNumber)]
        self.serviceResources = [i for i in xrange(self.serviceNumber)]

        
        
        


    
       
