from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import pandas as pd
import os
import shutil
import base64
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import JSONResponse
from deepface import DeepFace  # For precise facial recognition
import os
import shutil
from datetime import datetime
import pandas as pd
os.environ["CUDA_VISIBLE_DEVICES"] = "-1"

import openpyxl
app = FastAPI()
UPLOAD_FOLDER = 'upload_image'


if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)




class CheckOut(BaseModel):
    userid:str
    date:str
    check_out_time:str

class Duration(BaseModel):
    date:str
    lat: str
    long: str
    check_in_time: str
    check_out_time: str
    # duration:str


@app.post("/getname")
def read_root(name:str):
    return {"message": f"Hello, World {name}"}


@app.post("/login")
def read_root(username: str, password: str):
    try:                                           
        # Load the Excel file
        df = pd.read_excel('./userdata.xlsx')

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
    df = pd.read_excel('./userdata2.xlsx')
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
        df.to_excel('./userdata2.xlsx', index=False)
        return {'message': 'if'}
    else:
        print(f"before :{len(df)}")
        # Insert a new row into the DataFrame
        df.loc[len(df)] = [useridinfo,lat, longi]
        print(f"After :{len(df)}")
        # Save the updated DataFrame to the Excel file
        df.to_excel('./userdata2.xlsx', index=False)
                
        return {'message': 'else'}



# app = FastAPI()
# UPLOAD_FOLDER = 'upload_image'

# Ensure UPLOAD_FOLDER exists
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Ensure attendance folder exists
if not os.path.exists("attendance"):
    os.makedirs("attendance")

@app.post("/check_in/")
async def check_in(
    file: UploadFile = File(...),
    userid: str = Form(...),
    lat: str = Form(...),
    long: str = Form(...),
    date: str = Form(...),
    check_in_time: str = Form(...)
):
    try:
        # Generate a unique, readable filename for the attendance image
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        attendance_filename = f"{userid}_checkin_{timestamp}.jpg"
        attendance_image_path = os.path.join("attendance", attendance_filename)

        # Save the uploaded image to the attendance folder
        # USER CHECK: Ensure "attendance" folder has write permissions
        with open(attendance_image_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Find the reference image in UPLOAD_FOLDER based on provided userid
        reference_filename = f"{userid}.jpg"
        reference_image_path = os.path.join(UPLOAD_FOLDER, reference_filename)

        # Check if reference image exists
        # USER CHECK: Verify reference images are named as "userid.jpg" or adjust extensions
        if not os.path.exists(reference_image_path):
            for ext in ['.png', '.jpeg']:  # Add or remove extensions if needed
                alt_path = os.path.join(UPLOAD_FOLDER, f"{userid}{ext}")
                if os.path.exists(alt_path):
                    reference_image_path = alt_path
                    break

        if not os.path.exists(reference_image_path):
            return {"message": "No check-in details updated, reference image not found for this user"}

        # Use DeepFace for precise facial verification
        try:
            result = DeepFace.verify(reference_image_path, attendance_image_path, model_name="Facenet512",backend="dlib")
            if result.get('verified', False):  # Default to False if 'verified' key is missing
                # Images match, update Excel with all provided details
                df = pd.read_excel('./details1.xlsx')
                df.loc[len(df)] = [userid, date, lat, long, check_in_time, '']
                df.to_excel('./details1.xlsx', index=False)
                return {"message": f"Check-in recorded for user {userid}!", "file_path": attendance_image_path}
            else:
                # Images don't match, no update to Excel
                return {"message": "No check-in details updated, user invalid"}
        except Exception as e:
            return {"message": f"No check-in details updated, image comparison failed: {str(e)}"}

    except Exception as e:
        return {"message": f"No check-in details updated, upload failed: {str(e)}"}
        
@app.post("/check_out/")
def check_out(check_out: CheckOut):
        try:
            # Load the Excel file
            df = pd.read_excel('./details1.xlsx')
            
             # Ensure the USERNAME and PASSWORD columns are treated as strings
            df['userid'] = df['userid'].astype(str).str.strip().str.lower()
            df['date'] = df['date'].astype(str).str.strip().str.lower()           

            # Assuming the check-in time is stored in the last row of the DataFrame
            userid=str(check_out.userid)
            date=str(check_out.date)
            check_out_time=str(check_out.check_out_time)

            userid = userid.strip().lower()
            date = date.strip().lower()

             # Filter the DataFrame to find the matching row
            matching_row = df[(df['userid'] == userid) & (df['date'] == date)]
           
            # Step 3: Update a specific column for the filtered rows
            df.loc[matching_row.index, 'check out time'] = check_out_time 
 
            df.to_excel('./details1.xlsx', index=False)

            return {"message": "Check-out time recorded successfully!"}
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")



@app.post("/duration/")
def duration(userid: str, date: str = None):  # Made date optional with default None
    # Check if file exists
    if not os.path.exists('./details1.xlsx'):
        raise HTTPException(status_code=500, detail="Excel file 'FaceDetection-main/details1.xlsx' not found. Please create it with your data.")
    
    # Load the Excel file
    try:
        df = pd.read_excel('./details1.xlsx')
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Cannot load Excel file: {str(e)}")
    
    # Make userid and date consistent
    df['userid'] = df['userid'].astype(str).str.strip().str.lower()
    df['date'] = df['date'].astype(str).str.replace('.', '/').str.strip()
    
    # Filter for the specific user
    matching_row = df[df['userid'] == userid.lower().strip()]
    
    # If date is provided, filter by date
    if date is not None:
        matching_row = matching_row[matching_row['date'] == date.replace('.', '/').strip()]
    
    # Check if any matching row is found
    if matching_row.empty:
        raise HTTPException(status_code=404, detail="No data found for this user on the specified date or in history.")
    
    # Convert numeric times to HH:MM:SS (keep this simple)
    matching_row['check in time'] = matching_row['check in time'].apply(
        lambda x: f"{int(float(x)) if pd.notna(x) else None}:00:00" if isinstance(x, (int, float)) else x
    )
    matching_row['check out time'] = matching_row['check out time'].apply(
        lambda x: f"{int(float(x)) if pd.notna(x) else None}:00:00" if isinstance(x, (int, float)) else x
    )
    
    # Convert times to datetime
    matching_row['check in time'] = pd.to_datetime(matching_row['check in time'], format='%H:%M:%S', errors='coerce')
    matching_row['check out time'] = pd.to_datetime(matching_row['check out time'], format='%H:%M:%S', errors='coerce')
    
    # Calculate duration
    matching_row['duration'] = matching_row['check out time'] - matching_row['check in time']

    # After calculating duration
    matching_row['duration'] = matching_row['duration'].apply(
    lambda x: f"{int(x.total_seconds() // 3600)} hours and {int((x.total_seconds() % 3600) // 60)} minutes" if pd.notna(x) else None
)
    
    # Return the result
    return matching_row.to_dict('records')

@app.post("/get_location_times/")
def get_location_times(userid: str, date: str):
    # Check if the Excel file exists
    if not os.path.exists('./details1.xlsx'):
        raise HTTPException(status_code=500, detail="Excel file 'details1.xlsx' not found. Please create it with your data.")
    
    # Load the Excel file
    try:
        df = pd.read_excel('./details1.xlsx')
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Cannot load Excel file: {str(e)}")
    
    # Make userid and date consistent
    df['userid'] = df['userid'].astype(str).str.strip().str.lower()
    df['date'] = df['date'].astype(str).str.replace('.', '/').str.strip()
    
    # Filter for the specific user and date
    matching_row = df[(df['userid'] == userid.lower().strip()) & (df['date'] == date.replace('.', '/').strip())]
    
    # Check if any matching row is found
    if matching_row.empty:
        raise HTTPException(status_code=404, detail="No data found for this user on the specified date.")
    
    # Return only the requested fields
    result = matching_row[['userid', 'date', 'lat', 'long', 'check in time', 'check out time']].to_dict('records')
    
    return result
 