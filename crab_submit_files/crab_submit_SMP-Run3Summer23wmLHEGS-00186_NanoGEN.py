from CRABClient.UserUtilities import config
config = config()

# -------------------------
# General
# -------------------------
config.General.requestName = 'SMP-Run3Summer23wmLHEGS-00186-NanoGEN'
config.General.workArea = 'crab_projects'
config.General.transferOutputs = True
config.General.transferLogs = True

# -------------------------
# Job type
# -------------------------
config.JobType.pluginName = 'PrivateMC'
config.JobType.psetName = '../configs/SMP-Run3Summer23wmLHEGS-00186_NanoGEN_cfg.py'
config.JobType.allowUndistributedCMSSW = True
config.JobType.numCores = 1
config.JobType.maxMemoryMB = 3000

# -------------------------
# Data (GEN production)
# -------------------------
config.Data.outputPrimaryDataset = 'SMP-Run3Summer23wmLHEGS-00186'

config.Data.splitting = 'EventBased'
config.Data.unitsPerJob = 20
config.Data.totalUnits = 100
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