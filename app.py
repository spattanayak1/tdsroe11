from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
import pdfplumber
import io
import uvicorn

# Create FastAPI app
app = FastAPI()

# Enable CORS for all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Endpoint to analyze PDF
@app.post("/analyze")
async def analyze(file: UploadFile = File(...)):
    if file.content_type != "application/pdf":
        return {"error": "File must be a PDF"}

    contents = await file.read()
    total_sum = 0.0

    # Use pdfplumber to read PDF and extract tables
    with pdfplumber.open(io.BytesIO(contents)) as pdf:
        for page in pdf.pages:
            tables = page.extract_tables()
            for table in tables:
                if not table or not table[0]:
                    continue
                headers = table[0]
                try:
                    item_idx = headers.index("Item")
                    total_idx = headers.index("Total")
                except ValueError:
                    continue  # Skip tables without the required columns

                for row in table[1:]:
                    if row and len(row) > max(item_idx, total_idx):
                        item = row[item_idx]
                        total = row[total_idx]
                        if item and "doodad" in item.lower():
                            try:
                                total_cleaned = total.replace("$", "").replace(",", "").strip()
                                total_sum += float(total_cleaned)
                            except:
                                continue  # Ignore rows with invalid values

    return {"sum": round(total_sum, 2)}

# Run the server
if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
