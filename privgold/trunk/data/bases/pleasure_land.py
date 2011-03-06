import Base
import PlayerShip
import land_hooks

def MakePleasureAgriculturalLanding(time_of_day='', hook=land_hooks.setup):
	room0 = Base.Room ('Landing_Pad')
	hook(room0)
	Base.Texture (room0, 'background', 'bases/pleasure/Jolson_LandingBay'+time_of_day+'.spr', 0, 0)
	Base.Texture (room0, 'background', 'bases/pleasure/Jolson_LandingBay_wtr'+time_of_day+'.spr', 0, 0)
	Base.Texture (room0, 'background', 'bases/pleasure/Jolson_LandingBay_blt'+time_of_day+'.spr', 0.3576875, -0.0582)

	PlayerShip.InitPlayerShips()
	PlayerShip.AddPlayerShips('pleasure',room0,'landship')

	Base.LaunchPython (room0, 'my_launch_id', 'bases/launch_hooks.py', -0.3125, -0.543333, 0.8975, 0.54, 'Launch')

	return room0
