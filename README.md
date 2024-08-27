# VBShadNanoGen

References for NanoGEN: https://twiki.cern.ch/twiki/bin/viewauth/CMS/NanoGen, https://indico.cern.ch/event/962610/contributions/4325186/attachments/2235981/3789869/MG5%20tutorial(1).pdf, https://github.com/FNALLPC/cmseft 


## Setup from Davide to keep LHE Reweighting Weights

```sh
# Passo 1: Creazione dell'ambiente CMSSW
cmsrel CMSSW_10_6_26
cd CMSSW_10_6_26/src
# Passo 2: Configurazione dell'ambiente
cmsenv
# Passo 3: Inizializzazione del repository Git
git cms-init
# Passo 4: Aggiunta del repository remoto
git remote add valsdav git@github.com:valsdav/cmssw.git
# Passo 5: Recupero della branch desiderata
git fetch valsdav nanogen_EFT_weightspatch_10_6_26
# Passo 6: Unione della branch nel tuo ambiente di lavoro
git checkout -b nanogen_EFT_weightspatch_10_6_26 valsdav/nanogen_EFT_weightspatch_10_6_26
# Passo 7: Compilazione del codice
scram b -j 5


# Passo 8: configura questa cartella per la sottomissione dei files 
mkdir Configuration
cd Configuration
git clone git@github.com:mpresill/VBShadNanoGen.git #or just create your fragment in a <name>/python subfolder
scram b
```



# Various examples:
## Setup to run NanoGen with default weights

```sh
cmsrel CMSSW_11_2_0_pre7
cd CMSSW_11_0_0_pre7/src
cmsenv
# The following merge is not strictly necessary, but it enables a bit of functionality
git cms-init
git cms-merge-topic kdlong:NanoGen_dqm
scram b -j 5

mkdir Configuration
cd Configuration
git clone git@github.com:kdlong/WMassNanoGen.git #or just create your fragment in a <name>/python subfolder
scram b
```

## Setup to store all genWeights

```sh 
cmsrel CMSSW_10_6_18
cd CMSSW_10_6_18/src
cmsenv
git cms-init
git cms-merge-topic kdlong:NanoGenWeights_CMSSW_10_6_18
scram b -j 5

mkdir Configuration
cd Configuration
git clone git@github.com:kdlong/WMassNanoGen.git
scram b
```



# Making configs and running

First create a config fragment in python/. Follow the other examples there.
Generate the config for NanoGen with cmsDriver. If you want gridpack --> NanoGen, you can use the script runCmsDriverNanoGen.sh. To generate a full config from your fragment and run:
```sh
scram b
runCmsDriverNanoGen.sh <fragmentName_cff.py> <outputFile.root>
cmsRun fragmentName_cfg.py
```
An example to generate NanoGen from a MiniAOD file (useful to keep more gen particles or more LHE weights) is in runCmsDriverGenericMiniToNanoGen.sh.
```sh
scram b
cmsDriverZJMiNNLONanoGen.sh
cmsRun fragmentName_cfg.py
```
Example crab submit files are in the crab_submit_files directory. Note that you need to copy the gridpacks to a location readable from crab for this to work.

