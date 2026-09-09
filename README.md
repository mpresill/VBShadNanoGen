# VBShadNanoGen package

References for NanoGEN: https://twiki.cern.ch/twiki/bin/viewauth/CMS/NanoGen, https://indico.cern.ch/event/962610/contributions/4325186/attachments/2235981/3789869/MG5%20tutorial(1).pdf, https://github.com/FNALLPC/cmseft 
NanoGEN is a very convenient format for exploratory studies. The event content of the flat trees is similar to the generator infomration in NanoAOD, but much faster generation time because the detector simulation and reconstruction is being skipped.

References to setup the validation chain needed for EFT samples: https://indico.cern.ch/event/1602054/contributions/6877388/attachments/3210205/5718109/TopPAG_EFTValidation.pdf 

Goals of the validation:
* Check the LHE weights (PS, QCD scale ones) -- **!!maybe we should also add the pdf ones!!**
* Produce a sample that isn’t dominated by very large or very small weights 
* Validate the EFT sample reweighted to the SM point against approved central samples - following our publication https://arxiv.org/pdf/2406.14620 "LHC EFT WG Note: SMEFT predictions, event reweighting, and
simulation"
* Validate the EFT parameterization of the sample (i.e. check that the $\sigma_{EFT}$ scales appropriately to the polynomial formula) -- **!To Do!** 


## How to run it (Run 3 chain example):

### 1. make the nanoGEN files needed from the gridpacks 
Here I have included everything in a setup script, which uses my patched cmssw version:
```sh
cd generation
cmssw-el8
. setup.sh
```
then make the config for 100 events as example:
```sh
cmsDriver.py Configuration/GenProduction/python/SMP-Run3Summer23wmLHEGS-00186_cfg.py     --python_filename nanogen_cfg.py --eventcontent NANOAODGEN     --customise Configuration/DataProcessing/Utils.addMonitoring --datatier NANOAOD     --customise_commands "process.RandomNumberGeneratorService.externalLHEProducer.initialSeed=123"     --fileout file:nanogen_123.root --conditions 130X_mcRun3_2023_realistic_v14 --beamspot Realistic25ns13p6TeVEarly2023Collision     --step LHE,GEN,NANOGEN --geometry DB:Extended --era Run3 --no_exec --mc -n 100
```

```sh
cmsRun nanogen_cfg.py
```
- **!to do!**: add a setup to crab for more stat.

### 2. Analyze the nanoGEN and other scripts available to check lhe weights.

This part should work on any NanoAOD/GEN file. All scripts are in the `histograms` folder.
Those can be run in a virtual env like the following:
```
python3 -m venv coffea-env
source coffea-env/bin/activate
pip install coffea awkward hist matplotlib uproot fsspec-xrootd XRootD
```
then, for example:
`python3 lhescale_plot.py --input <file_full_path.root> --out <some_name>`

See `histograms/README.md` for the full list of scripts (single-sample LHE weight checks,
SM-vs-EFT comparisons within a channel, SM-vs-SM/EFT-vs-EFT overlays across channels, and the
shared plotting/kinematics helpers in `histogram_utils.py`), their options (`--boson-mask`,
`--top-veto`, `--drjj-cut`, `--extra-sample`, etc.), and example commands.

- Validate the EFT parameterization of the sample **TO DO**
> plot the xsection_SMEFT/xsection_SM as obtained by the sample at different reweighting points 
> ask madgraph to compute these cross-sections for a few points and compare


all checks summarized here: https://indico.cern.ch/event/1602054/contributions/6877388/attachments/3210205/5718109/TopPAG_EFTValidation.pdf 







Next part of the readme is just for my documentation, can be skipped.


----- 
----- 
## Run 3 test setup:
### Generating EDM GEN files 
Gridpack to be tested as example from VBS semileptonic final state can be found here: `/afs/cern.ch/work/m/mpresill/public/Run3_dim6_semileptonic_gridpacks/wmzjjdim6_ewk_el8_amd64_gcc10_CMSSW_12_4_8_tarball.tar.xz`.
Producing GEN files from the above gridpack is usually straight forward and similar to other CMS samples. We will use a fragment file that defines the settings that will be used for decays, parton shower and hadronization in pythia.

Run 3 fragments are taken from these [chains](https://gitlab.cern.ch/cms-gen/mccm/-/issues?sort=created_date&state=opened&search=%5BSMP%5D+VBS&first_page_size=20&show=eyJpaWQiOiIxMTk1IiwiZnVsbF9wYXRoIjoiY21zLWdlbi9tY2NtIiwiaWQiOjM1OTIxN30%3D) 
e.g. for Summer23: https://cms-pdmv-prod.web.cern.ch/mcm/requests?prepid=SMP-Run3Summer23wmLHEGS-00186&page=0&shown=127 , processed with CMSSW release `CMSSW_13_0_24`.

## Setup to keep correctly the LHE reweighting weights for run3 

### make the nanoGEN

Here I have included everything in a setup script, which uses my patched cmssw version:
```sh
cd generation
cmssw-el8
. setup.sh
```

then make the config for 100 events as example:
```sh
cmsDriver.py Configuration/GenProduction/python/SMP-Run3Summer23wmLHEGS-00186_cfg.py     --python_filename nanogen_cfg.py --eventcontent NANOAODGEN     --customise Configuration/DataProcessing/Utils.addMonitoring --datatier NANOAOD     --customise_commands "process.RandomNumberGeneratorService.externalLHEProducer.initialSeed=123"     --fileout file:nanogen_123.root --conditions 130X_mcRun3_2023_realistic_v14 --beamspot Realistic25ns13p6TeVEarly2023Collision     --step LHE,GEN,NANOGEN --geometry DB:Extended --era Run3 --no_exec --mc -n 100
```

```sh
cmsRun nanogen_cfg.py
```
[ ] **To Do**: include a crab submission to make more statistics.


### Analyze the nanoGEN and other scripts available to check lhe weights.
- plot the log10(weight) of each event is plotted, at diﬀerent reweight points
> 

- compare the SM EFT samples weighted to the EFT point to the SM EWK sampl 
> make a script with coffea to do that, give two samples (the EFT and the SM ones)

- Validate the EFT parameterization of the sample
> plot the xsection_SMEFT/xsection_SM as obtained by the sample at different reweighting points 
> ask madgraph to compute these cross-sections for a few points and compare


all checks summarized here: https://indico.cern.ch/event/1602054/contributions/6877388/attachments/3210205/5718109/TopPAG_EFTValidation.pdf 



In addition, in the `hitosgram` folder there are various codes to check lhe weights (both in nanoGEN and nanoAODs) using coffea based scripts. 
Those can be run in a virtual env like the following:
```
python3 -m venv coffea-env
source coffea-env/bin/activate
pip install coffea awkward hist matplotlib uproot fsspec-xrootd XRootD
```
then:
`python3 lhescale_plot.py --input <file_full_path.root> --out <some_name>`


--------------------------
# Various examples from Run 2:
## Previous setup to keep LHE Reweighting Weights

```sh
# Passo 0 per alma9:
cmssw-el7 # or use the singularity image from piergiulio: https://gitlab.cern.ch/cms-cat/cmssw-lxplus 
export SCRAM_ARCH=slc7_amd64_gcc700

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


---

### Comments on the PR for cmssw patch to nanoAOD LHE Rew. Weights

Patch branch: https://github.com/oponcet/cmssw/tree/from-CMSSW_13_0_14_EFT_nanogen. This is
the patched cmssw version `generation/setup.sh` cherry-picks onto `PhysicsTools/NanoAOD` in
`CMSSW_13_0_14` (see step 1 above).

Fixes EFT reweighting weight groups silently dropped during NanoAOD production due to overly strict regex patterns in `GenWeightsTableProducer`. Two root causes:

- **`weightgroupRwgt` regex** failed to match groups with additional attributes (e.g. `combine="..."`):
  ```cpp
  // Before: only matched if tag ended immediately after name/type attribute
  std::regex weightgroupRwgt("<weightgroup\\s+(?:name|type)=\"(.*)\"\\s*>");
  // After: tolerates any additional attributes before closing >
  std::regex weightgroupRwgt("<weightgroup\\s+(?:name|type)=\"([^\"]*)\"[^>]*>");
  ```

- **`rwgt` regex** used greedy `.+` causing incorrect matches on EFT weight IDs with special characters:
  ```cpp
  // Before
  std::regex rwgt("<weight\\s+id=\"(.+)\">(.+)?(</weight>)?");
  // After
  std::regex rwgt("<weight\\s+id=\"([^\"]+)\">([^<]+)?(</weight>)?");
  ```

- Adds debug log line when `weightgroupRwgt` matches, consistent with surrounding instrumentation.

Adds `.github/workflows/create-nanogen-eft-branch.yml`: a workflow that creates `nanogen_EFT_13_0_X` from `CMSSW_13_0_X` (SHA `ead39b29cdb`) in this fork and retargets this PR's base from `master` to `nanogen_EFT_13_0_X`. The workflow triggers on push to this branch and is also manually dispatchable. **It is currently pending approval** — approve the run at https://github.com/mpresill/cmssw/actions/runs/22970268679 to complete the branch creation and PR retargeting.

Inspired by [valsdav/cmssw@96ec8e7](https://github.com/valsdav/cmssw/commit/96ec8e7a596d4bf109d4e646d8989be3a74db696).