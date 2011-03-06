import Base
import dynamic_mission
import VS
import land_hooks
def MakePlanet (time_of_day='_day'):
    land_hooks.run('agricultural.m3u')
    dynamic_mission.CreateMissions()
    room1 = Base.Room ('Scenery')    
    land_hooks.setup(room1)
    Base.Texture (room1, 'tex', 'bases/generic/generic'+time_of_day+'.spr', 0, 0)
    Base.Texture (room1, 'tex', 'bases/generic/holo.spr', -.5, -.4)
    Base.Comp (room1, 'Computer', -0.6, -0.8, .2578906, 0.80833, 'Computer', 'Cargo Missions')
    Base.Ship (room1, 'ship', (0,-.5,4), (0,.93,-.34), (-1,0,0))
    Base.LaunchPython (room1, 'launch','bases/launch_hooks.py', -1, -1, 2, .8, 'Launch Your Ship')

    return room1
