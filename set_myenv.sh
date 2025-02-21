#! /bin/bash
# For running Timeloopfe after installation
# Step1: Activate conda environemnt (conda activate timeloopfe)
# Step2: Set $TIMELOOPPATH to your main working directory and set $CONDAPATH to your conda installation directory
# Step3: Append the library path containing NTL and ISL installations to the environement path varaiables as follows:
export LD_LIBRARY_PATH=$TIMELOOPPATH/accelergy-timeloop-infrastructure/src/timeloop/lib:$TIMELOOPPATH/libraries/lib:$CONDAPATH/envs/timeloopfe/lib:$LD_LIBRARY_PATH
export PATH=$TIMELOOPPATH/libraries/bin:$PATH 
# Step4: Verify that the paths are set correctly
echo $PATH
echo $LD_LIBRARY_PATH
