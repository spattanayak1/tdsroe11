from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
import pdfplumber
import io

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/analyze")
async def analyze(file: UploadFile = File(...)):
    if file.content_type != "application/pdf":
        return {"error": "File must be a PDF"}

    contents = await file.read()
    total_sum = 0.0

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
                    continue

                for row in table[1:]:
                    if row and len(row) > max(item_idx, total_idx):
                        item = row[item_idx]
                        total = row[total_idx]
                        if item and "doodad" in item.lower():
                            try:
                                total_cleaned = total.replace("$", "").replace(",", "").strip()
                                total_sum += float(total_cleaned)
                            except:
                                continue

    return {"sum": round(total_sum, 2)}
