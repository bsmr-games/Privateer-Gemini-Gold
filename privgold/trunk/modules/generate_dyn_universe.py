import VS
import Director
import vsrandom
import fg_util
import dj_lib # Needs to be enabled when loading.
import campaigns
from universe import getAdjacentSystemList,AllSystems
import debug

cp=fg_util.ccp
maxshipsinfg=20
fgnames=[] #list of lists of flightgroup names for each faction
origfgnames=[]
import faction_ships
def XProductionRate(fac,type):
    if fac in type:
        return type[fac]
    return type["default"]

def GenerateFgShips (shipinfg,factionnr,friendly):
    lst=[]
    capship=()
    fac = faction_ships.intToFaction(factionnr)
    fpr=XProductionRate(fac,faction_ships.fighterProductionRate)
    cpr=XProductionRate(fac,faction_ships.capitalProductionRate)
    if cpr>0 and (friendly==2 or (friendly==1 and vsrandom.random()<cpr/fpr)):
        capship=((faction_ships.getRandomCapitolInt(factionnr),1),)
        debug.debug("Generating capital "+str(capship))
    return ((faction_ships.getRandomFighterInt(factionnr),shipinfg),)+capship

def GenerateAllShips ():
    global fgnames,origfgnames
    for fnr in range(faction_ships.getMaxFactions()):
        fgnames.append(fg_util.GetRandomFGNames(1,faction_ships.factions[fnr]))
        origfgnames.append(list(fgnames[-1]))


doNotAddBasesTo={"enigma_sector/heavens_gate":1,"sol_sector/celeste":1,"enigma_sector/enigma":1,"enigma_sector/niven":1,"Gemini":1,"Crucible/Cephid_17":1}
def AddBasesToSystem (faction,sys):
    if (sys in doNotAddBasesTo):
        return
    slash = sys.find("/")
    if (slash!= -1):
        if (sys[0:slash] in doNotAddBasesTo):
            return
    if faction in faction_ships.factions:
        fsfac= list(faction_ships.factions).index(faction)
        numbases=0
#               numplanets=VS.GetGalaxyProperty(sys,"num_planets");
        numjumppoints=VS.GetNumAdjacentSystems(sys);
        if (numjumppoints<4):
            if (vsrandom.random()>=.25):
                numbases=1
        elif (vsrandom.random()>=.005):
            if (numjumppoints<7):
                numbases=vsrandom.randrange(1,int(numjumppoints/2)+1)
            elif numjumppoints==7:
                numbases=vsrandom.randrange(1,6)
            else:
                numbases=vsrandom.randrange(1,numjumppoints+1)
        if numbases==0:
            return
        shiplist=[]
        nums=[]
        for i in range(numbases):
            whichbase = faction_ships.bases[fsfac][vsrandom.randrange(0,len(faction_ships.bases[fsfac]))]
            if whichbase in shiplist:
                nums[shiplist.index(whichbase)]+=1
            else:
                shiplist.append(whichbase)
                nums.append(1)
        tn =[]
        for i in range (len(shiplist)):
            tn+=[ (shiplist[i],nums[i])]
        fg_util.AddShipsToFG(fg_util.BaseFGInSystemName (sys),faction,tn,sys)

numericalfaction=0

def GetNewFGName(faction):
    factionnr=faction_ships.factionToInt(faction)
    global numericalfaction
    if(factionnr>=len(fgnames)):
        print "Faction "+faction+" unable to create fgname"

        numericalfaction+=1
        return "Alpha_"+str(numericalfaction)
    if (not len(fgnames[factionnr])):
        fgnames[factionnr]=fg_util.TweakFGNames(origfgnames[factionnr])
        fg_util.origfgoffset+=1
    k=vsrandom.randrange(0,len(fgnames[factionnr])); #pop returns item inside array
    fgname=fgnames[factionnr][k]
    del fgnames[factionnr][k]
    return fgname
def AddSysDict (cursys):
    #pick random fighter from insysenemies with .3 probability OR pick one from the friendlies list.
#       print 'Addsysdict'
    sysfaction=VS.GetGalaxyFaction(cursys)
    global fgnames, fglists
    i=0
    AddBasesToSystem(sysfaction, cursys)
    for i in range (1+vsrandom.randrange(fg_util.MinNumFlightgroupsInSystem(cursys)-1,fg_util.MaxNumFlightgroupsInSystem(cursys))): #number of fgs in a system.
        faction=sysfaction
        friendly=0
        if vsrandom.random()<.3 or sysfaction=='unknown' or sysfaction=='':
            faction=faction_ships.get_rabble_of(sysfaction)
        else:            
            faction=faction_ships.get_friend_of(sysfaction)
            if (faction==sysfaction):
                friendly=1
            if (sysfaction in faction_ships.production_centers):
                if (cursys in faction_ships.production_centers[sysfaction]):
                    friendly=2
            #if (friendly):
            #    print faction+" "+sysfaction+" "+cursys
        factionnr=faction_ships.factionToInt(faction)
        global maxshipsinfg
        typenumbertuple=GenerateFgShips(vsrandom.randrange(maxshipsinfg)+1,factionnr,friendly)
        fgname=GetNewFGName(faction)
        fg_util.AddShipsToFG (fgname,faction,typenumbertuple,cursys)
    return i

def ForEachSys (functio):
    debug.debug("Getting reachable systems...")
    systems = AllSystems()
    debug.debug("done")
    for sys in systems:
	functio(sys)
    return len(systems)
def MakeUniverse():
    # fg_util.DeleteAllFGFromAllSystems()
    ForEachSys(AddSysDict)

systemcount={None:0}
def getSystemCount(fac=None):
    global systemcount
    return systemcount[fac]
def CountSystems(sys):
    fac =VS.GetGalaxyFaction(sys)
    if fac in systemcount:
        systemcount[fac]+=1
    else:
        systemcount[fac]=1
    systemcount[None] += 1
def TakeoverSystem(fac,sys):
    systemcount[VS.GetGalaxyFaction(sys)]-=1
    VS.SetGalaxyFaction(sys,fac)
    systemcount[fac]+=1
    AddBasesToSystem(fac,sys)

hasUniverse=False

genUniverse=-1
def ReloadUniverse():
  global genUniverse, hasUniverse
  if cp>=0:
    debug.debug('Purging...')
    for i in fg_util.AllFactions():
        fg_util.PurgeZeroShips(i)
        systemcount[i]=0
    debug.debug('StartSystemCount')
    ForEachSys(CountSystems)
    debug.debug(systemcount)
    debug.debug('EndSystemCount')
    genUniverse=0
    curfaclist = fg_util.AllFactions()
    reflist = fg_util.ReadStringList(cp,"FactionRefList")
    if (reflist !=curfaclist):
        debug.debug('reflist is '+str(reflist))
        debug.debug('curfaclist is '+str(curfaclist))

        fg_util.WriteStringList(cp,"FactionRefList",curfaclist)
        debug.debug('generating ships... ... ...')
        GenerateAllShips() ###Insert number of flight groups and max ships per fg
        debug.debug('placing ships... ... ...')
        genUniverse=MakeUniverse()
        #now every system has distributed ships in the save data!
    else:
        GenerateAllShips()
        debug.debug("Second Load")
        for i in range(len(fgnames)):
            fgnames[i]=fg_util.TweakFGNames(origfgnames[i])
        fg_util.origfgoffset+=1
    campaigns.loadAll(cp)
    hasUniverse=True;
    #TODO: add ships to current system (for both modes)  uru?
  else:
    debug.error('fatal error: no cockpit')

def KeepUniverseGenerated():
    if VS.networked():
        dj_lib.enable()
        #debug.debug('Not generating dyn universe: Networked game')
        return False
    
    sys = VS.getSystemFile()
    if not VS.GetNumAdjacentSystems(sys):
        #debug.debug('Not generating dyn universe: System has no jumps or is not in Universe XML.')
        return False
    
    dj_lib.enable()
    #curfaclist = fg_util.AllFactions()
    #reflist = fg_util.ReadStringList(cp,"FactionRefList")
    #if (reflist == curfaclist):
    #    debug.debug('Generating dyn universe!');
    if not hasUniverse:
        ReloadUniverse()
        return True
    return False
