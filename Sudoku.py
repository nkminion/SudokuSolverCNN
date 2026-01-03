#Imports
import cv2
import numpy as np
import torch
import torch.nn as nn
import torchvision.transforms as transforms
import base64
import os

#Set device
if torch.cuda.is_available():
	device = torch.device("cuda:0")
else:
	device = torch.device("cpu")
print(f"Using device: {device}")

#Define architecture
class MNISTModel(nn.Module):
	def __init__(self):
		super(MNISTModel,self).__init__()

		#Layer1
		self.conv1 = nn.Conv2d(in_channels=1,out_channels=32,kernel_size=3,padding=1,bias=False)#Size does not change
		self.bn1 = nn.BatchNorm2d(num_features=32)
		self.relu1 = nn.ReLU()
		self.pool1 = nn.MaxPool2d(kernel_size=2)#Size halves into 14x14

		#Layer2
		self.conv2 = nn.Conv2d(in_channels=32,out_channels=32,kernel_size=3,padding=1,bias=False)
		self.bn2 = nn.BatchNorm2d(num_features=32)
		self.relu2 = nn.ReLU()

		#Layer3
		self.conv3 = nn.Conv2d(in_channels=32,out_channels=64,kernel_size=3,padding=1,bias=False)
		self.bn3 = nn.BatchNorm2d(num_features=64)
		self.relu3 = nn.ReLU()

		#Layer4
		self.conv4 = nn.Conv2d(in_channels=64,out_channels=64,kernel_size=3,padding=1,bias=False)
		self.bn4 = nn.BatchNorm2d(num_features=64)
		self.relu4 = nn.ReLU()

		#Layer5
		self.conv5 = nn.Conv2d(in_channels=64,out_channels=64,kernel_size=3,padding=1,bias=False)
		self.bn5 = nn.BatchNorm2d(num_features=64)
		self.relu5 = nn.ReLU()
		self.pool2 = nn.MaxPool2d(kernel_size=2)#Size halves into 7x7

		#FlattenLayer
		self.flatten = nn.Flatten()

		#Layer6
		self.fc1 = nn.Linear(in_features=64*7*7,out_features=256)
		self.relu6 = nn.ReLU()

		#Layer7
		self.fc2 = nn.Linear(in_features=256,out_features=64)
		self.relu7 = nn.ReLU()

		#DropoutLayer
		self.dropout = nn.Dropout(p=0.2)

		#Layer8
		self.fc3 = nn.Linear(in_features=64,out_features=10)

	def forward(self,x):

		#Pass through Layer1
		x = self.pool1(self.relu1(self.bn1(self.conv1(x))))

		#Pass through Layer2
		x = self.relu2(self.bn2(self.conv2(x)))

		#Pass through Layer3
		x = self.relu3(self.bn3(self.conv3(x)))

		#Pass through Layer4
		x = self.relu4(self.bn4(self.conv4(x)))

		#Pass through Layer5
		x = self.pool2(self.relu5(self.bn5(self.conv5(x))))

		#Pass through Layer5
		x = self.flatten(x)

		#Pass through Layer6
		x = self.relu6(self.fc1(x))

		#Pass through Layer7
		x = self.relu7(self.fc2(x))

		#Pass through DropoutLayer
		x = self.dropout(x)

		#Pass through Layer7
		x = self.fc3(x)

		#Return Prediction
		return x

#Load Model
model = MNISTModel().to(device)
try:
	ScriptDir = os.path.dirname(os.path.abspath(__file__))
	ModelPath = os.path.join(ScriptDir,"./MNISTModel.pth")
	ModelPath = os.path.normpath(ModelPath)
	model.load_state_dict(torch.load(ModelPath, map_location=torch.device('cpu')))
	model.eval()
except FileNotFoundError:
	print("Model not found")

#Kernels
ThickVerticalKernel = cv2.getStructuringElement(cv2.MORPH_RECT , (1,25))
ThickHorizontalKernel = cv2.getStructuringElement(cv2.MORPH_RECT , (25,1))
ThinVerticalKernel = cv2.getStructuringElement(cv2.MORPH_RECT , (1,17))
ThinHorizontalKernel = cv2.getStructuringElement(cv2.MORPH_RECT , (17,1))

def ProcessAndExtract(InputImg):
	InputImg = cv2.cvtColor(InputImg , cv2.COLOR_BGR2GRAY)
	_,InputImgProcess = cv2.threshold(InputImg,127,255,cv2.THRESH_BINARY_INV)

	#Grid Detection
	Contours,Heirarchy = cv2.findContours(InputImgProcess , cv2.RETR_EXTERNAL , cv2.CHAIN_APPROX_SIMPLE)
	PuzzleContours = None

	if Contours:
		Contours = sorted(Contours , key=cv2.contourArea , reverse=True)
		for Contour in Contours:
			Perimeter = cv2.arcLength(Contour , True)
			Approx = cv2.approxPolyDP(Contour , Perimeter*0.02 , True)
			if (len(Approx) == 4):
				PuzzleContours = Approx
				break

	#Puzzle Cropped Perfectly
	if (PuzzleContours is None):
		x,y,w,h = 0,0,InputImgProcess.shape[1],InputImgProcess.shape[0]
		InputImgProcess = InputImgProcess
	#Contour Found
	else:
		x,y,w,h = cv2.boundingRect(PuzzleContours)
		InputImgProcess = InputImgProcess[y:y+h , x:x+w]

	#Removing Grid Lines
	InputImgProcess = cv2.resize(InputImgProcess , (450,450))
	OutputImg = InputImg[y:y+h , x:x+w]
	OutputImg = cv2.resize(OutputImg , (450,450))

	#Remove Horizontal Lines
	Temp = cv2.morphologyEx(InputImgProcess,cv2.MORPH_OPEN,ThickHorizontalKernel,iterations=2)
	contours,_ = cv2.findContours(Temp,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
	for c in contours:
		cv2.drawContours(InputImgProcess,[c],-1,(0,0,0),5)
	Temp = cv2.morphologyEx(InputImgProcess,cv2.MORPH_OPEN,ThinHorizontalKernel,iterations=2)
	contours,_ = cv2.findContours(Temp,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
	for c in contours:
		cv2.drawContours(InputImgProcess,[c],-1,(0,0,0),5)

	#Remove Vertical Lines
	Temp = cv2.morphologyEx(InputImgProcess,cv2.MORPH_OPEN,ThickVerticalKernel,iterations=2)
	contours,_ = cv2.findContours(Temp,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
	for c in contours:
		cv2.drawContours(InputImgProcess,[c],-1,(0,0,0),5)
	Temp = cv2.morphologyEx(InputImgProcess,cv2.MORPH_OPEN,ThinVerticalKernel,iterations=2)
	contours,_ = cv2.findContours(Temp,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
	for c in contours:
		cv2.drawContours(InputImgProcess,[c],-1,(0,0,0),5)

	Transform = transforms.Compose(
		[
			transforms.ToTensor(),
			transforms.Normalize((0.5,),(0.5,))
		])


	#Cell Segmentation and prediction
	BoardHeight,BoardWidth = InputImgProcess.shape[:2]
	CellHeight = BoardHeight//9
	CellWidth = BoardWidth//9

	Cells = []

	for j in range(9):
		CellRow = []
		for i in range(9):
			x1 = i*CellWidth
			y1 = j*CellHeight
			x2 = (i+1)*CellWidth
			y2 = (j+1)*CellHeight

			CellImage = InputImgProcess[y1:y2 , x1:x2]
			if np.count_nonzero(CellImage) < 20:
				Num = 0
			else:
				CellImage = cv2.resize(CellImage , (28,28) , interpolation=cv2.INTER_AREA)
				CellImage = Transform(CellImage)
				CellImage = CellImage.unsqueeze(0)
				CellImage = CellImage.to(device)
				with torch.no_grad():
					output = model(CellImage)
					_,prediction = torch.max(output,dim=1)
					Num = prediction.item()

			CellRow.append(Num)
		Cells.append(CellRow)

	_,OutputImgEncode = cv2.imencode('.png',OutputImg)
	OutputImgEncode = base64.b64encode(OutputImgEncode).decode('utf-8')
	OutputImgEncode = "data:image/png;base64,"+OutputImgEncode

	return Cells,OutputImgEncode

#Solve Puzzle

def FindNextEmpty(Puzzle):
	for row in range(9):
		for col in range(9):
			if Puzzle[row][col] == 0:
				return row,col
	return None,None

def IsValid(Puzzle , guess , row , col):
	#Row
	if guess in Puzzle[row]:
		return False
	
	#Column
	Col = []
	for i in range(9):
		Col.append(Puzzle[i][col])
	if guess in Col:
		return False
	
	#Grid
	RowStart = (row//3)*3
	ColStart = (col//3)*3

	for r in range(RowStart , RowStart+3):
		for c in range(ColStart , ColStart+3):
			if guess == Puzzle[r][c]:
				return False

	return True

def SolvePuzzle(Puzzle):
	row,col = FindNextEmpty(Puzzle)
	
	if row is None:
		return True
	
	for guess in range(1,10):
		if (IsValid(Puzzle,guess,row,col)):
			Puzzle[row][col] = guess

			yield {"type":"update","row":row,"col":col,"val":guess}

			if (yield from SolvePuzzle(Puzzle)):
				return True
			
		Puzzle[row][col] = 0
		yield {"type":"update","row":row,"col":col,"val":0}
	return False