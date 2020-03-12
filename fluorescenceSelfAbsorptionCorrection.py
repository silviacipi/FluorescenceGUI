import h5py
import numpy as np
from matplotlib import pyplot as plt
from scipy import math
import cv2
import json
#import TomopyReconstructionForVortexAbsorptionPt2506
#from TomopyReconstructionForVortexCsU import tomography
#from TomopyReconstructionForVortexAbsorptionPt1407 import tomography


  
class material(object):
    def __init__(self, name,density):
        self.name=name
        self.density=density
        print 'class defining material'
    #name =''
    keys=['material', 'massAbsCoef']
    myDictionary=dict(dict.fromkeys(keys, None))
    
    #def setName(self,materialName):
    #    self.name=materialName
    def readName(self):
        print 'material name:',self.name  
    def setPathToProjections(self,path):
        self.pathToProjections=path
        
class processingTools():
    def __init__(self):
        print 'defining tool'
        
class materialProjectionsTomo(object):
    def __init__(self, name,pathToProjection):
        self.name=name
        print 'class defining material'
        #self.projections=pathToProjection
        self.path=pathToProjection
    def set_projection(self,projection):
        self.projection=projection
    def set_materialTomo(self,tomo):    #self.tomo=np.zeros([angles,width,width])
        self.tomo=tomo
    
 
            
def AttenuationCorrection(listOfMaterials,outFold, pathToMerlinTomo,dataFolder,tomoCentre,minFluoSignal,projShift,numAngle,angleRange):

    pixelSize=0.25e-4
    mypathMerlin=h5py.File(pathToMerlinTomo,'r') 
    print 'looking for "',dataFolder, '" in the tree...'
    contLoop3=True
    pathTot3=''
    contLoop3, pathToData3, pathTot3=myRec(mypathMerlin,contLoop3,pathTot3,dataFolder)
    
    if not (contLoop3):
        print 'database "',dataFolder,'" found in  ', pathTot3
        #npdataPt=np.array(mypathPt[str(pathTot)])
        #npdataCu=np.array(mypathCu[str(pathTot2)])
        tomoMerlin=mypathMerlin[str(pathTot3)]
        
        
        
        print 'loading materials'
        print len(listOfMaterials)
        materialsAnalysis=[]
        print 'loading data...'
        
        for i in range(len(listOfMaterials)):
            print 'Im happy here'
            name=listOfMaterials[i]
            temp=materialProjectionsTomo(listOfMaterials[i].name,listOfMaterials[i].pathToProjections)
            contLoop=True
            pathTot=''
            print 'path to projections', listOfMaterials[i].pathToProjections
            mypathTemp=h5py.File(temp.path,'r') 
            contLoop, pathToData, pathTot=myRec(mypathTemp,contLoop,pathTot,dataFolder)
            try:
               
                temp.set_projection(np.array(mypathTemp[str(pathTot)]))
                #print 'just before ', temp.path,dataFolder,tomoCentre
                
                #temp.set_materialTomo(tomography(temp.path,dataFolder, tomoCentre))
                #print 'tomography added'
                materialsAnalysis.append(temp)
                materialsAnalysis[i].set_materialTomo(tomography(materialsAnalysis[i].path,dataFolder, tomoCentre,numAngle,angleRange))
                print materialsAnalysis[i].name, 'loaded'
                #plt.imshow(materialsAnalysis[i].tomo[1,:,:])
                #plt.show()
                #raw_input("Press Enter to continue...")   
            except:
                print 'data', listOfMaterials[i].pathToProjections, 'not found! closing'
            
        #raw_input("Press Enter to continue...")       
            #materialsAnalysis.append(materialProjectionsTomo())
            #materialsAnalysis=[]
        #npdataPt=np.array(mypathPt[str(pathTot)])
            
            
        #raw_input("Press Enter to continue...")    
        '''
        STEP 1:
        do the tomography with the acquired sinograms
        '''
        testIteration=0
        NewMaterials = [None] * len(listOfMaterials)
        MaterialsCorrection = [None] * len(listOfMaterials)
        MaterialDensity = [None] * len(listOfMaterials)
        while testIteration<10:
            testIteration+=1
            print 'iteration', testIteration
            npdataMerlin=np.array(tomoMerlin)
            #a,b,c=np.shape(npdataMerlin)
            nAngles=0
            height=0
            width=0
            print np.shape(tomoMerlin), 'shape'
            SumTotTomo=np.zeros(np.shape(tomoMerlin))
            for nMat in range (len(listOfMaterials)):
                #print nMat
                
                #print 'reconstruction done for ', materialsAnalysis[nMat].name
                print np.shape(materialsAnalysis[nMat].tomo)
                SumTotTomo+=materialsAnalysis[nMat].tomo
                #print 'VALUE',materialsAnalysis[nMat].tomo[1,25,68]
                #plt.figure(1)
                #plt.imshow(materialsAnalysis[nMat].tomo[1,:,:],'Greys')
                #plt.show()
                nAngles,height,width=np.shape(materialsAnalysis[nMat].projection)
                NewMaterials[nMat]=np.zeros([nAngles,height,width])
                NewMaterials[nMat][:,:,0]=materialsAnalysis[nMat].projection[:,:,0]
                #print nAngles,height,width, 'shape'
                MaterialsCorrection[nMat]=np.ones((nAngles,height,width,width))
            print 'tomography done, now Calculated Densities'    
            print 'VALUE',materialsAnalysis[6].tomo[11,23,20]
            #raw_input("Press Enter to continue...") 
            materialRatio=[None]*len(listOfMaterials)
            materialEffectiveDensity=[None]*height
            for heightIndex in range(height):
                effDens=np.zeros([width,width,len(listOfMaterials)])
                for firstIndex in range(width):
                    for secondIndex in range(width):
                        sum=0
                        nMat=0
                        for nMat in range (len(listOfMaterials)):
                            effDensTemp=np.zeros([height,width,width])
                            if SumTotTomo[heightIndex,firstIndex,secondIndex]>minFluoSignal:
                                materialRatio[nMat]=materialsAnalysis[nMat].tomo[heightIndex,firstIndex,secondIndex]/SumTotTomo[heightIndex,firstIndex,secondIndex]
                            else:
                                materialRatio[nMat]=0
                            sum+=listOfMaterials[nMat].density* materialRatio[nMat]*listOfMaterials[nMat].myDictionary['Beam']
                            
                            #print 'beam Coefficient', listOfMaterials[nMat].myDictionary['Beam'], 'for', listOfMaterials[nMat].name, sum
                            #raw_input("Press Enter to continue...") 
                        constant=0
                        try:
                            #print 'log of absorption',abs(npdataMerlin[heightIndex,firstIndex,secondIndex])
                            constant=-math.log(1-abs(npdataMerlin[heightIndex,firstIndex,secondIndex]))/(pixelSize*sum)
                            
                            #print 
                            
                        except:
                            constant=0
                            #print npdataMerlin[heightIndex,firstIndex,secondIndex]
                        
                        
                        for nMat in range (len(listOfMaterials)):
                            effDens[firstIndex,secondIndex,nMat]=constant*listOfMaterials[nMat].density*materialRatio[nMat]
                            #print 'this is the calculated constant',constant,listOfMaterials[nMat].name,materialRatio[nMat]
                
                materialEffectiveDensity[heightIndex]=effDens
                #raw_input("end of one slice Press Enter to continue...")   
                #plt.figure(2000)
                #plt.imshow(materialEffectiveDensity[heightIndex][:,:,0])
                #plt.figure(2001)
                #plt.imshow(materialEffectiveDensity[heightIndex][:,:,1])
                #plt.show()
                #plt.figure(2)
                #plt.imshow(materialRatio[nMat][1,:,:],'Greys')
            #plt.show() 
            #print 'this is the ratio'
            #raw_input("Press Enter to continue...") 
            
            
            #print a,b,c, 'shape of npdataPt'
            
            #NewPt=np.zeros(npdataPt.shape)
            #NewCu=np.zeros(npdataCu.shape)
            #NewPt[:,:,0]=npdataPt[:,:,0]
            #NewCu[:,:,0]=npdataCu[:,:,0]
            #PtCorrect=np.ones((nAngles,height,width,width))
            MaterialCorrection=np.ones((len(listOfMaterials),nAngles,height,width,width))
            #a,b,c=npdataPt.shape
            #print a,b,c, ' file images to analyse' 
            print 'doing correction'
            shift=projShift
            minimum=0.001
            maximum=0.05
            
            '''
            massAttcoeffCu118=141.9657
            massAttcoeffPt118=134.3#184.0857#134.3#
            
            massAttcoeffCu944=241.8#127.08#252.5462#241.8#
            massAttcoeffPt944=288.16#130.3238#288.16#
            
            massAttcoeffCu804=50.7332
            massAttcoeffPt804=321.4#197.5128#321.4#
            '''
            #PtDensity=0
            #CuDensity=0
            generalDensity=0
            '''
            this shift is due to the centre of rotation, the centre of rotation is 23, the centre of the reconstruction is 43,
             so I need to shift 20 pixels to have the profile coincide '''
            xplot=np.linspace(0, width-1,width)
            for i in range(0,nAngles):
                print 'angle', i
                for k in range(height):
                    #print 'slice',k
                    '''
                    rotating absorption
                    '''
                    M = cv2.getRotationMatrix2D((width/2,width/2),-i,1)
                    merlinSlice=npdataMerlin[k,:,:]
                    dst = cv2.warpAffine(merlinSlice,M,(width,width))
                    dstShifted=np.zeros((width,width))
                    if abs(shift)>0:
                        dstShifted[0:width-1-shift,:]=dst[shift:width-1,:]
                    else:
                        dstShifted=dst
                    binaryMask=np.zeros((width,width))
                    
                    MaterialSlice=[None]*len(listOfMaterials)
                    dstShiftedMaterial=[None]*len(listOfMaterials)
                    shiftedMaterialDensity=[None]*len(listOfMaterials)
                    binaryMaskMaterial=[None]*len(listOfMaterials)
                    '''
                    rotating fluorescence and density
                    '''
                    
                    for nMat in range(len(listOfMaterials)):
                        #print 'pippo'
                        #MaterialSlice[nMat]=materialsAnalysis[nMat].tomo[k,:,:]
                        #dstMAterial=cv2.warpAffine(MaterialSlice[nMat],M,(width,width))
                        '''
                        rotate tomography of each material
                        '''
                        #print 'material', nMat
                        dstMaterial=cv2.warpAffine(materialsAnalysis[nMat].tomo[k,:,:],M,(width,width))
                        #print 'here',np.shape(np.zeros((width,width)))
                        
                        binaryMaskMaterial[nMat]=np.zeros((width,width))
                        #print 'here here'
                        #temp111=np.zeros((width,width))
                        #print np.shape(dstShiftedMaterial[nMat])
                        dstShiftedMaterial[nMat]=np.zeros((width,width))
                        #print 'here here here'
                        '''
                        shift the rotated material
                        '''
                        shiftedMaterialDensity[nMat]=np.zeros([width,width])
                        if abs(shift)>0:
                            dstShiftedMaterial[nMat][0:width-1-shift,:]=dstMaterial[shift:width-1,:]
                            '''
                            shift material density
                            '''
                            shiftedMaterialDensity[nMat][0:width-1-shift,:]=cv2.warpAffine(materialEffectiveDensity[k][:,:,nMat],M,(width,width))[shift:width-1,:]
                        else:
                            dstShiftedMaterial[nMat]=dstMaterial
                            shiftedMaterialDensity[nMat]=cv2.warpAffine(materialEffectiveDensity[k][:,:,nMat],M,(width,width))

                        '''
                        shift material density
                        '''
                        shiftedMaterialDensity[nMat][0:width-1-shift,:]=cv2.warpAffine(materialEffectiveDensity[k][:,:,nMat],M,(width,width))[shift:width-1,:]
                        #shiftedMaterialDensity[nMat]=cv2.warpAffine(materialEffectiveDensity[k][:,:,nMat],M,(width,width))

                    #print 'creating masks...'
                    
                    for kk in range(width):
                        for ll in range(width):
                            if (dstShifted[kk,ll]>minimum) and (dstShifted[kk,ll]<maximum):
                                binaryMask[kk,ll]=1
                            for nMat in range(len(listOfMaterials)):
                                if (dstShiftedMaterial[nMat][kk,ll]>minFluoSignal):
                                    #print 'thick'
                                    binaryMaskMaterial[nMat][kk,ll]=1
                                #else:
                                    #print 'not thick'
                    #raw_input('created mask')
                                #binaryMaskPt[kk,ll]=1
                            #if (dstCuShifted[kk,ll]>0.001):
                                #binaryMaskCu[kk,ll]=1
                    #print 'masks created'
                    
                    
                    plt.figure(3)
                    plt.imshow(binaryMask)
                    plt.figure(4)
                    plt.imshow(binaryMaskMaterial[1])
                    #plt.figure(7)
                    #plt.imshow(dstShiftedMaterial[1])
                    
                    #plt.show()
                    '''
                    plt.figure(5)
                    plt.imshow(binaryMaskCu)
                    plt.figure(6)
                    plt.imshow(dstPtShifted)
                    plt.figure(7)
                    plt.imshow(dstCu)
                    plt.show()
                    '''
                    #PtCorrect=np.ones(npdataPt.shape)
                    #print 'calculating average density for each amterial'
                    for j in range(0,width):
                        #print 'inside'
                        #PtCorrect=1
                        #CuCorrect=1
                        #profThickScanning=np.sum(binaryMask[j,:],axis=0)
                        #profAbsScanning=np.sum(dstShifted[j,:],axis=0)
                        #PtCorrect=1
                        for ll in range(0,j-1):
                            #print 'inside2'
                        #for ll in range(j-1,c):
                            '''
                            correction for absorption
                            '''
                            profll=binaryMask[ll,:]*binaryMask[j,:]
                            profllAbs=dstShifted[ll,:]*binaryMask[j,:]
                            profThick= np.sum(profll)# thickenss of the procile at j-1
                            profAbs= np.sum(profllAbs)
                            '''
                            correct the new mask for my mask
                            For Cu first and Pt then
                            '''
                            #profThickMaterial=np.zeros(len(listOfMaterials))
                            #profAbsMaterial=np.zeros(len(listOfMaterials))
                            averageDensityMaterial=np.zeros(len(listOfMaterials))
                            #print 'calculating average raw density for each material'
                            for nMat in range(len(listOfMaterials)):
                                #profllMaterial=binaryMask[ll,:]*binaryMask[j,:]*binaryMaskMaterial[nMat][j,:]
                                profllMaterial=binaryMask[ll,:]*binaryMaskMaterial[nMat][j,:]
                                correction=1
                                nMat2=0
                                for nMat2 in range(len(listOfMaterials)):
                                    #profllDensMaterial=shiftedMaterialDensity[nMat2][ll,:]*binaryMask[j,:]*binaryMaskMaterial[nMat][j,:]
                                    profllDensMaterial=shiftedMaterialDensity[nMat2][ll,:]*binaryMaskMaterial[nMat][j,:]
                                    profThickMaterial= np.sum(profllMaterial)
                                    profDensMaterial=np.sum(profllDensMaterial)
                                    if profThickMaterial>0:
                                        averageDensityMaterial[nMat2]=profDensMaterial/profThickMaterial
                                    else:
                                        #print 'Im here'
                                        averageDensityMaterial[nMat2]=0
                                    correction=correction*math.exp(-averageDensityMaterial[nMat2]*listOfMaterials[nMat2].myDictionary[listOfMaterials[nMat].name]*pixelSize)
                                    
                            #for nMat in range(len(listOfMaterials)):
                                #raw_input("Press Enter to continue...")
                                MaterialCorrection[nMat,i,k,j,ll]=correction
                                #print correction, 'correction',MaterialCorrection[nMat,i,k,j,ll]
                            #print 'after for loop'
                            
                            
                        #plt.imshow(MaterialCorrection[0,:,2,:,20])    
                        #plt.show()
                        #print np.min(MaterialCorrection[])
                        NewCorrectionMaterial=np.ones(len(listOfMaterials))
                        #NewcorrectionPt=1
                        #NewcorrectionCu=1
                        for lll in range(j):  
                            for nMat in range (len(listOfMaterials)):
                                 NewCorrectionMaterial[nMat]*=MaterialCorrection[nMat,i,k,j,lll] 
                            #print NewCorrectionMaterial[nMat], 'newCorrection AMterial', lll
                            #NewcorrectionPt*=PtCorrect[i,k,j,lll]
                            #NewcorrectionCu*=CuCorrect[i,k,j,lll]
                        for nMat in range(len(listOfMaterials)):
                            #if not(NewCorrectionMaterial[nMat]==1):
                                #print 'correction',NewCorrectionMaterial[nMat],i,k,j
                            NewMaterials[nMat][i,k,j]=materialsAnalysis[nMat].projection[i,k,j]/NewCorrectionMaterial[nMat]
                            #plt.figure(1)
                            #plt.imshow(materialsAnalysis[nMat].projection[i,:,:])
                            #plt.figure(2)
                            #plt.imshow(NewMaterials[nMat])
                            #plt.show()
            
            
                #plt.imshow(shiftedMaterialDensity[nMat])
                #plt.show()
            print 'all done, writing file for each material....'
            
            tomoNew=[None]*len(listOfMaterials)
            for nMat in range(len(listOfMaterials)):
                
                nameMat=outFold+"vortexProjections"+listOfMaterials[nMat].name+"0108.hdf"
                vortexImPt=h5py.File(nameMat,"w")
                dsetImagePt=vortexImPt.create_dataset('data', (nAngles,height,width), 'f')
                dsetImagePt[...]=NewMaterials[nMat]#/myMax
                vortexImPt.close()
                print 'nameMat'
                listOfMaterials[nMat].path=nameMat
                print 'processing the new tomography for', listOfMaterials[nMat].name, 'name',nameMat 
                tomoNew[nMat]=tomography(nameMat, 'data',tomoCentre, numAngle,angleRange)
                plt.figure(1)
                plt.imshow(materialsAnalysis[nMat].tomo[12,:,:])
        
                plt.figure(2)
                plt.imshow(tomoNew[nMat][12,:,:])
                #plt.show()
                materialsAnalysis[nMat].set_materialTomo(tomoNew[nMat])
                
                #raw_input("Press Enter to continue...")
                
            #namePt="/dls/i13-1/data/2017/cm16785-1/processing/VortexTomo/vortexProjectionsPtAttenuation2506.hdf"
            #nameCu="/dls/i13-1/data/2017/cm16785-1/processing/VortexTomo/vortexProjectionsCuAttenuation2506.hdf"
            
            
            #namePtCorrection="/dls/i13-1/data/2017/cm16785-1/processing/VortexTomo/vortexProjectionsPtAttenuationCorrection0803.hdf"
            #nameCuCorrection="/dls/i13-1/data/2017/cm16785-1/processing/VortexTomo/vortexProjectionsCuAttenuationCorrection0803.hdf"
            #name="/dls/i13-1/data/2017/cm16785-1/processing/VortexTomo/vortexProjectionsPtAttenuation.hdf"
            '''
            vortexImPt=h5py.File(namePt,"w")
            dsetImagePt=vortexImPt.create_dataset('data', (a,b,c), 'f')
            dsetImagePt[...]=NewPt#/myMax
            vortexImPt.close()
            
            vortexImCu=h5py.File(nameCu,"w")
            dsetImageCu=vortexImCu.create_dataset('data', (a,b,c), 'f')
            dsetImageCu[...]=NewCu#/myMax
            vortexImCu.close()
            '''
        '''
            pathToNexusPt=namePt
            pathToNexusCu=nameCu
            
            tomoPtNew=tomography(namePt, 'data', 23)
            tomoCuNew=tomography(nameCu, 'data', 23)
            plt.figure(1)
            plt.imshow(tomoPt[1,:,:])
        
            plt.figure(2)
            plt.imshow(tomoPtNew[1,:,:])
        
            plt.figure(3)
            plt.imshow(tomoCu[1,:,:])
        
            plt.figure(4)
            plt.imshow(tomoCuNew[1,:,:])
            #plt.show()
        '''
            
        for nMat in range(len(listOfMaterials)):
            nameTomoMaterial=outFold+"vortexTomo"+listOfMaterials[nMat].name+"0108.hdf"
        #nameTomoPt="/dls/i13-1/data/2017/cm16785-1/processing/VortexTomo/vortexTomoPt2506.hdf"
        #nameTomoCu="/dls/i13-1/data/2017/cm16785-1/processing/VortexTomo/vortexTomoCu2506.hdf"
        
        
        
            vortexImPtCorr=h5py.File(nameTomoMaterial,"w")
            dsetImagePtCorr=vortexImPtCorr.create_dataset('data', (height,width,width), 'f')
            dsetImagePtCorr[...]=tomoNew[nMat]#/myMax
            vortexImPtCorr.close()
        
        
        '''
        
        #print dsetImage.shape
        #print dsetImage.dtype
        #count=0
        #imageVortex=np.zeros(((depthProjections,height,width)))
        #myMax=0
        '''
        
        
        
    else:
        print 'database "', dataFolder,'" not found!'
    #mypathPt.close()
    #mypathCu.close()
    print 'all done, all closed'
    #return image

      
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

def findIndexAbove(value,arr): 
	item2=0
	index2=len(arr)
	for index, item in enumerate(arr):
    		if item > value:
			if index<index2:
				index2=index
				item2=item
        return index2, item2
   

def findIndexBelow(value,arr):  
	item2=0
	index2=0
	for index, item in enumerate(arr):
    		if item < value:
			if index>index2:
				index2=index
				item2=item
	
        return index2, item2

def interpolateValue(lowX, loxY, highX, highY, wantedX): 
	wantedY=loxY+(wantedX-lowX)*(highY-loxY)/(highX-lowX)
	print lowX, loxY, highX, highY, wantedX,wantedY
	raw_input('interpolated values...')
	return wantedY

  
#########For testing function
if __name__ == "__main__":
    # load material list with density, projection files, absorption file and output file
    materialName="/dls/i13-1/data/2020/mg23919-1/processing/Densities297293.json"
    with open(materialName) as json_data_file:
        data = json.load(json_data_file)
        print data
        print data["materials"]["name"][0],len(data["materials"]["name"])
        print 'output folder', data["outputFolder"]["path"]
        print 'absorption Path', data["absorptionTomo"]["path"]
    raw_input('Press enter to continue...')
    numbOfMaterials=2
    emissionLine="/dls_sw/i13-1/scripts/fluorescence/elementsEmissionLines.json"
    with open(emissionLine) as json_dataLines_file:
	dataLines = json.load(json_dataLines_file)
	#print dataLines["materials"]["Pb"]
    

    
    
    
    listOfMaterials = []
    for i in range(len(data["materials"]["name"])):
        listOfMaterials.append(material(data["materials"]["name"][i],data["materials"]["density"][i]))
        listOfMaterials[i].setPathToProjections(data["materials"]["path"][i])
        print listOfMaterials[i].name,listOfMaterials[i].density, listOfMaterials[i].pathToProjections
    raw_input('Press enter to continue...')
    print 'loading mass attenuation coefficients...'
    massAttenuationCoefficientsFile=[]

    for i in range(len(data["materials"]["name"])):
	print data["materials"]["name"][i]
	massAttenuationCoefficientsFile.append("/dls_sw/i13-1/scripts/Silvia/Fluorescence/dev/"+data["materials"]["name"][i]+".dat")
	print massAttenuationCoefficientsFile[i]
	try:
    		absorption=np.loadtxt(massAttenuationCoefficientsFile[i], skiprows=1)
		#absorption=np.ndarray(absorption)
		print np.shape(absorption)
		plt.xscale('log')
		plt.plot(absorption[:,0]*1000,absorption[:,1])
		plt.show()
	except:
		print 'mass attenuation coefficent file for ',data["materials"]["name"][i] ,'not found'
	
    for i in range(len(data["materials"]["name"])):
            for j in range(len(data["materials"]["name"])):
		try:
    			absorption=np.loadtxt(massAttenuationCoefficientsFile[i], skiprows=1)
			#absorption=np.ndarray(absorption)
			#print np.shape(absorption)
			#plt.xscale('log')
			#plt.plot(absorption[:,0]*1000,absorption[:,1])
			#plt.show()
			print 'setting up mass absorption coefficient of ', listOfMaterials[i].name, " for the energy ", dataLines["materials"][listOfMaterials[j].name]
			energyLine=float(dataLines["materials"][listOfMaterials[j].name])
			indexAbove,itemAbove=findIndexAbove(energyLine,absorption[:,0]*1000)
			indexBelow,itemBelow=findIndexBelow(energyLine,absorption[:,0]*1000)
			absorptionCoef=interpolateValue(itemBelow, absorption[indexBelow,1], itemAbove, absorption[indexAbove,1], energyLine)
                	listOfMaterials[i].myDictionary[listOfMaterials[j].name]=absorptionCoef
			print absorptionCoef
		except:
			print 'mass attenuation coefficent file for ',data["materials"]["name"][i] ,'not found'
	    energyLine=float(dataLines["materials"]["Beam"])
	    indexAbove,itemAbove=findIndexAbove(energyLine,absorption[:,0]*1000)
	    indexBelow,itemBelow=findIndexBelow(energyLine,absorption[:,0]*1000)
	    absorptionCoef=interpolateValue(itemBelow, absorption[indexBelow,1], itemAbove, absorption[indexAbove,1], energyLine)
            listOfMaterials[i].myDictionary["Beam"]=absorptionCoef
            print  'here'
            print listOfMaterials[i].myDictionary
    raw_input('finished loading material properties: Press enter to continue...')
    '''
    
    #listOfMaterials
    #a=listOfMaterials[0]()
    #mat1=material()
    #mat1.setName('Cu')
    #mat1.myDictionary={'Cu':massAttcoeffCu804, 'Pt':massAttcoeffCu944, 'Beam':massAttcoeffCu118}
    #a=listOfMaterials[0]()
    #mat2=material()
    #mat2.setName('Pt')
    #mat2.myDictionary={'Cu':massAttcoeffPt804, 'Pt':massAttcoeffPt944, 'Beam':massAttcoeffPt118}
    listOfMaterials.append(material('Cu',8.96))
    
    #listOfMaterials.append(mat2)
    listOfMaterials[0].readName()
    listOfMaterials[0].myDictionary={'Cu':massAttcoeffCu804, 'Pt':massAttcoeffCu944, 'Beam':massAttcoeffCu118}
    listOfMaterials[0].setPathToProjections(nameCu)
    listOfMaterials.append(material('Pt',21.45))
    listOfMaterials[1].readName()
    listOfMaterials[1].myDictionary={'Cu':massAttcoeffPt804, 'Pt':massAttcoeffPt944, 'Beam':massAttcoeffPt118}
    listOfMaterials[1].setPathToProjections(namePt)
    print 'number of materials',len(listOfMaterials), listOfMaterials[i].pathToProjections
    print  listOfMaterials[1].myDictionary['Cu']
    #raw_input("Press Enter to continue...")
    '''
    width=40
    height=30
    depthProjections=40
    tomoCentre=19#19 for sample 2
    #name="/home/xfz42935/Documents/Vortex/Merlin/merlinProjections.hdf"
    
    #name="/dls/i13-1/data/2017/cm16785-1/processing/VortexTomo/vortexProjectionsPtAttenuation.hdf"
    nameMerlinTomo=data["absorptionTomo"]["path"]#"/dls/i13-1/data/2017/mt16702-1/processing/Excalibur/PCOTomosample2.hdf"
    outputFolder=data["outputFolder"]["path"]
    #name="/dls/i13-1/data/2017/cm16785-1/processing/VortexTomo/vortexProjectionsPtAttenuation.hdf"
    #vortexIm=h5py.File(name,"w")
    #dsetImage=vortexIm.create_dataset('data', (depthProjections,height,width), 'f')
    #print dsetImage.shape
    #print dsetImage.dtype
    #count=0
    #imageVortex=np.zeros(((depthProjections,height,width)))
    #myMax=0
    minFluoSignal=0.001
    projShift=0
    numAngles=40
    angleRange=175
    AttenuationCorrection(listOfMaterials,outputFolder, nameMerlinTomo,'data',tomoCentre, minFluoSignal, projShift,numAngles,angleRange)
