from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
import pandas as pd
import os
import shutil

app = FastAPI()
UPLOAD_FOLDER = 'upload_image'




@app.post("/getname")
def read_root(name:str):
    return {"message": f"Hello, World {name}"}


@app.post("/login")
def read_root(username: str, password: str):
    try:
        df = pd.read_excel('userdata.xlsx')
        print(f"LEN : {len(df)}")

        # Filter the DataFrame to find the matching row
        matching_row = df.loc[(df['USERNAME'] == username) & (df['PASSWORD'] == password)]
        
        # If a match is found, return the entire row
        if not matching_row.empty:
            return {'message': 'Login successful', 'row': matching_row.to_dict('records')[0]}
        else:
            return {'message': 'Invalid username or password'}
    except Exception as e:
        return {'message': f'An error occurred: {str(e)}'}

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
    
    
    
