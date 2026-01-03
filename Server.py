from fastapi import FastAPI, UploadFile, File, WebSocket
from fastapi.staticfiles import StaticFiles
import uvicorn
import numpy as np
import cv2
import Sudoku

app = FastAPI()

@app.post("/process")
async def Process(InputFile: UploadFile = File(...)):
	FileContents = await InputFile.read()
	FileContents = np.frombuffer(FileContents,np.uint8)
	InputImg = cv2.imdecode(FileContents,cv2.IMREAD_COLOR)
	
	try:
		Cells,OutputImage = Sudoku.ProcessAndExtract(InputImg)
		return {
			"Image":OutputImage,
			"Cells":Cells,
			"Ret":True
		}
	except Exception as e:
		print(f"Error: {e}")
		return {
			"Ret":False,
			"Error":str(e)
		}
	
@app.websocket("/solve")
async def StreamSolve(Socket: WebSocket):
	await Socket.accept()

	Puzzle = await Socket.receive_json()
	
	for step in Sudoku.SolvePuzzle(Puzzle):

		await Socket.send_json(step)

	await Socket.close()

app.mount("/",StaticFiles(directory="FrontEnd",html=True),name="FrontEnd")