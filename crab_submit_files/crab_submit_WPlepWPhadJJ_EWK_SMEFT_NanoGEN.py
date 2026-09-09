from CRABClient.UserUtilities import config
config = config()

# -------------------------
# General
# -------------------------
config.General.requestName = 'WPlepWPhadJJ_EWK_SMEFT-NanoGEN'
config.General.workArea = 'crab_projects'
config.General.transferOutputs = True
config.General.transferLogs = True

# -------------------------
# Job type
# -------------------------
config.JobType.pluginName = 'PrivateMC'
config.JobType.psetName = '../configs/WPlepWPhadJJ_EWK_SMEFT_NanoGEN_cfg.py'
config.JobType.inputFiles = ["/uscms_data/d3/oponcet1/VBS/VBS_NanoGen_EFT/crab_submit_files/WPlepWPhadJJ_EWK_SMEFT_el8_amd64_gcc10_CMSSW_12_4_8_tarball.tar.xz"]
config.JobType.allowUndistributedCMSSW = True
config.JobType.numCores = 1
config.JobType.maxMemoryMB = 3000

# -------------------------
# Data (GEN production)
# -------------------------
config.Data.outputPrimaryDataset = 'WPlepWPhadJJ_EWK_SMEFT'

config.Data.splitting = 'EventBased'
config.Data.unitsPerJob = 100
config.Data.totalUnits  = 10000
# -------------------------
# Output
# -------------------------
config.Data.outLFNDirBase = '/store/user/oponcet/'
config.Data.publication = False
config.Data.outputDatasetTag = 'Run3Summer23_NanoGEN_v2'

# -------------------------
# Site
# -------------------------
config.Site.storageSite = 'T3_US_FNALLPC'
