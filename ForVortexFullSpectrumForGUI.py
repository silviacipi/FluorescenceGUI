import h5py
import cv2
import os
from os import listdir
from os.path import isfile, join
import numpy as np
from matplotlib import pyplot as plt
from matplotlib.pyplot import ion
from scipy.signal.signaltools import wiener
import EllipseForKaz
from scipy import math

def selectData(v, nxsfileName,dataFolder):
    if v==1:
        print 'you selected HDF5 file'
        findContour(v, nxsfileName,dataFolder)
    else:
        print 'you selected TIF file'
        findContour(v, nxsfileName,dataFolder)
            
def findContour(v,nxsfileName,dataFolder, channelmin,channelmax,aa,bb):
    print nxsfileName
    
    mypath=h5py.File(nxsfileName,'r') 
    print 'looking for "',dataFolder, '" in the tree...'
    contLoop=True
    pathTot=''
    contLoop, pathToData, pathTot=myRec(mypath,contLoop,pathTot,dataFolder)
    print pathTot
    if not contLoop:
        print 'database "',dataFolder,'" found in  ', pathTot
        data=mypath[str(pathTot)]
        npdata=np.array(data)
        a,b,c=npdata.shape
        print a,b,c, ' file images to analyse' 
        sizeA=int(math.sqrt(a))
        print 'size', sizeA
        s=(aa,bb)
        image=np.zeros((bb,aa))
        print np.shape(image)
        counter=0
        minchan=int(channelmin/0.00125)
        maxchan=int(channelmax/0.00125)
        for i in range (aa):
#            print 'i', i
            for j in range (bb):
#               print j
                sum=0
                for col in range(minchan,maxchan):
                    sum=sum+npdata[counter][0][col]
                if v==1:
                    image[j][i]=sum
                else:
                    if i % 2 == 0:
    #                print 'it is even 
                       # print i,j
                        image[j][i]=sum
    #                print j,i
                    else:
                        image[bb-1-j][i]=sum
#                print sizeA-1-j,i
                counter=counter+1
        fig1 = plt.figure(1)
        plt.imshow(image)
        plt.show()
        xlength=np.linspace(0, aa, aa)
        plt.plot(xlength,image[0][:])
        plt.show()
    else:
        print 'database "', dataFolder,'" not found!'
    '''
        if v==1:
            a,b,c=npdata.shape
        else:
            a,b=npdata.shape
        print a, ' file images to analyse' 
        circlesProperties = np.zeros((1,2))
        fig3 = plt.figure(2)
        ax = fig3.gca()
        fig3.show()
        for i in range(a-1):
            print 'image ',i
            if v==1:
                # for HDF file
                img=npdata[i][:b][:c]
                blank_image = np.zeros((b,c,1), np.uint8)
            else:
                #For tif file
                #filename, file_extension = os.path.splitext(npdata[i][0])
                #########temporary
                mypath='C:\\Users\\xfz42935\\Documents\\Alignement\\64768-pco1-files' 
                #print mypath
                onlyfiles=[f for f in listdir(mypath) if isfile(join(mypath,f))]
                filename, file_extension = os.path.splitext(onlyfiles[i])             
                #########end of temporary
                if file_extension=='.tif':
                    #temporary
                    try:
                        #img=cv2.imread(join(mypath,onlyfiles[i]),cv2.IMREAD_UNCHANGED )
                        #end of temporary
                        img=cv2.imread(npdata[i][0],cv2.IMREAD_UNCHANGED )
                        height=np.size(img, 0)
                        width=np.size(img, 1)
                        blank_image = np.zeros((height,width,1), np.uint8)
                    except:
                        print 'image ',npdata[i][0]
                        print 'image not found: check the path'
                        continue
                else:
                    print 'tif image not found...looking for the next'
                    continue
                
            #minVal, maxVal, minLoc, maxLoc= cv2.minMaxLoc(img)   
            #temp=img/maxVal*255
            #blank_image=temp.astype(np.uint8)
            
            #### filtering
            img=wiener(img,mysize=9, noise=0.9)        
            height,width=img.shape
            blank_image = np.zeros((height,width,1), np.uint8)
            minVal, maxVal, minLoc, maxLoc= cv2.minMaxLoc(img)
            temp=img/maxVal*255
            #lowThresh=int((maxVal-minVal)/maxVal*255/4)
            #print 'low thresh',lowThresh
            blank_image=temp.astype(np.uint8)
            #ax.imshow(blank_image,cmap = 'gray')
            #fig3.canvas.draw()
            #ret, thresh=cv2.threshold(blank_image,50,255,cv2.THRESH_BINARY)  
            
            thresh=cv2.adaptiveThreshold(blank_image,255,cv2.ADAPTIVE_THRESH_MEAN_C,cv2.THRESH_BINARY,31,0)   
            ax.imshow(thresh,cmap = 'gray')
            fig3.canvas.draw()                
            pippo=thresh.copy()
            #looking for contours
            pippo, contours,hierarchy = cv2.findContours(pippo, cv2.RETR_TREE,cv2.CHAIN_APPROX_NONE)
            cnt=contours[0]
            centres = []
            test=0;
            for ii in range(len(contours)):
                moments = cv2.moments(contours[ii])
                  
                if not (moments['m00']==0):
                    p1=moments['m10']/moments['m00']
                    p2=moments['m01']/moments['m00']
                    if ii==1:
                        newrow = [[p1, p2]]
                        print 'circle found ', p1,p2
                        print 'hierarchy', hierarchy
                        centres.append([int(p1), int(p2)])
                       # print 'centre value', blank_image[int(p1), int(p2)]/maxVal, 'max value', maxVal
                        test=1
                        if i==0:
                            circlesProperties=newrow
                        else:
                            circlesProperties=np.vstack((circlesProperties,newrow))
                        break
            if not (test):
                print 'circle not found'        
        circlesProperties=np.array(circlesProperties)
        OneMat=np.ones_like(circlesProperties)    
        circlesProperties=circlesProperties+OneMat
        if len(circlesProperties)>1:
            y0, y1, y2, y3,y4=EllipseForKaz.Ellipse(circlesProperties[:,0], circlesProperties[:,1])
        else:
            print 'No circles found in images: check loaded nxs'
        print 'END'
        '''

      
def myRec(obj,continueLoop,pathTot,dataFolder):  
    ### recursive function to look for the data database
    temp=None
    i=1
    tempPath=''
    for name, value in obj.items():
        if continueLoop:
            #check if the object is a group
            if isinstance(obj[name], h5py.Group):
                tempPath='/'+name
                if len(obj[name])>0:
                    continueLoop,temp,tempPath= myRec(obj[name],continueLoop,tempPath,dataFolder)
                else:
                    continue
            else:
                test=obj[name]
                temp1='/'+dataFolder
                if temp1 in test.name:
                    continueLoop=False
                    tempPath=pathTot+'/'+name
                    return continueLoop,test.name,tempPath
            i=i+1
        if (i-1)>len(obj.items()):
            tempPath=''
    pathTot=pathTot+tempPath
    return continueLoop,temp, pathTot

    
   
#########For testing function
if __name__ == "__main__":
    pathToNexus='/dls/i13-1/data/2017/cm16785-1/raw/92770.nxs'
    #name='C:\\Users\\xfz42935\\Documents\\Alignement\\pco1-63429.hdf'
    findContour(pathToNexus,'fullSpectrum',9.5,9.7,86,10)
