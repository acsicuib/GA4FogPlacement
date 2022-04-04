This program has been implemented for the research presented in the article "Evaluation and Efficiency Comparison of Evolutionary Algorithms for Service Placement Optimization in Fog Architectures", submitted for evaluation in the journal "Future Generation Computer Systems".


These are the implementations of three genetic algorithms (weighted sum, NSGA-II, and MOEA/D) for the placement of fog applications. They are implemented in python 2.7. For more details, please, read the article in TBD.

This program is released under the GPLv3 License.

**Please consider to cite this work as**:

```bash

@article{guerrero_evaluation_2019,
	title = {Evaluation and efficiency comparison of evolutionary algorithms for service placement optimization in fog architectures},
	volume = {97},
	copyright = {All rights reserved},
	issn = {0167-739X},
	url = {https://www.sciencedirect.com/science/article/pii/S0167739X18325147},
	doi = {10.1016/j.future.2019.02.056},
	abstract = {This study compares three evolutionary algorithms for the problem of fog service placement: weighted sum genetic algorithm (WSGA), non-dominated sorting genetic algorithm II (NSGA-II), and multiobjective evolutionary algorithm based on decomposition (MOEA/D). A model for the problem domain (fog architecture and fog applications) and for the optimization (objective functions and solutions) is presented. Our main concerns are related to optimize the network latency, the service spread and the use of the resources. The algorithms are evaluated with a random Barabasi–Albert network topology with 100 devices and with two experiment sizes of 100 and 200 application services. The results showed that NSGA-II obtained the highest optimizations of the objectives and the highest diversity of the solution space. On the contrary, MOEA/D was better to reduce the execution times. The WSGA algorithm did not show any benefit with regard to the other two algorithms.},
	language = {en},
	urldate = {2022-03-30},
	journal = {Future Generation Computer Systems},
	author = {Guerrero, Carlos and Lera, Isaac and Juiz, Carlos},
	month = aug,
	year = {2019},
	keywords = {Resource management, Fog computing, Evolutionary algorithms, Service placement},
	pages = {131--144},
	file = {ScienceDirect Snapshot:/Users/isaaclera/Zotero/storage/BYX6RMZ5/S0167739X18325147.html:text/html},
}

```

**Execution of the program**:

```bash
    python caller.py
```
The different configuration of the experiments are called with  "subprocess.call" to facilitate a future implementation with threads.


**Acknowledgment**:

This research was supported by the Spanish Government (Agencia Estatal de Investigacion) and the European Commission (Fondo Europeo de Desarrollo Regional) through Grant Number TIN2017-88547-P (AEI/FEDER, UE).
