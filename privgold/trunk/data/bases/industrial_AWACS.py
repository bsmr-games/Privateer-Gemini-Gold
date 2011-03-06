import dynamic_mission
import VS
import vsrandom
import industrial_lib
sunny=vsrandom.uniform(0,1)>.9

import land_hooks
land_hooks.run('AWACS.m3u')

time_of_day=''
dynamic_mission.CreateMissions()

industrial_lib.MakeIndustrial(sunny,time_of_day,True)
