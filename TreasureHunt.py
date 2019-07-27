# coding: utf-8
# Kids Treasure
# Simple GPS & speech based treasure quest
# Wors offline, no user acount needed
# Editor included with sharing feature
# coded straight from my iPhone, 
# Thanks Pythonista !!!
# Feel free to improve !
# Enjoy !
# Emmanuel ICART
# eicart@momorprods.com
import ui
import Image
import location
import motion
import time
import photos
import sound
import speech
import console
from io import BytesIO
from io import *
from scene import *
from math import *
import os
import zipfile
import shutil
import appex
import configparser
import base64
import io

# global vars

# How far should the player be from the hint to trigger question (in meters)
HintMinimalDistance=5.0

AdventureFolder="default"
isEditor=False
mustSave=False              
CurrentPosition=(0.0,0.0)
CurrentHintID=0
hintImage = 'Image'
photoImage=Image.new('RGBA',(640,960)) # defines stored photo images size in pixels
gameState=0 # 0=searching, 1=hint, 2=congrats
gameAnswerIsCorrect=True 
gameScore=0

# hint structure
HINT_LONGITUDE=0
HINT_LATITUDE=1
HINT_QUESTION=2
HINT_ANSWER_RED=3
HINT_ANSWER_GREEN=4
HINT_ANSWER_BLUE=5
HINT_ANSWER_YELLOW=6
HINT_ANSWER_ID=7
CurrentHint = [
               0.0, # lon
               0.0, # lat
               'question', # question
               'answerRed', # red answer
               'answerGreen', # green answer
               'answerBlue', # blue answer
               'answerYellow', # yellow answer
               0 # correct answer ID
               ]

# Hint data
Hint=[]
Hint.append(CurrentHint)
Language=""
langList=[]
AdventureDescription=""
AdventureEndMessage=""
AdventureAuthor=""

def getuniquename(filename, ext):
	root, extension = os.path.splitext(filename)
	if ext!='':
		extension = ext
		filename = root + extension
		filenum = 1
		while os.path.isfile(filename):
			filename = '{} {}{}'.format(root, filenum, extension)
			filenum += 1
	return filename

def recurseDeleteFolder(top):
	for root, dirs, files in os.walk(top, topdown=False):
		for name in files:
			print("deleting file "+os.path.join(root, name))
			os.remove(os.path.join(root, name))
			for name in dirs:
				print("deleting folder:"+os.path.join(root, name))
				os.rmdir(os.path.join(root, name))
	os.rmdir(top)

##### Data loading & saving
def saveAdventure():
	global Hint
	global AdventureFolder
	global Language
	global AdventureDescription
	global AdventureEndMessage
	global AdventureAuthor
	if not os.path.exists(AdventureFolder):
		os.mkdir(AdventureFolder)
	
	config = configparser.RawConfigParser()
	config.add_section('General')
	config.set('General','language',Language)
	config.set('General','numberOfHints',len(Hint))
	
	for i in range(len(Hint)):
		section='Hint '+str(i)
		config.add_section(section)
		
		config.set(section,"long",Hint[i][HINT_LONGITUDE])
		
		config.set(section,"lat",Hint[i][HINT_LATITUDE])
		config.set(section,'question',base64.b64encode(bytes(Hint[i][HINT_QUESTION],'utf-8')).decode('utf-8'))
		config.set(section,'answerRed',base64.b64encode(bytes(Hint[i][HINT_ANSWER_RED],'utf-8')).decode('utf-8'))
		config.set(section,'answerGreen',base64.b64encode(bytes(Hint[i][HINT_ANSWER_GREEN],'utf-8')).decode('utf-8'))
		config.set(section,'answerBlue',base64.b64encode(bytes(Hint[i][HINT_ANSWER_BLUE],'utf-8')).decode('utf-8'))
		config.set(section,'answerYellow',base64.b64encode(bytes(Hint[i][HINT_ANSWER_YELLOW],'utf-8')).decode('utf-8'))
		
		config.set(section,"answerId",Hint[i][HINT_ANSWER_ID])	
		
	config.set('General', 'AdventureDescription', base64.b64encode(bytes(AdventureDescription,'utf-8')).decode('utf-8'))
	
	config.set('General', 'AdventureEndMessage', base64.b64encode(bytes(AdventureEndMessage,'utf-8')).decode('utf-8'))

	config.set('General', 'AdventureAuthor', base64.b64encode(bytes(AdventureAuthor,'utf-8')).decode('utf-8'))
				
	# save to file
	cfgFile = open(AdventureFolder+'/Definition.txt','w')
	config.write(cfgFile)
	cfgFile.close()
		
	
def loadAdventure():
	global Hint
	global CurrentHintID
	global CurrentHint
	global AdventureFolder
	global Language
	global AdventureDescription
	global AdventureEndMessage
	global AdventureAuthor
	
	
	try:
		config = configparser.RawConfigParser()
		config.read(AdventureFolder+'/Definition.txt')

		Language=config.get('General',"language")
		AdventureDescription=base64.b64decode(config.get('General','AdventureDescription')).decode('utf-8')
		
		AdventureAuthor=base64.b64decode(config.get('General','AdventureAuthor')).decode('utf-8')
		
		AdventureEndMessage=base64.b64decode(config.get('General','AdventureEndMessage')).decode('utf-8')
		nbHints=config.getint('General','numberOfHints')
		
		Hint=[]
		# load all scenes
		for i in range(nbHints):
			section='Hint '+str(i)
			
			long=config.getfloat(section,"long")
		
			lat=config.getfloat(section,"lat")
			question=base64.b64decode(config.get(section,'question')).decode('utf-8')
			answerRed=base64.b64decode(config.get(section,'answerRed')).decode('utf-8')
			answerGreen=base64.b64decode(config.get(section,'answerGreen')).decode('utf-8')
			answerBlue=base64.b64decode(config.get(section,'answerBlue')).decode('utf-8')
			answerYellow=base64.b64decode(config.get(section,'answerYellow')).decode('utf-8')
			answerId=config.getint(section,"answerId")
			h=[long,lat,question,answerRed,answerGreen,answerBlue,answerYellow,answerId]
			Hint.append(h)	
	except:
		Hint=[]
		Hint.append(CurrentHint)
		
	# end of loading
	if Hint==None:
		Hint=[]
		Hint.append(CurrentHint)
	if not Hint==None:
		CurrentHint=Hint[CurrentHintID]
		
##### Helper GPS function
# thanks to Chris Veness
# http://www.movable-type.co.uk/scripts/latlong.html
def getDistanceAndDirection(lon1,lat1,lon2,lat2):
	lon1, lat1, lon2, lat2 = list(map(radians, [lon1, lat1, lon2, lat2]))
	# haversine formula
	dlon = lon2 - lon1
	dlat = lat2 - lat1
	R = 6371
	a = sin(dlat/2) * sin(dlat/2) + cos(lat1) * cos(lat2) * sin(dlon/2) * sin(dlon/2)
	c = 2 * atan2(sqrt(a), sqrt(1-a))
	distance = R * c
	
	#Horizontal Bearing
	y = sin(dlon) * cos(lat2)
	x = cos(lat1)*sin(lat2) -sin(lat1)*cos(lat2)*cos(dlon)
	Bearing = degrees(atan2(y, x))
	
	#Output the data
	return distance*1000, Bearing

def say(text):
	global Language
	speech.stop()
	speech.say(text,Language)

@ui.in_background	
def sayHint():
	global CurrentHint
	# spoken text
	tts=CurrentHint[HINT_QUESTION]+'--'
	tts=tts+CurrentHint[HINT_ANSWER_YELLOW]+'.--'
	tts=tts+CurrentHint[HINT_ANSWER_BLUE]+'.--'
	tts=tts+CurrentHint[HINT_ANSWER_GREEN]+'.--'
	tts=tts+CurrentHint[HINT_ANSWER_RED]+'.--'
	say(tts)
	
	# popup text
	tts=CurrentHint[HINT_QUESTION]+'\n\n'
	tts=tts+CurrentHint[HINT_ANSWER_YELLOW]+'\n'
	tts=tts+CurrentHint[HINT_ANSWER_BLUE]+'\n'
	tts=tts+CurrentHint[HINT_ANSWER_GREEN]+'\n'
	tts=tts+CurrentHint[HINT_ANSWER_RED]
	console.alert(tts,'','OK',hide_cancel_button=True)
	
def human_format(num):
	num = float('{:.3g}'.format(num))
	magnitude = 0
	while abs(num) >= 1000:
		magnitude += 1
		num /= 1000.0
		return '{}{}'.format('{:f}'.format(num).rstrip('0').rstrip('.'), ['', ' K', ' M', ' B', ' T'][magnitude])
	return str(num)
    
def loadCurrentGameHint():
	global CurrentPosition
	global Hint
	global CurrentHintID
	global CurrentHint
	global hintImage
	global photoImage
	CurrentHint=Hint[CurrentHintID]
	filename=AdventureFolder+'/photo_hint_'+str(CurrentHintID)+'.jpg'
	if os.path.exists(filename):
		photoImage = Image.open(filename)
		photoImage=photoImage.convert('RGBA')
		hintImage=load_pil_image(photoImage)
	
##### Radar scene
class GPSViewCore (Scene):
	
	lastBipTimer=0.0
	lastTouchTimer=0
	def setup(self):
		global CurrentPosition
		global Hint
		global CurrentHintID
		global CurrentHint
		global hintImage
		global photoImage
		global gameState
		# This will be called before the first frame is drawn.
		sound.load_effect('8ve-beep-hightone')
		if not isEditor:loadCurrentGameHint()
		pass
		
	def launchEditor(self):
		global isEditor
		KillGPSView()
		isEditor=True 
		CreateGPSView()
		refreshEditorItems(True )
		
	def draw(self):
		global CurrentPosition
		global Hint
		global CurrentHintID
		global CurrentHint
		global hintImage
		global photoImage
		global gameState
		global gameScore
		global HintMinimalDistance
		global AdventureEndMessage
		
		screen_x=self.bounds[0]
		screen_y=self.bounds[1]
		screen_width=self.bounds[2]
		screen_height=self.bounds[3]
		screen_centerx=screen_x+(screen_width/2)
		screen_centery=screen_y+(screen_height/2)
		# This will be called for every frame (typically 60 times per second).
			
		loc = location.get_location()
		CurrentPosition = (loc['longitude'],loc['latitude'],loc['altitude'])
		
		distance, orientation = getDistanceAndDirection(CurrentPosition[0], CurrentPosition[1], CurrentHint[HINT_LONGITUDE],CurrentHint[HINT_LATITUDE])
		
		if isEditor:
			g['CurrentPosLon'].text=str(round(CurrentPosition[0],9))
			g['CurrentPosLat'].text=str(round(CurrentPosition[1],9))
			g['CurrentPosAlt'].text='Alt: '+str(round(CurrentPosition[2],0))+' m'
			return 
			
		comp = motion.get_attitude()
		
		############### congrats mode
		if gameState==2:
			gameView.hidden=True 
			background(0, 0, 0)
			tint(0,1,0)
			text('Congratulations!',font_name='AppleSDGothicNeo-Bold',font_size=35,x=screen_centerx,y=screen_centery+125)
			
			text('SCORE: '+str(gameScore),font_name='AppleSDGothicNeo-Bold',font_size=35,x=screen_centerx,y=screen_centery)
			
			text('Touch screen to play again',font_name='AppleSDGothicNeo-Bold',font_size=17,x=screen_centerx,y=screen_centery-125)
			
			if CurrentHintID>=len(Hint):
				CurrentHintID=0
				say(AdventureEndMessage)
				console.alert(AdventureEndMessage,'','OK',hide_cancel_button=True)
			
		############### hint mode
		if gameState==1:
			gameView.hidden=False 
			# display hint --------
			tint(1,1,1)
			background(0, 0, 0)
			hi=photoImage.height*screen_width/photoImage.width
			wi=screen_width
			image(hintImage, screen_centerx-0.5*wi,screen_centery-0.5*hi,wi,hi)			
		
		############### search mode 
		if gameState==0:
			# check next game state ?
			if distance<HintMinimalDistance:
				gameState=1
				sayHint()
				
			# display
			gameView.hidden=True
			angle=radians(-orientation)-comp[2]-1.0*3.14159
			
			# computes angle between north direction and target bearing
			angle=-(comp[2]-radians(-orientation))-0.5*3.14159
			
			c=cos(angle+3.14159)
			s=sin(angle+3.14159)
			
			# compute compass vertices
			w=128/2
			h=-128/2
			
			x1=screen_centerx+(-w)*c - (-h)*s
			y1=screen_centery+(-w)*s + (-h)*c
			x2=screen_centerx+(w)*c - (-h)*s
			y2=screen_centery+(w)*s + (-h)*c
			x3=screen_centerx+(w)*c - (h)*s
			y3=screen_centery+(w)*s + (h)*c
			x4=screen_centerx+(-w)*c - (h)*s
			y4=screen_centery+(-w)*s + (h)*c
			
			# display radar --------
			background(0, 0, 0)
			stroke(0,0.8,0)
			stroke_weight(1)
			fill(0,0.4,0,0.3)
			for i in range(0,8):
				ellipse(screen_centerx-i*30,screen_centery-i*30,i*60,i*60)
			
			line(screen_centerx,0,screen_centerx,screen_height)
			line(0,screen_centery,screen_width,screen_centery)
			# display compass
			stroke(0.2,1,0.2)
			stroke_weight(3)
			line(screen_centerx,screen_centery,x2,y2)
			line(screen_centerx,screen_centery,x1,y1)
			line(x1,y1,screen_centerx+100*s,screen_centery-100*c)
			line(x2,y2,screen_centerx+100*s,screen_centery-100*c)
			
			tint(0,1,0)
			
			distanceFormatted=human_format(round(distance))+'m'
			text(distanceFormatted,font_size=9,x=screen_width-25,y=5)
			
			# distance bar
			fill(0,1,0,0.5)
			stroke_weight(0)
			coef=(distance/200)
			if coef<0:coef=0
			if coef>1:coef=1
			coeftime=0.5+2.5*coef
			rect(screen_width-40,10,30,(1-coef)*(screen_height-20))
	
			if time.time()-self.lastBipTimer>coeftime:
				self.lastBipTimer=time.time()
				sound.play_effect('8ve-beep-hightone',1.0)
			
			fill(0,1,0,0.0)
			stroke(0,1,0)
			stroke_weight(1)
			rect(screen_width-40,10,30,screen_height-20)
			# score
			tint(0,1,0)
			text('SCORE: '+str(gameScore),font_name='AppleSDGothicNeo-Bold',font_size=15,x=screen_centerx,y=screen_height-15)
			text('Indice '+str(CurrentHintID+1) + ' / ' +str(len(Hint)),font_name='AppleSDGothicNeo-Bold',font_size=15,x=screen_centerx,y=10)
			##### end of gameState==0
	
	def touch_began(self, touch):
		self.lastTouchTimer=time.time()
		pass
	
	def touch_moved(self, touch):
		pass

	def touch_ended(self, touch):
		global gameState
		global CurrentHintID
		global gameScore
		
		# restart game if correct state
		if gameState==2:
			sound.play_effect('Ding_3')
			CurrentHintID=0
			gameScore=0
			loadCurrentGameHint()
			gameState=0
		pass

@ui.in_background
def CreateGPSView():
	v['gps'].hidden=not isEditor
	gps = GPSViewCore()
	gps2 = SceneView()
	gps2.scene = gps
	gps2.paused=False 
	gps2.name='gps2'
	gps2.bounds = v['gps'].bounds
	gps2.center = v['gps'].center
	gps2.width = v['gps'].width
	gps2.height = v['gps'].height
	
	if isEditor:
		gps2.width=0
		gps2.height=0
	gps2.touch_enabled=True 
	gps2.bring_to_front()
	v.add_subview(gps2)

def KillGPSView(): 
	gg=v['gps2']
	if gg:
		gg.scene.stop()
		v.remove_subview(gg)
		del(gg)
	
	

#### UI events -----------------------
def gameAnswerSelect(sender):
	global CurrentHint
	global CurrentHintID
	global gameAnswerIsCorrect
	global gameState
	global gameScore
	currentAnswerID=-1
	if sender.name=='redButton': currentAnswerID=0
	if sender.name=='greenButton': currentAnswerID=1
	if sender.name=='blueButton': currentAnswerID=2
	if sender.name=='yellowButton': currentAnswerID=3
	
	if currentAnswerID==CurrentHint[HINT_ANSWER_ID]:
		gameAnswerIsCorrect=True 
		sound.play_effect('Ding_3',1.0)
		gameScore=gameScore+1
		say('Bonne réponse,-- tu gagnes 1 point.--Recherche l''indice suivant !')
	else:
		gameAnswerIsCorrect=False  
		sound.play_effect('Error',1.0)
		say('Mauvaise réponse.-- Recherche l''indice suivant !')
	gameState=0
	CurrentHintID=CurrentHintID+1
	if CurrentHintID>=len(Hint):
		gameState=2
		return 
	loadCurrentGameHint()

def refreshEditorItems(doLoadImage=False):
	global Hint
	global CurrentHintID
	global CurrentHint
	global settings
	global langList
	global Language
	global AdventureEndMessage
	global AdventureAuthor
	global AdventureDescription
	gameView.hidden=isEditor
	
	langid=-1
	for i in range(len(langList)):
		if langList[i][0]==Language:
			langid=i
	settings['languageTableView'].selected_row=(0,langid)
	
	settings['AuthorText'].text=AdventureAuthor
	settings['DescriptionTextView'].text=AdventureDescription
	
	settings['EndOfGameTextView'].text=AdventureEndMessage
	
	v['AdventureNameLabel'].text=AdventureFolder
	
	g['HintID'].text='HINT '+str(CurrentHintID+1)+'/'+str(len(Hint))
	g['HintLon'].text=str(round(CurrentHint[HINT_LONGITUDE],9))
	g['HintLat'].text=str(round(CurrentHint[HINT_LATITUDE],9))
	g['HintText'].text=CurrentHint[HINT_QUESTION]
	g['HintYellowText'].text=CurrentHint[HINT_ANSWER_YELLOW]
	g['HintRedText'].text=CurrentHint[HINT_ANSWER_RED]
	g['HintGreenText'].text=CurrentHint[HINT_ANSWER_GREEN]
	g['HintBlueText'].text=CurrentHint[HINT_ANSWER_BLUE]
	g['HintAnswer'].selected_index=CurrentHint[HINT_ANSWER_ID]
	if doLoadImage:
		filename=AdventureFolder+'/photo_hint_'+str(CurrentHintID)+'.jpg'
		if os.path.exists(filename):
			img2 = Image.open(filename)
			# convert the Image to PNG string
			img_buf = BytesIO()
			img2.save(img_buf,'jpeg')
			img=img_buf.getvalue()
			g['photoview'].image=ui.Image.from_data(img)
			g['photoview'].height = (g['photoview'].width * img2.height)/img2.width

def refreshValues(sender):
	global Hint
	global CurrentHintID
	global CurrentHint
	global mustSave
	mustSave=True
	# set current hint values
	CurrentHint[HINT_QUESTION]=g['HintText'].text
	CurrentHint[HINT_ANSWER_YELLOW]=g['HintYellowText'].text
	CurrentHint[HINT_ANSWER_RED]=g['HintRedText'].text
	CurrentHint[HINT_ANSWER_GREEN]=g['HintGreenText'].text
	CurrentHint[HINT_ANSWER_BLUE]=g['HintBlueText'].text
	CurrentHint[HINT_ANSWER_ID]=g['HintAnswer'].selected_index
	# set to the hints array
	Hint[CurrentHintID]=CurrentHint

def saveFile(sender):
	global mustSave
	sound.play_effect('digital:ThreeTone2')
	refreshValues(sender)
	saveAdventure()
	mustSave=False
	
def openSettings(sender):
	global settings
	global isEditor
	
	if not settings.on_screen:
		settings.present(style='full_screen_',hide_title_bar=False,orientations=['portrait'])
	refreshValues(sender)
	
def prevHintButton(sender):
	global Hint
	global CurrentHintID
	global CurrentHint
	sound.play_effect('ui:click1')
	refreshValues(sender)
	CurrentHintID=CurrentHintID-1
	if CurrentHintID<0:CurrentHintID=0
	CurrentHint=Hint[CurrentHintID]
	refreshEditorItems(True)

def nextHintButton(sender):
	global Hint
	global CurrentHintID
	global CurrentHint
	sound.play_effect('ui:click1')
	refreshValues(sender)
	CurrentHintID=CurrentHintID+1
	if CurrentHintID>=len(Hint)-1:CurrentHintID=len(Hint)-1
	CurrentHint=Hint[CurrentHintID]
	refreshEditorItems(True)
	
def addHintButton(sender):
	global Hint
	global CurrentHintID
	global CurrentHint
	global mustSave
	mustSave=True
	sound.play_effect('casino:CardPlace1')
	hintToAdd=[
               0.0, # lon
               0.0, # lat
               'question', # question
               'answerRed', # red answer
               'answerGreen', # green answer
               'answerBlue', # blue answer
               'answerYellow', # yellow answer
               0 # correct answer ID
               ]
	Hint.insert(CurrentHintID+1,hintToAdd)
	CurrentHintID=CurrentHintID+1
	CurrentHint=Hint[CurrentHintID]
	refreshEditorItems(True)

def removeHintButton(sender):
	global CurrentHint
	global Hint
	global CurrentHintID
	sound.play_effect('game:Error')
	result = console.alert("Delete Hint ?", "Do you confirm you want to delete this hint ?", "Yes", "No", hide_cancel_button=True)
	if result==2:
		return
		
	Hint.pop(CurrentHintID)
	if CurrentHintID>len(Hint)-1:CurrentHintID=len(Hint)-1
	CurrentHint=Hint[CurrentHintID]
	refreshEditorItems(True )
	
def setTargetButton(sender):
	global Hint
	global CurrentHintID
	global CurrentHint
	global mustSave
	loc=location.get_location()
	CurrentHint[HINT_LONGITUDE]=loc['longitude']
	CurrentHint[HINT_LATITUDE]=loc['latitude']
	sound.play_effect('ui:click1',1.0)
	mustSave=True
	
	refreshEditorItems()

def triggerMustSave(sender):
	global mustSave
	mustSave=True

def testHintButton(sender):
	tts=sender.superview['HintText'].text+'--'
	tts=tts+sender.superview['HintYellowText'].text+'.--'
	tts=tts+sender.superview['HintBlueText'].text+'.--'
	tts=tts+sender.superview['HintGreenText'].text+'.--'
	tts=tts+sender.superview['HintRedText'].text+'.--'
	say(tts)
	
def repeatHint(sender):
	sayHint()

@ui.in_background
def pickImageButton(sender):
	global Hint
	global CurrentHintID
	global CurrentHint
	global photoImage
	global mustSave
	KillGPSView()
	
	listPhotos=photos.get_assets('image')
	
	imageAsset = photos.pick_asset(listPhotos, title='Pick some assets', multi=False)
	
	if not imageAsset:
		return
		
	if imageAsset.location!=None:
		CurrentHint[HINT_LONGITUDE]=imageAsset.location['longitude']
		CurrentHint[HINT_LATITUDE]=imageAsset.location['latitude']
	else:
		console.alert('Warning','This photo has no location information, unable to set GPS coordinates.','OK',hide_cancel_button=True)
	
	
	wi=photoImage.width
	hi=(int)(wi*imageAsset.pixel_height/imageAsset.pixel_width)
	
	imgUI=imageAsset.get_ui_image((wi,hi))
	
	pngdata=imgUI.to_png()

	image=Image.open(io.BytesIO(pngdata))
	
	CreateGPSView()
	img2 = image.resize((wi,hi),Image.ANTIALIAS)
	img2.save(AdventureFolder+'/photo_hint_'+str(CurrentHintID)+'.jpg','jpeg')
	# convert the Image to PNG string
	img_buf = BytesIO()
	img2.save(img_buf,'jpeg')
	img=img_buf.getvalue()
	sender.superview['photoview'].image=ui.Image.from_data(img)
	
	mustSave=True
	refreshEditorItems(True)
	
@ui.in_background
def photoButton(sender):
	global Hint
	global CurrentHintID
	global CurrentHint
	global photoImage
	global mustSave
	KillGPSView()
	
	image = photos.capture_image()
	
	mustSave=True
	
	CreateGPSView()
	wi=photoImage.width
	hi=(int)(photoImage.width*image.height/image.width)

	img2 = image.resize((wi,hi),Image.ANTIALIAS)
	img2.save(AdventureFolder+'/photo_hint_'+str(CurrentHintID)+'.jpg','jpeg')
	# convert the Image to PNG string
	img_buf = BytesIO()
	img2.save(img_buf,'jpeg')
	img=img_buf.getvalue()
	sender.superview['photoview'].image=ui.Image.from_data(img)
	refreshEditorItems(True)
	
def selectFolderAction(sender):
	print ("selected:"+sender.selected_row)
	
def fillFolderPopupValues():
	global filePopupDialog
	templateA = ['aaa','bbb']
	
	adventures=[]
	
	for entry in os.scandir("./"):
		if not entry.name.startswith('.') and not entry.is_file():
			adventures.append(entry.name)
					
	tv = filePopupDialog['folderListUI']
	
	tv.data_source = ui.ListDataSource(templateA)
	tv.data_source.items=adventures
	tv.action=selectFolderAction
	
	tv.data_source.delete_enabled=False
	tv.reload_data()

	
def onAdventureCreate(sender):
	global filePopupDialog
	global AdventureFolder
	global Hint
	global selectedAdventureId
	
	tv = filePopupDialog['folderListUI']
	
	name=console.input_alert("Create Adventure","Please enter the adventure name", "", "OK")
	
	name=name.replace("/","")
	name=name.replace(".","")
	name=name.replace(" ","")
	
	res=False
	if name!="":
		if not os.path.exists(name):
			try:
				os.mkdir(name)
				res=True
			except:
				console.alert("Please enter a valid name")
	if res:
		console.alert("Adventure created!","","Ok",hide_cancel_button=True)
		
		AdventureFolder=name
		Hint=[]
		hintToAdd=[
			0.0, # lon
			0.0, # lat
			'question', # question
			'answerRed', # red answer
			'answerGreen', # green answer
			'answerBlue', # blue answer
			'answerYellow', # yellow answer
			0 # correct answer ID
			]
		Hint.append(hintToAdd)
		saveAdventure()
		launchEditorScreen()
	
	
def onAdventurePlay(sender):
	global filePopupDialog
	global AdventureFolder
	global Hint
	global selectedAdventureId
	
	tv = filePopupDialog['folderListUI']
	if len(tv.selected_rows)==0:
		return
	
	id=tv.selected_row[1]
	AdventureFolder=tv.data_source.items[id]
	launchGameScreen()
	
def onAdventureEdit(sender):
	global filePopupDialog
	global AdventureFolder
	global Hint
	global selectedAdventureId
	
	tv = filePopupDialog['folderListUI']
	if len(tv.selected_rows)==0:
		return
	
	id=tv.selected_row[1]
	AdventureFolder=tv.data_source.items[id]
	launchEditorScreen()

@ui.in_background
def onBackToTitle(sender):
	global mustSave
	if mustSave:
		id=console.alert('Warning','Un-saved modifications detected, do you want to save them?','Yes','No',hide_cancel_button=True)
		if id==1:
			saveAdventure()
	mustSave=False
	launchTitleScreen()
	
@ui.in_background
def onDeleteAdventureAction(sender):
	global AdventureFolder
	sound.play_effect('game:Error')
	
	result = console.alert("Delete Adventure ?", "Do you confirm you want to delete this Adventure ?\nYou won't be able to recover it after this action !", "Yes", "No", hide_cancel_button=True)
	
	if result==2:
		return
		
	print("deleting adventure : "+AdventureFolder)
	
	recurseDeleteFolder(AdventureFolder)
	launchTitleScreen()
	
@ui.in_background	
def onShareButton(sender):
	global AdventureFolder
	global mustSave
	if mustSave:
		id=console.alert('Warning','Un-saved modifications detected, do you want to save them?','Yes','No',hide_cancel_button=True)
		if id==1:
			saveAdventure()
	mustSave=False
	make_zipfile("./"+AdventureFolder+".thz","./"+AdventureFolder+"/")
	console.open_in(AdventureFolder+".thz")
	
@ui.in_background
def launchGameScreen():
	global filePopupDialog
	global v
	global isEditor
	global CurrentHintID
	global gameState
	global AdventureDescription
	global AdventureAuthor
	
	loadAdventure()
	filePopupDialog.close()
	filePopupDialog.wait_modal()
	KillGPSView()
	isEditor=False
	CurrentHintID=0
	gameState=0
	CreateGPSView()
	refreshEditorItems(False )
	loadCurrentGameHint()
	if not v.on_screen:
		v.present(style='full_screen_',hide_title_bar=True,orientations=['portrait'])
		
		say(AdventureDescription)
		console.alert(AdventureDescription,'\n'+AdventureAuthor,'OK',hide_cancel_button=True)
		say('')
	

def launchEditorScreen():
	global filePopupDialog
	global v
	global isEditor
	
	loadAdventure()
	filePopupDialog.close()
	filePopupDialog.wait_modal()
	KillGPSView()
	isEditor=True
	CreateGPSView()
	refreshEditorItems(True)
	
	if not v.on_screen:
		v.present(style='full_screen_',hide_title_bar=True,orientations=['portrait'])
	
	
def launchTitleScreen():
	global filePopupDialog
	global v
	global isEditor
	v.close()
	v.wait_modal()
	fillFolderPopupValues()
	if not filePopupDialog.on_screen:
		filePopupDialog.present(style='full_screen_',hide_title_bar=True,orientations=['portrait'])
		

		
def decompress_zipfile(filename,location):
	if (os.path.exists(location)) and not (os.path.isdir(location)):
		print ("unzip: %s: destination is not a directory" % location)
		return False
	elif not os.path.exists(location):
		os.makedirs(location)
	
	zipfp = open(filename, 'rb')
	try:
		zipf = zipfile.ZipFile(zipfp)
		for name in zipf.namelist():
			data = zipf.read(name)
			fn = name
			fn = fn.lstrip('/')
			fn = os.path.join(location, fn)
			print(fn)
			if fn.endswith('/'):
				# A directory
				if not os.path.exists(fn):
					os.makedirs(fn)
			else:
				fp = open(fn, 'wb')
				try:
					fp.write(data)
				finally:
					fp.close()
	except Exception:
						zipfp.close()
						print("unzip: %s: zip file is corrupt" % filename)
						return False
	finally:
		zipfp.close()
	return True
						
										
def make_zipfile(output_filename, source_dir):
	relroot = os.path.abspath(os.path.join(source_dir, os.pardir))+"/"+source_dir
	#print("relroot:"+relroot)
	with zipfile.ZipFile(output_filename, "w", zipfile.ZIP_DEFLATED) as zip:
		for root, dirs, files in os.walk(source_dir,topdown=True):
			path_element=os.path.relpath(root,source_dir)
			#print("Adding {pe}".format(pe=path_element))
			zip.write(root, os.path.relpath(root, relroot))
			for file in files:
				filename = os.path.join(root, file)
				if os.path.isfile(filename):
					#print(filename+":"+file)
					arcname = os.path.join(os.path.relpath(root, relroot), file)
					zip.write(filename, arcname)


def languageSelected(sender):
	global settings
	global langList
	global Language
	global mustSave
	
	mustSave=True
	Language=langList[settings['languageTableView'].selected_row[1]][0]
	
def authorEdit(sender):
	global AdventureAuthor
	global AdventureEndMessage
	global AdventureDescription
	global settings
	global mustSave
	mustSave=True
	AdventureAuthor=settings['AuthorText'].text
	
# load languages file
def loadLanguagesFile():
	global langList
	global settings
	
	langList=[]
	
	with open('languages.txt', 'r') as f:
		for line in f.readlines():
			langList.append(line.split('       '))
	
	# fill setup view component
	content=[]
	for l in langList:
		content.append(l[1][:-1])
	settings['languageTableView'].data_source.items=content

	
#### delegates for textviews
class AdventureDescTextViewDelegate (object):
    def textview_did_change(self, textview):
    	global AdventureDescription
    	global mustSave
    	AdventureDescription=textview.text
    	mustSave=True

class AdventureEndTextViewDelegate (object):
    def textview_did_change(self, textview):
    	global AdventureEndMessage
    	global mustSave
    	AdventureEndMessage=textview.text
    	mustSave=True

#### Main program ---------------------
selectedAdventureId=-1
# display background splash image
splash = ui.load_view('TreasureSplash')
splash.present(style='full_screen_',hide_title_bar=True,orientations=['portrait'])

# load game views
v = ui.load_view('TreasureHunt') 
g=v['gps']
gameView=v['gameView']

#settings view
settings = ui.load_view('TreasureSetup') 

settings['DescriptionTextView'].delegate=AdventureDescTextViewDelegate()

settings['EndOfGameTextView'].delegate=AdventureEndTextViewDelegate()

filePopupDialog=ui.load_view('TreasureTitle')

setup = ui.load_view('TreasureSetup')

loadLanguagesFile()

def main():
	global splash
	if appex.is_running_extension():
		# copy input file to sandbox folder
		dest_path_short = '~/Documents/inbox'
		dest_path = os.path.expanduser(dest_path_short)
		if not os.path.isdir(dest_path):
			print('Create ' + dest_path_short)
			os.mkdir(dest_path) 
		file = appex.get_file_path() 
		print('Input path: %s' % file)
		if (file==None):
			console.alert("Error","Unable to process the input data. Import failed.","Ok",hide_cancel_button=True)
			appex.finish()
			return
			
		filename=os.path.join(dest_path, os.path.basename(file))
		filename=getuniquename(filename,'')
		shutil.copy(file,filename)
		print('Saved in %s' % dest_path_short)
		if not os.path.exists(filename):
			print(' > Error file %s not found !' % os.path.basename(filename))
		
		# prompt for a new adventure name
		s=os.path.basename(file).replace(".thz","")
		name=console.input_alert("Import Adventure","Please enter the imported adventure name", s, "OK")
		
		name=name.replace("/","")
		name=name.replace(".","")
		name=name.replace(" ","")
	
		res=False
		if name!="":
			if not os.path.exists(name):
				try:
					os.mkdir(name)
					res=True
				except:
					console.alert("Please enter a valid or non-existing name")
		if not res:
			appex.finish()
			return
		# unzip the file	
		decompress_zipfile(filename,"./"+name)
		os.remove(filename)
		
		# check decompressed file integrity : does it include game files ?
		res=True
		if not os.path.exists("./"+name+"/Definition.txt"):
			res=False
		
		if res:
			console.alert("Adventure successfully imported!","","Ok",hide_cancel_button=True)
		else:
			recurseDeleteFolder(name)
			console.alert("File corrupted!","The adventure you tried to import is corrupted, import failed.","Ok",hide_cancel_button=True)
		appex.finish()
	
	# launch game
	
	console.set_idle_timer_disabled(True)
	
	# Get the GPS info.
	location.start_updates()
	
	# Compass
	motion.start_updates()
	launchTitleScreen()


if __name__ == '__main__':
	main()
