# caption_images.py 

 import os 
 import pathlib 
 import mimetypes 
 import base64 
 import time 
 import requests 
 import json 
 from PIL import Image 
 from io import BytesIO 

 # --- Configuration --- 
 # IMPORTANT: Set this to the name of your image folder in the root directory 
 IMAGE_FOLDER_NAME = "images"  
 # ADD YOUR FAL.AI API KEY HERE: 
 FAL_API_KEY = "Insert your API key here"  
 # --- End Configuration --- 

 # Fal.ai API endpoint for Florence-2 caption 
 # Try the API endpoint format from the docs more precisely 
 FLORENCE_API_URL = "https://fal.run/fal-ai/florence-2-large/caption" 

 # Define supported image file extensions 
 SUPPORTED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"} 

 # Get the absolute path to the image folder 
 script_dir = pathlib.Path(__file__).parent.resolve() 
 image_folder_path = script_dir / IMAGE_FOLDER_NAME 

 def resize_image_if_needed(image_bytes, max_size=(1024, 1024), max_file_size=1024*1024*5):  # 5MB max 
     """Resize image if it's too large, return new bytes""" 
     if len(image_bytes) <= max_file_size: 
         try: 
             # Check dimensions without fully decoding 
             img = Image.open(BytesIO(image_bytes)) 
             width, height = img.size 
             if width <= max_size[0] and height <= max_size[1]: 
                 return image_bytes  # No resize needed 
         except Exception as e: 
             print(f"   Warning: Could not check image dimensions: {e}") 
             return image_bytes  # Return original if we can't process 

     # Resize the image 
     try: 
         img = Image.open(BytesIO(image_bytes)) 
         img.thumbnail(max_size, Image.LANCZOS) 
         output = BytesIO() 
         format = img.format or 'JPEG' 
         img.save(output, format=format, quality=85) 
         output.seek(0) 
         print(f"   Image resized from {len(image_bytes)} bytes to {output.getbuffer().nbytes} bytes") 
         return output.getbuffer() 
     except Exception as e: 
         print(f"   Warning: Failed to resize image: {e}") 
         return image_bytes  # Return original if resize fails 

 def process_images(): 
     """ 
     Finds images, generates captions using Fal.ai, and saves them as text files. 
     """ 
     print(f"Looking for images in: {image_folder_path}") 

     if not image_folder_path.is_dir(): 
         print(f"Error: Folder not found at {image_folder_path}") 
         print("Please make sure the IMAGE_FOLDER_NAME is set correctly.") 
         return 

     image_files = [ 
         f for f in image_folder_path.iterdir()  
         if f.is_file() and f.suffix.lower() in SUPPORTED_EXTENSIONS 
     ] 

     if not image_files: 
         print("No images found in the folder.") 
         return 

     print(f"Found {len(image_files)} image(s) to process.") 

     # Set up the headers for API requests 
     headers = { 
         "Authorization": f"Key {FAL_API_KEY}", 
         "Content-Type": "application/json", 
         "Accept": "application/json" 
     } 

     for image_path in image_files: 
         caption_path = image_path.with_suffix(".txt") 

         if caption_path.exists(): 
             print(f"Skipping '{image_path.name}', caption file already exists.") 
             continue 

         print(f"Processing '{image_path.name}'...") 

         try: 
             # 1. Read image data 
             image_bytes = image_path.read_bytes() 
             
             # 2. Check if image needs resizing 
             image_bytes = resize_image_if_needed(image_bytes) 
             
             # 3. Encode image as base64 
             base64_encoded_data = base64.b64encode(image_bytes) 
             base64_string = base64_encoded_data.decode('utf-8') 
             
             # 4. Create data URI 
             mime_type, _ = mimetypes.guess_type(image_path) 
             if not mime_type: 
                 mime_type = 'image/jpeg'  # Safer default for images 
             data_uri = f"data:{mime_type};base64,{base64_string}" 
             
             # 5. Try different payload formats based on API expectations 
             # Format 1: Based on the API documentation structure 
             payload = { 
                 "image_url": data_uri 
             } 
             
             # 6. Submit request to Fal.ai API 
             print(f"   Sending request to Fal.ai API...") 
             response = requests.post(FLORENCE_API_URL, headers=headers, json=payload) 
             
             # 7. Check for errors with more detailed error reporting 
             try: 
                 response.raise_for_status() 
             except requests.exceptions.HTTPError as e: 
                 # Try to get the JSON error message if available 
                 error_detail = "" 
                 try: 
                     error_json = response.json() 
                     error_detail = f" Details: {error_json}" 
                 except: 
                     error_detail = f" Response text: {response.text[:200]}" 
                 
                 raise requests.exceptions.HTTPError(f"{e}{error_detail}") 
             
             # 8. Parse response 
             result = response.json() 
             print(f"   Response received: {result}") 
             
             # 9. Extract caption from various possible response structures 
             caption = None 
             
             # Try different locations where the caption might be found 
             if isinstance(result, dict): 
                 # Direct results field 
                 if 'results' in result: 
                     caption = result['results'] 
                 # Nested data.results 
                 elif 'data' in result and isinstance(result['data'], dict): 
                     caption = result['data'].get('results') 
                 # Direct result field (singular) 
                 elif 'result' in result: 
                     caption = result['result'] 
                 # If it's the only string in the response 
                 elif len(result) == 1 and isinstance(next(iter(result.values())), str): 
                     caption = next(iter(result.values())) 
             
             if caption is None: 
                 print(f"   Error: Could not find caption in API response for {image_path.name}") 
                 print(f"   Full response: {result}") 
                 continue 
             
             # 10. Save caption to file 
             caption_path.write_text(caption, encoding='utf-8') 
             print(f"   Saved caption to '{caption_path.name}'") 
             
             # 11. Add a small delay to avoid rate limiting 
             time.sleep(1.0)  # Increased delay slightly 
                  
         except requests.exceptions.RequestException as e: 
             print(f"   Error processing '{image_path.name}': Request failed - {e}") 
         except Exception as e: 
             print(f"   Error processing '{image_path.name}': {e}") 

     print("Finished processing all images.") 

 if __name__ == "__main__": 
     # Try to install PIL if not available 
     try: 
         from PIL import Image 
     except ImportError: 
         print("Installing required packages...") 
         import subprocess 
         subprocess.check_call(["pip", "install", "pillow"]) 
         from PIL import Image 

     # Initialize mimetypes database 
     mimetypes.init() 
     
     # Process the images 
     process_images()