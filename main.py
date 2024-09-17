from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import pandas as pd
import os
import shutil
import base64

app = FastAPI()
UPLOAD_FOLDER = 'upload_image'


if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)


# Define a Pydantic model to receive base64 image data
class ImageUpload(BaseModel):
    image_base64: str
    filename: str

@app.post("/getname")
def read_root(name:str):
    return {"message": f"Hello, World {name}"}


@app.post("/login")
def read_root(username: str, password: str):
    try:
        # Load the Excel file
        df = pd.read_excel('userdata.xlsx')

        # Ensure the USERNAME and PASSWORD columns are treated as strings
        df['Username'] = df['Username'].astype(str).str.strip().str.lower()
        df['Password'] = df['Password'].astype(str).str.strip().str.lower()

        # Strip any extra spaces and convert inputs to lowercase for comparison
        username = username.strip().lower()
        password = password.strip().lower()

        # Filter the DataFrame to find the matching row
        matching_row = df.loc[(df['Username'] == username) & (df['Password'] == password)]

        # If a match is found, return the entire row
        if not matching_row.empty:
            return {"status": True, 'message': 'Login successful', 'row': matching_row.to_dict('records')[0]}
        else:
            return {"status": False,'message': 'Invalid username or password'}
    except Exception as e:
        return {"status": False,'message': f'An error occurred: {str(e)}'}

@app.post("/uploadimage/")
async def upload_image(file: UploadFile = File(...)):
    try:
        # Create a unique filename to avoid conflicts
        file_location = os.path.join(UPLOAD_FOLDER, file.filename)

        # Save the uploaded file to the specified directory
        with open(file_location, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Return a success message with the file location
        return {"filename": file.filename, "location": file_location}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return JSONResponse(content={"message": "Image uploaded successfully"}, status_code=201)

@app.post("/useridinfo")
def read_root(useridinfo: str, lat: str, longi: str):
    #try:
    # Load the Excel file
    df = pd.read_excel('userdata2.xlsx')
    print(f"useridinfo :{useridinfo}")
    ls=df['USERID'] == useridinfo
    print(f"ls : {ls}")
    print(df.head())

    matching_row = df.loc[(df['USERID'] == useridinfo)]
    print(f"matching_row : {matching_row.to_dict('records')}")
    if not matching_row.empty:
        # Update the latitude and longitude values
        df.loc[(df['USERID'] == useridinfo), 'LATITUDE'] = lat
        df.loc[(df['USERID'] == useridinfo), 'LONGITUDE'] = longi
            
        # Save the updated DataFrame to the Excel file
        df.to_excel('userdata2.xlsx', index=False)
        return {'message': 'if'}
    else:
        print(f"before :{len(df)}")
        # Insert a new row into the DataFrame
        df.loc[len(df)] = [useridinfo,lat, longi]
        print(f"After :{len(df)}")
        # Save the updated DataFrame to the Excel file
        df.to_excel('userdata2.xlsx', index=False)
                
        return {'message': 'else'}


@app.post("/uploadimage_base/")
async def upload_image(image_base64: str, filename: str):
    try:
        # Decode the base64 image
        image_bytes = base64.b64decode(image_base64)

        # Save the image to a file
        image_path = os.path.join(UPLOAD_FOLDER, filename)
        with open(image_path, "wb") as image_file:
            image_file.write(image_bytes)

        return {"message": f"Image {filename} uploaded successfully!", "file_path": image_path}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Image upload failed: {str(e)}")

    
    
    
