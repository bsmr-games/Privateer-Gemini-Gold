import Director
import patrol
import cargo_mission
import bounty
import plunder
import defend
import escort_mission
import vsrandom
import universe
import faction_ships
import VS
import PickleTools
last_constructor={}
saved_args = (1,1,1,1,)#nice patrol args
last_args ={}
last_briefing=[{},{}]
last_briefing_vars=[{},{}]
active_missions = []
active_missions_nextid = 0

lastMission=None

hookargs = None

class missionhook:
	def __init__(self,amentry):
		self.amentry_id = AddActiveMissionEntry(amentry)
		print "New Mission entry: %s (%s)" % (self.amentry_id,amentry.get('MISSION_SHORTDESC',''))
	def __del__(self):
		RemoveActiveMissionEntry(self.amentry_id)
		print "Mission entry %s destroyed." % self.amentry_id

def SetMissionHookArgs(args):
    global hookargs
    hookargs = args

def AddMissionHooks(director):
    global hookargs
    doMissionHooks=True
    try:
        if hasattr(director,'aborted'):
            if getattr(director,'aborted'):
                doMissionHooks=False
    except:
        import sys
        print sys.exc_info()[0]
        print sys.exc_info()[1]
        print "CARGO MISSION ABORTING done"
    if doMissionHooks:
        director.mission_hooks___ = missionhook(hookargs)
    
def SetLastMission(which):
	global lastMission
	lastMission=str(which)
	print 'set last mission to "'+str(which)+'"'

def LoadLastMission(which=None):
	global lastMission
	global active_missions
	if which is None:
		which=lastMission
	if which in last_constructor and which in last_args:
		if last_constructor[which]==None:
			if type(last_args[which])==str:
				script = "%(args)s"
			else:
				script = "%(args)r()"
			vars = dict(args=last_args[which])
		else:
			script = '''#
import %(constructor)s
temp=%(constructor)s.%(constructor)s%(args)s
mission_lib.AddMissionHooks(temp)
temp=0
'''
			cons=last_constructor[which]
			if type(cons)!=str:
				cons=cons.__name__
			if type(last_args[which])==str:
				args = last_args[which]
			else:
				args = repr(last_args[which])
			vars = dict(constructor=cons,args=args)
		script = script % vars
		if script[:1] == '#':
			prescript = '''#
import mission_lib
mission_lib.SetMissionHookArgs(%(amentry)r)
%(postscript)s'''
			amentry = last_briefing_vars[0].get(which,dict())
			try:
				amentry.update(last_briefing_vars[1].get(which,dict()).iteritems())
				amentry.update([
					('MISSION_NAME',which),
					('DESCRIPTION',last_briefing[0].get(which,'')),
					('ACCEPT_MESSAGE',last_briefing[1].get(which,'')) 
					])
			except:
				print "TRACING BACK"
				import sys
				print sys.exc_info()[0]
				print sys.exc_info()[1]
				print "BACKTRACE done"
			vars = dict(amentry=amentry,postscript=script)
			script = prescript % vars
		print "Loading mission:\n%s" % script
		VS.LoadMissionScript(script)
	else:
		print 'No last mission with name "'+str(which)+'"'
	for container in (	last_args,last_constructor,
						last_briefing[0],last_briefing[1],
						last_briefing_vars[0],last_briefing_vars[1]  ):
		if which in container:
			del container[which]
	lastMission=None

def AddActiveMissionEntry(entry):
	global active_missions
	global active_missions_nextid
	active_missions.append(entry)
	active_missions[-1].update([('ENTRY_ID',active_missions_nextid)])
	active_missions_nextid += 1
	return active_missions_nextid-1

def RemoveActiveMissionEntry(entry_id):
	global active_missions
	active_missions = filter(lambda x:x.get('ENTRY_ID',None)!=entry_id,active_missions)

def CountMissions(first,prefix):
	nummissions = 0
	for which in last_briefing[first]:
		if str(which).startswith(prefix):
			nummissions = nummissions + 1
	return nummissions

def BriefLastMission(which,first,textbox=None,template='#DESCRIPTION#'):
	import Base
	which=str(which)
	if first<0 or first>=len(last_briefing):
		return
	if (which in last_briefing[first]):
		# compute variables
		s_which = str(which).split('/')
		w_prefix = ''
		curmission = s_which[len(s_which)-1]
		if str(int(curmission)) == curmission:
			# allow non-numeric mission identifiers ( 'Disc_1', anyone? )
			# But for numeric identifiers, convert base-0 to base-1 indices
			curmission = str(int(curmission)+1)
		for i in s_which[:len(s_which)-1]:
			w_prefix += str(i) + '/'
		nummissions = CountMissions(first,w_prefix)

		# replace variables in template
		template = template.replace('#MISSION_NUMBER#',str(curmission))
		template = template.replace('#MISSION_ID#',which)
		template = template.replace('#GUILD_NAME#',s_which[0])
		template = template.replace('#NUM_MISSIONS#',str(nummissions))
		template = template.replace('#DESCRIPTION#',str(last_briefing[first][which]))
		template = template.replace('#SHORT_DESCRIPTION#',str(last_briefing_vars[first][which]['MISSION_SHORTDESC']))
		try:    
			template = template.replace('#MISSION_TYPE#',last_briefing_vars[first][which]['MISSION_TYPE'])
		except: 
			template = template.replace('#MISSION_TYPE#','')

		# set text
		if textbox:
			Base.SetTextBoxText(Base.GetCurRoom(),textbox, template)
		else:
			Base.Message (template)

def AddNewMission(which,args,constructor=None,briefing0='',briefing1='',vars0=None,vars1=None):
	which=str(which)
	last_constructor[which]=constructor
	last_args[which]=args
	last_briefing[0][which]=briefing0
	last_briefing[1][which]=briefing1
	last_briefing_vars[0][which]=vars0
	last_briefing_vars[1][which]=vars1

def GetMissionList(activelist=True):
	global active_missions
	if activelist:
		return active_missions
	else:
		return list( dict( list(last_briefing_vars[0][index].iteritems())+
						[('DESCRIPTION',last_briefing[0][index]),
						 ('ACCEPT_MESSAGE',last_briefing[1][index]),
						 ('MISSION_NAME',index)] )
					 for index in last_briefing[0] )

def Jumplist (jumps):
	if not len(jumps):
		return 'Your destination is this system.'
	str="First of all, you will need to fly to the %s jumppoint. "%jumps[0].split('/')[-1]
	for j in jumps[1:]:
		str+="Then jump in the %s jumppoint. "%j.split('/')[-1]
	return str

def MakePlunder(which):
	constructor = plunder.plunder
	creds=vsrandom.randrange(15,25)*1000
	args = (creds,'pirates',5,'Contraband',1)
	briefing0 = 'Arr Matey. We have a target in this system that needs a lil roughin up. We need you to bag a merchant and deliver her cargo into our hands.  It\'s worth '+str(creds)+ ' to us. Up to you, ya space pirate.'
	briefing1 = 'Ahoy! We\'ll be lookin for that cargo mighty soon!'
	vars = { 'MISSION_TYPE' : 'PIRACY',
			 'MISSION_SHORTDESC' : 'Plunder merchant target for %s' % creds }
	AddNewMission(which,args,constructor,briefing0,briefing1,vars,vars)
	return ("bases/fixers/pirate.spr","Talk with the Pirate")

def MakeContraband(which):
	constructor = cargo_mission.cargo_mission
	numsys=vsrandom.randrange(2,5)
	jumps=universe.getAdjacentSystems(VS.getSystemFile(),numsys)[1]
	diff=vsrandom.randrange(0,3)
	creds=numsys*2500+diff*800
	args = ('pirates', 0, 6, diff,creds, 1, 1200, 'Contraband',jumps)
	briefing0 = 'We need some...*cough*... cargo delivered to some of our pirates in a nearby system: '+ Jumplist(jumps)+ ' It\'d be preferable if ye kept the ole po\' off yo back durin the run. Will ya do it for '+str(creds)+' creds?'
	briefing1 = 'Thanks pal; keep it on the d&l if you know my meanin.'
	vars = { 'MISSION_TYPE' : 'CONTRABAND',
			 'MISSION_SHORTDESC' : 'Deliver contraband to %s for %s' % (Jumplist(jumps),creds) }
	AddNewMission(which,args,constructor,briefing0,briefing1,vars,vars)
	return ("bases/fixers/pirate.spr","Talk with the Pirate")

def CreateRandomMission(whichnum):
	"""This function gets a random mission and saves the infomation in
an array as the which element. Returns the sprite file and text"""
	which=str(whichnum)
	missiontype = vsrandom.random();
	fac = VS.GetGalaxyFaction(VS.getSystemFile())
	if fac=="pirates":
		if (missiontype>.5):
			return ()
		missiontype*=.2;
	elif (VS.GetRelation(fac,"pirates")<-.8 and missiontype<.1):
		missiontype=.1+.9*missiontype
	plr=VS.getPlayer().isPlayerStarship()
	if (missiontype<.05):
		return MakePlunder(which)
	elif (missiontype<.1):####CONTRABAND
		return MakeContraband(which)
	else:
		goodlist=[]
		for indx in range(Director.getSaveStringLength(plr, "mission_scripts")):
			script=Director.getSaveString(plr,"mission_scripts",indx)
			if script.find("#F#")!=-1:
				goodlist.append(indx)
		goodlist.sort()
		goodlist.reverse()
		if len(goodlist):
			i=goodlist[vsrandom.randrange(len(goodlist))]
			script=Director.getSaveString(plr,"mission_scripts",i)
			desc=Director.getSaveString(plr,"mission_descriptions",i)
			vars=PickleTools.decodeMap( Director.getSaveString(plr,"mission_vars",i) )
			vars.setdefault('MISSION_SHORTDESC',Director.getSaveString(plr, "mission_names",i))
			Director.eraseSaveString(plr,"misson_scripts",i)
			Director.eraseSaveString(plr,"misson_descriptions",i)
			Director.eraseSaveString(plr,"misson_names",i)
			Director.eraseSaveString(plr,"misson_vars",i)
			mylist=script.split("#")  ###Skip the first two because first is always '' and second is always 'F'
			AddNewMission(which,script,None,desc,mylist[4],vars,vars)
			return (mylist[2],mylist[3])
		else:
			# It should only get here if no fixer missions were found
			return ()  # Fixer code will generate a NoFixer hopefully.
##			  if (searchMissionNameStr("patrol")):
##					last_briefing[0][which] = 'Confed needs the help of mercs and hunters to keep our air space clean.  There are increasing reports of pirate and alien activity in these sectors and we need your sensor data. '+Jumplist(jumps) +' Will you do the patrol in said system for '+str(creds)+' credits?'
##			  if (searchMissionNameStr("cargo")):
##					last_briefing[0][which] = 'Our business needs you to run some legit goods to a base a few systems away. '+ Jumplist(jumps) + ' This is worth '+str(creds)+' to us.'
##					if (diff>=2):
##							last_briefing[0][which]+=' However, you cannot fail us!  There are consequences for your actions in this universe.'
##			  if (searchMissionNameStr("bounty")):
##					last_briefing[0][which] = 'We need you to hit a nearby target. '+Jumplist(jumps)+' Our reward is '+str(creds)+' will you do it?'
##			  if (searchMissionNameStr("defend")):
##					last_briefing[0][which] = 'We need help to secure a nearby strategic point in this system. Eliminate all enemies there. We offer '+str(encred)+' per enemy. Will you do it?'
##					if (base):
##							last_briefing[0][which] = 'One of our capitol vessels is under attack in this system! We call to the aid of all bounty hunters to defend it.  Our reward is '+str(encred)+' per enemy craft destroyed.  Will you help us?'

def PickRandomMission(goodlist):
	bounds = 0
	for mis in goodlist:
		bounds = bounds + mis[1]
	if bounds:
		pos = vsrandom.randrange(bounds)
		for midx in range(len(goodlist)):
			if pos>=goodlist[midx][1]:
				pos = pos - goodlist[midx][1]
			else:
				return midx
		return len(goodlist)-1
	else:
		return None

# accepttypes is a dictionary that takes mission types as keys, and has
# mission frequencies (likelihood of appearing) as values. A special key
# is the asterisk ('*'), which is a wildcard key that applies to any other
# key. If a mission's type cannot find a matching key (the wildcard matches
# all), then it will have frequency 0 (meaning, it will be disallowed).
def CreateGuildMissions(guildname,nummissions,accepttypes,prefix,acceptmsg=''):
	plr=VS.getPlayer().isPlayerStarship()
	goodlist=[]
	for indx in range(Director.getSaveStringLength(plr, "mission_scripts")):
		script=Director.getSaveString(plr,"mission_scripts",indx)
		if (script.find(prefix)!=-1):
			missiontype=script[3:script.find('#',3)]
			freq = 0
			if (accepttypes==None):
				freq = 1
			elif (missiontype in accepttypes):
				freq = accepttypes[missiontype]
			elif ('*' in accepttypes):
				freq = accepttypes['*']
			if freq:
				goodlist.append( (indx,freq) )
	if len(goodlist)<nummissions:
		nummissions=len(goodlist)
	delit=[]
	for missionnum in range(0,nummissions):
		goodi=PickRandomMission(goodlist)
		if goodi == None:
			break
		i=goodlist[goodi][0]
		which=guildname+'/'+str(missionnum)
		script=Director.getSaveString(plr,"mission_scripts",i)
		desc=Director.getSaveString(plr,"mission_descriptions",i)
		vars=PickleTools.decodeMap( Director.getSaveString(plr,"mission_vars",i) )
		vars.setdefault('MISSION_SHORTDESC',Director.getSaveString(plr,"mission_names",i))
		delit.append(i)
		AddNewMission(which,script,None,desc,acceptmsg,vars,vars)
		goodlist.pop(goodi)
	delit.sort()
	delit.reverse()
	for i in delit:
		Director.eraseSaveString(plr,"mission_scripts",i)
		Director.eraseSaveString(plr,"mission_descriptions",i)
		Director.eraseSaveString(plr,"mission_names",i)
		Director.eraseSaveString(plr,"mission_vars",i)
	#more reliable... sometimes we run out of good missions, 
	#sometimes we have preexistent missions (!)
	return CountMissions(0,guildname)

