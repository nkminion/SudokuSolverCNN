const UploadBtn = document.getElementById("Upload");
const FileInput = document.getElementById("FileInput");
const SudokuGrid = document.getElementById("SudokuGrid");
const StartBtn = document.getElementById("Start");
const PreviewPort = document.getElementById("Preview");

let Puzzle = [];

UploadBtn.addEventListener("click", function()
{
	FileInput.click();
});

FileInput.addEventListener("change", async function()
{
	if (FileInput && FileInput.files[0])
	{
		const File = FileInput.files[0];

		const data = new FormData();
		data.append("InputFile",File)

		try
		{
			const Response = await fetch("/process",{
				method: "POST",
				body: data
			});

			const Data = await Response.json();

			if (Data.Ret)
			{
				Puzzle = Data.Cells;
				CreateGrid(Data.Cells);
				PreviewPort.src = Data.Image;
				StartBtn.disabled = false;
			}
		}
		catch (error)
		{
			console.error("Error: ",error);
		}
	}
});

StartBtn.addEventListener("click", function()
{
	StartBtn.disabled = true;
	UploadBtn.disabled = true;

	const Socket = new WebSocket("/solve");

	Socket.onopen = function()
	{
		Socket.send(JSON.stringify(Puzzle));
	};

	Socket.onmessage = function(event)
	{
		const move = JSON.parse(event.data);

		const CellID = `cell-${move.row}-${move.col}`;
		const Cell = document.getElementById(CellID);

		if (Cell)
		{
			if (move.val == 0)
			{
				Cell.innerText = "";
			}
			else
			{
				Cell.innerText = move.val;
			}
		}
	};

	Socket.onclose = function()
	{
		alert("Puzzle Solved!");
		UploadBtn.disabled = false;
	};
});

function CreateGrid(Cells)
{
    SudokuGrid.innerHTML = ""; // Clear existing
    
    for (let i = 0; i < 9; i++)
	{
		for (let j = 0; j<9;j++)
		{
			let cell = document.createElement("div");
			cell.classList.add("Cell");
			
			cell.id = `cell-${i}-${j}`;

			if (Cells[i][j] != 0)
			{
				cell.innerText = Cells[i][j];
			}
			else
			{
				cell.innerText = "";
				cell.style.color = "#0083FF";
			}			

			SudokuGrid.appendChild(cell);
		}
    }
}

StartBtn.disabled = true;