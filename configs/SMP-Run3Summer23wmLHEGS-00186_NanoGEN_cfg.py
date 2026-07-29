# Auto generated style NanoGEN configuration for CRAB PrivateMC
# CRAB config file 
import FWCore.ParameterSet.Config as cms
import os

from Configuration.Eras.Era_Run3_cff import Run3

process = cms.Process('NANOGEN', Run3)

# import of standard configurations
process.load('Configuration.StandardSequences.Services_cff')
process.load('SimGeneral.HepPDTESSource.pythiapdt_cfi')
process.load('FWCore.MessageService.MessageLogger_cfi')
process.load('Configuration.EventContent.EventContent_cff')
process.load('SimGeneral.MixingModule.mixNoPU_cfi')
process.load('Configuration.StandardSequences.GeometryRecoDB_cff')
process.load('Configuration.StandardSequences.MagneticField_cff')
process.load('Configuration.StandardSequences.Generator_cff')
process.load('IOMC.EventVertexGenerators.VtxSmearedRealistic25ns13p6TeVEarly2023Collision_cfi')
process.load('GeneratorInterface.Core.genFilterSummary_cff')
process.load('PhysicsTools.NanoAOD.nanogen_cff')
process.load('Configuration.StandardSequences.EndOfProcess_cff')
process.load('Configuration.StandardSequences.FrontierConditions_GlobalTag_cff')

process.maxEvents = cms.untracked.PSet(
    input=cms.untracked.int32(10)
)

# Input source
process.source = cms.Source('EmptySource')

process.options = cms.untracked.PSet(
    numberOfThreads=cms.untracked.uint32(1),
    numberOfStreams=cms.untracked.uint32(0),
)

# Production Info
process.configurationMetadata = cms.untracked.PSet(
    annotation=cms.untracked.string('Configuration/GenProduction/python/SMP-Run3Summer23wmLHEGS-00186_cfg.py nevts:100'),
    name=cms.untracked.string('Applications'),
    version=cms.untracked.string('$Revision: 1.19 $')
)

# Output definition
process.NANOAODGENoutput = cms.OutputModule(
    'NanoAODOutputModule',
    SelectEvents=cms.untracked.PSet(
        SelectEvents=cms.vstring('generation_step')
    ),
    compressionAlgorithm=cms.untracked.string('LZMA'),
    compressionLevel=cms.untracked.int32(9),
    dataset=cms.untracked.PSet(
        dataTier=cms.untracked.string('NANOAOD'),
        filterName=cms.untracked.string('')
    ),
    # fileName=cms.untracked.string('file:nanogen_123.root'),
    fileName = cms.untracked.string('file:WPhadWMhadJJ_EWK_SMEFT_NanoGEN.root'),
    outputCommands=process.NANOAODGENEventContent.outputCommands
)

# Other statements
process.genstepfilter.triggerConditions = cms.vstring('generation_step')
from Configuration.AlCa.GlobalTag import GlobalTag
process.GlobalTag = GlobalTag(process.GlobalTag, '130X_mcRun3_2023_realistic_v14', '')

process.generator = cms.EDFilter(
    'Pythia8ConcurrentHadronizerFilter',
    maxEventsToPrint=cms.untracked.int32(1),
    pythiaPylistVerbosity=cms.untracked.int32(1),
    filterEfficiency=cms.untracked.double(1.0),
    pythiaHepMCVerbosity=cms.untracked.bool(False),
    comEnergy=cms.double(13600.0),
    PythiaParameters=cms.PSet(
        parameterSets=cms.vstring(
            'pythia8CommonSettings',
            'pythia8CP5Settings',
            'processParameters',
            'pythia8PSweightsSettings',
        ),
        processParameters=cms.vstring(
            'SpaceShower:dipoleRecoil = 1',
            'TauDecays:externalMode = 2',
        ),
        pythia8CommonSettings=cms.vstring(
            'Tune:preferLHAPDF = 2',
            'Main:timesAllowErrors = 10000',
            'Check:epTolErr = 0.01',
            'Beams:setProductionScalesFromLHEF = off',
            # 'SLHA:keepSM = on',
            'SLHA:minMassSM = 1000.',
            'ParticleDecays:limitTau0 = on',
            'ParticleDecays:tau0Max = 10',
            'ParticleDecays:allowPhotonRadiation = on'
        ),
        pythia8CP5Settings=cms.vstring(
            'Tune:pp 14',
            'Tune:ee 7',
            'MultipartonInteractions:ecmPow=0.03344',
            'MultipartonInteractions:bProfile=2',
            'MultipartonInteractions:pT0Ref=1.41',
            'MultipartonInteractions:coreRadius=0.7634',
            'MultipartonInteractions:coreFraction=0.63',
            'ColourReconnection:range=5.176',
            'SigmaTotal:zeroAXB=off',
            'SpaceShower:alphaSorder=2',
            'SpaceShower:alphaSvalue=0.118',
            'SigmaProcess:alphaSvalue=0.118',
            'SigmaProcess:alphaSorder=2',
            'MultipartonInteractions:alphaSvalue=0.118',
            'MultipartonInteractions:alphaSorder=2',
            'TimeShower:alphaSorder=2',
            'TimeShower:alphaSvalue=0.118',
            'SigmaTotal:mode = 0',
            'SigmaTotal:sigmaEl = 21.89',
            'SigmaTotal:sigmaTot = 100.309',
            'PDF:pSet=LHAPDF6:NNPDF31_nnlo_as_0118'
        ),
        pythia8PSweightsSettings=cms.vstring(
            'UncertaintyBands:doVariations = on',
            'UncertaintyBands:List = {isrRedHi isr:muRfac=0.707,fsrRedHi fsr:muRfac=0.707,isrRedLo isr:muRfac=1.414,fsrRedLo fsr:muRfac=1.414,isrDefHi isr:muRfac=0.5,fsrDefHi fsr:muRfac=0.5,isrDefLo isr:muRfac=2.0,fsrDefLo fsr:muRfac=2.0,isrConHi isr:muRfac=0.25,fsrConHi fsr:muRfac=0.25,isrConLo isr:muRfac=4.0,fsrConLo fsr:muRfac=4.0,fsr_G2GG_muR_dn fsr:G2GG:muRfac=0.5,fsr_G2GG_muR_up fsr:G2GG:muRfac=2.0,fsr_G2QQ_muR_dn fsr:G2QQ:muRfac=0.5,fsr_G2QQ_muR_up fsr:G2QQ:muRfac=2.0,fsr_Q2QG_muR_dn fsr:Q2QG:muRfac=0.5,fsr_Q2QG_muR_up fsr:Q2QG:muRfac=2.0,fsr_X2XG_muR_dn fsr:X2XG:muRfac=0.5,fsr_X2XG_muR_up fsr:X2XG:muRfac=2.0,fsr_G2GG_cNS_dn fsr:G2GG:cNS=-2.0,fsr_G2GG_cNS_up fsr:G2GG:cNS=2.0,fsr_G2QQ_cNS_dn fsr:G2QQ:cNS=-2.0,fsr_G2QQ_cNS_up fsr:G2QQ:cNS=2.0,fsr_Q2QG_cNS_dn fsr:Q2QG:cNS=-2.0,fsr_Q2QG_cNS_up fsr:Q2QG:cNS=2.0,fsr_X2XG_cNS_dn fsr:X2XG:cNS=-2.0,fsr_X2XG_cNS_up fsr:X2XG:cNS=2.0,isr_G2GG_muR_dn isr:G2GG:muRfac=0.5,isr_G2GG_muR_up isr:G2GG:muRfac=2.0,isr_G2QQ_muR_dn isr:G2QQ:muRfac=0.5,isr_G2QQ_muR_up isr:G2QQ:muRfac=2.0,isr_Q2QG_muR_dn isr:Q2QG:muRfac=0.5,isr_Q2QG_muR_up isr:Q2QG:muRfac=2.0,isr_X2XG_muR_dn isr:X2XG:muRfac=0.5,isr_X2XG_muR_up isr:X2XG:muRfac=2.0,isr_G2GG_cNS_dn isr:G2GG:cNS=-2.0,isr_G2GG_cNS_up isr:G2GG:cNS=2.0,isr_G2QQ_cNS_dn isr:G2QQ:cNS=-2.0,isr_G2QQ_cNS_up isr:G2QQ:cNS=2.0,isr_Q2QG_cNS_dn isr:Q2QG:cNS=-2.0,isr_Q2QG_cNS_up isr:Q2QG:cNS=2.0,isr_X2XG_cNS_dn isr:X2XG:cNS=-2.0,isr_X2XG_cNS_up isr:X2XG:cNS=2.0}',
            'UncertaintyBands:nFlavQ = 4',
            'UncertaintyBands:MPIshowers = on',
            'UncertaintyBands:overSampleFSR = 10.0',
            'UncertaintyBands:overSampleISR = 10.0',
            'UncertaintyBands:FSRpTmin2Fac = 20',
            'UncertaintyBands:ISRpTmin2Fac = 1'
        ),
    ),
)


process.externalLHEProducer = cms.EDProducer(
    'ExternalLHEProducer',
    # args=cms.vstring('/uscms_data/d3/oponcet1/VBS/VBS_NanoGen_EFT/gridpacks/13p6TeV/VBS/VVjj_semileptonic_SMEFT/WMhadZlepJJ_EWK_SMEFT_el8_amd64_gcc10_CMSSW_12_4_8_tarball.tar.xz'),
    # args=cms.vstring('/cvmfs/cms-griddata.cern.ch/phys_generator/gridpacks_tarball/pp/13p6TeV/madgraph/VBS_Semileptonic/VBS_WminusZ_PolarizLL_WtoHAD_ZtoLEP_el8_amd64_gcc10_CMSSW_12_4_8_tarball.tar.xz'),
    #args = cms.vstring('root://eosuser.cern.ch//eos/user/o/oponcet2/private/gridpacks/13p6TeV/VBS/VVjj_semileptonic_SMEFT/WMhadZlepJJ_EWK_SMEFT_el8_amd64_gcc10_CMSSW_12_4_8_tarball.tar.xz'),
    # args = cms.vstring('root://cmseos.fnal.gov//store/user/oponcet/gridpacks/13p6TeV/VBS/VVjj_semileptonic_SMEFT/WMhadZlepJJ_EWK_SMEFT_el8_amd64_gcc10_CMSSW_12_4_8_tarball.tar.xz'),
    # args = cms.vstring('WMhadZlepJJ_EWK_SMEFT_el8_amd64_gcc10_CMSSW_12_4_8_tarball.tar.xz'),
    args = cms.vstring('/srv/WPhadWMhadJJ_EWK_SMEFT_el8_amd64_gcc10_CMSSW_12_4_8_tarball.tar.xz'),
    nEvents=cms.untracked.uint32(10),
    numberOfParameters=cms.uint32(1),
    outputFile=cms.string('cmsgrid_final.lhe'),
    scriptName=cms.FileInPath('GeneratorInterface/LHEInterface/data/run_generic_tarball_cvmfs.sh'),
    generateConcurrently=cms.untracked.bool(False),
)

process.ProductionFilterSequence = cms.Sequence(process.generator)

# Paths and EndPaths
process.lhe_step = cms.Path(process.externalLHEProducer)
process.generation_step = cms.Path(process.pgen)
process.nanoAOD_step = cms.Path(process.nanogenSequence)
process.genfiltersummary_step = cms.EndPath(process.genFilterSummary)
process.endjob_step = cms.EndPath(process.endOfProcess)
process.NANOAODGENoutput_step = cms.EndPath(process.NANOAODGENoutput)

# Schedule definition
process.schedule = cms.Schedule(
    process.lhe_step,
    process.generation_step,
    process.genfiltersummary_step,
    process.nanoAOD_step,
    process.endjob_step,
    process.NANOAODGENoutput_step,
)

from PhysicsTools.PatAlgos.tools.helpers import associatePatAlgosToolsTask
associatePatAlgosToolsTask(process)

for path in process.paths:
    if path in ['lhe_step']:
        continue
    getattr(process, path).insert(0, process.ProductionFilterSequence)

from PhysicsTools.NanoAOD.nanogen_cff import customizeNanoGEN
process = customizeNanoGEN(process)

from Configuration.DataProcessing.Utils import addMonitoring
process = addMonitoring(process)

# process.genWeightsTable.maxGroupsPerType = cms.vint32(-1, -1, -1, -1, -1)

from Configuration.StandardSequences.earlyDeleteSettings_cff import customiseEarlyDelete
process = customiseEarlyDelete(process)
