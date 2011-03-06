import dynamic_mission
import VS
import vsrandom
import industrial_lib
sunny=vsrandom.uniform(0,1)>=.99

import land_hooks
land_hooks.run('new_detroit.m3u')

time_of_day=''
dynamic_mission.CreateMissions()

industrial_lib.MakeIndustrial(sunny,time_of_day,False)
