#!/usr/bin/python
#LAST MOD: 19th Jan 2016
#****************************************************************************************************
#Author: Domenico De Vivo MEng (Concept2 Ltd) - domdv@concept2.co.uk
#Date: 14 Oct 2014
#Thanks : Sam Gambrell & UVD (PyRow)
#Distributed for free, and for non commercial use. Copyright Domenico De Vivo, please do not copy.
#For more info please open the readme.txt file.
#****************************************************************************************************
import pyrow, math, time, pygame, sys, usb.core, usb.util, os
from pygame.locals import *

#TOP LEVEL CONSTANTS
WINDOWWIDTH=1024; WINDOWHEIGHT=768
GAMETITLE="Concept2 Monitor"
WHITE=[255,255,255]; RED=[255,0,0]; GREEN=[0,255,0]; BLUE=[0,100,255]; BLACK=[0,0,0]; GOLD=[255,215,0]; 
PURPLE=[127,0,255]; ORANGE=[255,128,0]; GREY=[192,192,192]; LTGREY=[216,220,216]

#load all images
splash=pygame.image.load("images/splash_j.jpg")
background=pygame.image.load("images/pi_monitor_bg_b.jpg")
heart=pygame.image.load("images/heart_b.png")
graph=pygame.image.load("images/force_axis_bg_b.png")
plotter_red=pygame.image.load("images/x_plot_red.png")
plotter_green=pygame.image.load("images/x_plot_green.png")
plotter_blue=pygame.image.load("images/x_plot_blue.png")
plotter_yellow=pygame.image.load("images/x_plot_yellow.png")
plotter_black=pygame.image.load("images/x_plot_black.png")

def main():
	
	#INITIAL SETUP
	pygame.init()
	pygame.mouse.set_visible(False)
	displayFont=pygame.font.Font("fonts/digital-7.ttf",180)
	display_smFont=pygame.font.Font("fonts/digital-7.ttf",90)
	titleFont=pygame.font.Font("fonts/256BYTES.TTF",180)
	smallFont=pygame.font.Font("fonts/256BYTES.TTF",70)
	tinyFont=pygame.font.Font("fonts/256BYTES.TTF",30)
	screen = pygame.display.set_mode((WINDOWWIDTH,WINDOWHEIGHT))
	pygame.display.set_caption(GAMETITLE)
	
	ergs = list(pyrow.find())
	if len(ergs) == 0:
		exit("No ergs found.")
	erg = pyrow.pyrow(ergs[0])
	print "Connected to erg."
	
	#SETUP PM VARS
	command = ['CSAFE_PM_GET_WORKDISTANCE']
	cmeters = 0
	pace = 0
	wtime = 0
	srate = 0
	hrate = 0
	wtime_mins = 0 
	wtime_secs = 0
	wtime_tenths = 0
	pace_mins = 0 
	pace_secs = 0
	calhr = 0
	calories = 0
	
	#SPLASH SCREEN
	screen.blit(splash,(0,0))
	connectedText=tinyFont.render('* Monitor Connected',True,GREEN)
	disconnectedText=tinyFont.render('* Monitor Connection Lost - Re-Start!',True,RED)
	quitText=tinyFont.render('Press Esc to Exit',True, BLACK)
	errexitText=smallFont.render('Press Esc to',True, RED)#after error
	errexitText2=smallFont.render('Exit!',True, RED)#after error
	startText=smallFont.render('Press Enter',True,BLACK)
	startText2=smallFont.render('or Row',True,BLACK)
	startText3=smallFont.render('to start',True,BLACK)
	
	pygame.display.update()
	pygame.time.wait(1500)
	screen.blit(connectedText,(1,1))
	screen.blit(quitText,(20,30))
	screen.blit(startText,(610,450))
	screen.blit(startText2,(685,510))
	screen.blit(startText3,(660,560))
	pygame.display.update()
	
	#SETUP GAME AND SCREEN DISPLAY VARS
	game_over=False
	start_game=False
	view=0
	sample=0
	counter=0
	plot_col_picker=0
		
	#SETUP SCREEN DISPLAY LABELS
	split_units="/500m"
	distance_units="m"
	srate_units="s/m"
	cal_hr_units="cal/hr"
	cals_units="cal"
	
	#SETUP VAR LABEL FONTS
	split_unitsText=smallFont.render(split_units,True,GOLD)
	distance_unitsText=smallFont.render(distance_units,True,PURPLE)
	srate_unitsText=smallFont.render(srate_units,True,ORANGE)
	cal_hr_unitsText=smallFont.render(cal_hr_units,True,GOLD)
	cals_unitsText=smallFont.render(cals_units,True,PURPLE)
	
	#SETUP STATIC MENU TEXT FOR ALL VIEWS
	menuText=tinyFont.render("Press 0 = Pace View",True,WHITE)
	menuText2=tinyFont.render("Press 1 = Calorie view",True,WHITE)
	menuText3=tinyFont.render("Press 2 = Force Curve",True,WHITE)
	
	while start_game==False:
		try:
			monitor = erg.get_monitor()
			if monitor['time'] > 0:#if rowing detected start main loop
				start_game=True
		except:#display error msg
			screen.fill(LTGREY,(1,1,300,60))#x,y,w,h
			screen.fill(LTGREY,(600,445,350,200))#x,y,w,h
			screen.blit(disconnectedText,(1,1))
			screen.blit(errexitText,(610,450))
			screen.blit(errexitText2,(720,510))
			pygame.display.update()
				
		for event in pygame.event.get():
			if event.type==pygame.KEYDOWN:
				if event.key==pygame.K_ESCAPE:
					game_over=True
					pygame.quit()
					sys.exit()
				elif event.key==pygame.K_RETURN:
					start_game=True
						
	#MAIN WORKOUT LOOP
	while game_over==False:
		for event in pygame.event.get():
			if event.type==pygame.KEYDOWN:
				if event.key==pygame.K_ESCAPE:
					game_over=True
				elif event.key==pygame.K_2 or event.key==pygame.K_KP2:
					view=2
				elif event.key==pygame.K_1 or event.key==pygame.K_KP1:
					view=1
				elif event.key==pygame.K_0 or event.key==pygame.K_KP0:
					view=0
			if event.type == pygame.QUIT:#pygame window quit 
					game_over=True
					pygame.quit()
					sys.exit()	
						
		monitor = erg.get_monitor()
		#screen = erg.get_screen()
		result = erg.send(command)
		
		#output to terminal
		if view==0 or view==1:
			print "-------------"
			cmeters = result['CSAFE_PM_GET_WORKDISTANCE'][0]/10
			print "Meters = " + str(cmeters)
			
			calhr = monitor['calhr']#pre processed data
			calhr = str(int(math.ceil(calhr)))
			print str(calhr) + " cal/hr"
			
			calories = monitor['calories']
			print str(calories) + " calories"
			
			pace = monitor['pace']
			pace_mins, pace_secs = divmod(pace, 60) #python math function to get mins and secs
			print "%02d:%02d (/500m)" % (pace_mins, pace_secs)
						
			wtime = monitor['time']
			print str(wtime) + " time(secs)"
			wtime_mins, wtime_secs = divmod(wtime, 60)
			wtime_tenths = str(wtime).rsplit('.',1)[1]#split time string to get tenths array pos[1]
			
			if len(wtime_tenths) ==1:#add following zero to exact tenths eg. .60, .70
				wtime_tenths = wtime_tenths + "0"
				
			print wtime_tenths + " tenths"
			print "%02d:%02d" % (wtime_mins, wtime_secs) + " M:S"
			
			srate = monitor['spm']
			print str(srate) + " spm"
			
			hrate = monitor['heartrate']
			print str(hrate) + " bpm"
			
			print "Serial = " + str(monitor['serial'])
			#print "Display = " + str(monitor['display'])
			
		
		if view==2:
			print counter
			power = monitor['power']
			#force plot loop		
			forceplot = erg.get_force_plot()
			#Loop while waiting for drive
			while forceplot['strokestate'] != 2:
				forceplot = erg.get_force_plot()	
		
			#Record force data during the drive
			force = forceplot['forceplot'] #start of pull (when strokestate first changed to 2)
			monitor = erg.get_monitor() #get monitor data for start of stroke
			#Loop during drive
			while forceplot['strokestate'] == 2:
				forceplot = erg.get_force_plot()
				force.extend(forceplot['forceplot'])		
			else: #Get force data from end of stroke
				forceplot = erg.get_force_plot()
				force.extend(forceplot['forceplot'])
			
			forcedata = ",".join([str(f) for f in force])
			print forcedata
			print sample
			print str(power) + "W"


		#output to pygame screen
		if view==0:	
			counter = 0#reset the counter from previous force curve view
			screen.blit(background,(0,0))
			
			#DISPLAY STATIC MENU
			pygame.draw.rect(screen, BLACK,(30,8,278,95),2)
			screen.blit(menuText,(35,10))
			screen.blit(menuText2,(35,40))
			screen.blit(menuText3,(35,70))
			##
			
			#SETUP RETURNED DATA VAR FONTS
			timeText=displayFont.render("%02d:%02d " % (wtime_mins, wtime_secs),True,BLUE)
			tenthsText=display_smFont.render("." + wtime_tenths,True,BLUE)
			paceText=displayFont.render("%02d:%02d " % (pace_mins, pace_secs),True,GOLD)
			metersText=displayFont.render(str(cmeters),True,PURPLE)		
			srateText=displayFont.render(str(srate),True,ORANGE)
			hrateText=displayFont.render(str(hrate),True,RED)
			
			screen.blit(timeText,(400,10))
			if wtime_mins < 100:
				screen.blit(tenthsText,(780,75))
			else:#shift tenths figure to right for 3-digit mins
				screen.blit(tenthsText,(865,75))
			
			screen.blit(paceText,(400,195))	
			screen.blit(split_unitsText,(820,260))#label
			
			screen.blit(metersText,(400,395))
			screen.blit(distance_unitsText,(825,462))#label
			
			screen.blit(srateText,(110,590))
			screen.blit(srate_unitsText,(340,655))#label
			
			screen.blit(hrateText,(670,590))
			screen.blit(heart,(900,630))#symbol
			pygame.display.update()
			
		if view==1:
			counter = 0#reset the counter from previous force curve view 
			screen.blit(background,(0,0))
			
			#DISPLAY STATIC MENU
			pygame.draw.rect(screen, BLACK,(30,8,278,95),2)
			screen.blit(menuText,(35,10))
			screen.blit(menuText2,(35,40))
			screen.blit(menuText3,(35,70))
			##
			
			#SETUP RETURNED DATA VAR FONTS
			timeText=displayFont.render("%02d:%02d " % (wtime_mins, wtime_secs),True,BLUE)
			tenthsText=display_smFont.render("." + wtime_tenths,True,BLUE)
			calhrText=displayFont.render(str(calhr),True,GOLD)
			caloriesText=displayFont.render(str(calories),True,PURPLE)		
			srateText=displayFont.render(str(srate),True,ORANGE)
			hrateText=displayFont.render(str(hrate),True,RED)
			
			screen.blit(timeText,(400,10))
			if wtime_mins < 100:
				screen.blit(tenthsText,(780,75))
			else:#shift tenths figure to right for 3-digit mins
				screen.blit(tenthsText,(865,75))	
			
			screen.blit(calhrText,(400,195))	
			screen.blit(cal_hr_unitsText,(820,260))#label
			
			screen.blit(caloriesText,(400,395))
			screen.blit(cals_unitsText,(820,465))#label
			
			screen.blit(srateText,(110,590))
			screen.blit(srate_unitsText,(340,655))#label
			
			screen.blit(hrateText,(670,590))
			screen.blit(heart,(900,630))#symbol
			pygame.display.update()			
		
		if view==2:
			plot_col_picker = counter
			if counter==0:	#5 visible force curves before clearing screen
				screen.fill(GREY)
				screen.blit(graph,(0,0))
			elif counter==4:
				counter=-1
				
			#DISPLAY STATIC MENU
			pygame.draw.rect(screen, BLACK,(30,8,278,95),2)
			screen.blit(menuText,(35,10))
			screen.blit(menuText2,(35,40))
			screen.blit(menuText3,(35,70))
			##
			
			counter+=1
			sample=20 #starts at 20 pixels along x_axis for first reading
			for f in force:
				if plot_col_picker == 0: #red
					screen.blit(plotter_red,(sample,735-(f*2.52))) 
				elif plot_col_picker == 1: #green
					screen.blit(plotter_green,(sample,735-(f*2.52))) 
				elif plot_col_picker == 2: #blue
					screen.blit(plotter_blue,(sample,735-(f*2.52))) 
				elif plot_col_picker == 3: #yellow
					screen.blit(plotter_yellow,(sample,735-(f*2.52))) 
				elif plot_col_picker == 4: #black
					screen.blit(plotter_black,(sample,735-(f*2.52))) 
				
				#screen.blit(plotter,(sample,735-(f*2.52))) 
				'''y_axis max height (758) / max force (300) = 2.52 (each force unit is 2.52 pixels on y axis)
				minus from 735 (y_axis height) to plot the curve starting at bottom since coord 0,0 is top left'''
				sample+=13 #moves the plotter 13 pixels along x_axis per cycle
				pygame.display.update() #update screen for each plotted point
			
			if plot_col_picker == 0: #red
				powerText=smallFont.render(str(power)+"w",True,RED)
				screen.blit(powerText,(700,60))
			elif plot_col_picker == 1: #green
				powerText=smallFont.render(str(power)+"w",True,GREEN)
				screen.blit(powerText,(700,130))
			elif plot_col_picker == 2: #blue
				powerText=smallFont.render(str(power)+"w",True,BLUE)
				screen.blit(powerText,(700,200)) 
			elif plot_col_picker == 3: #yellow
				powerText=smallFont.render(str(power)+"w",True,GOLD)
				screen.blit(powerText,(700,270))
			elif plot_col_picker == 4: #black
				powerText=smallFont.render(str(power)+"w",True,BLACK)
				screen.blit(powerText,(700,340))
				
			pygame.display.update()
			
		#pygame.display.update() either update all views here or update after each view

	#handle end of workout
	while game_over==True:
		pygame.draw.rect(screen, BLACK, (390,300,265,100),0)
		endText=tinyFont.render("Session Ended!",True,WHITE)
		endText2=tinyFont.render("Press ENTER to EXIT",True,WHITE)
		screen.blit(endText,(430,305))
		screen.blit(endText2,(400,360))
		pygame.display.update()
		for event in pygame.event.get():
			if event.type==pygame.KEYDOWN:
				if event.key==pygame.K_RETURN or event.key==pygame.K_KP_ENTER:
					pygame.quit()
					sys.exit()

if __name__ == '__main__':
    main()
