# Fal.ai Image Captioner

A simple Python script to automatically generate captions for images in a local folder using the [Fal.ai](https://fal.ai/) Florence-2 Large model API.

## Features

* Scans a specified local directory for image files (`.jpg`, `.jpeg`, `.png`, `.webp`).
* Sends images to the Fal.ai Florence-2 Large API to generate descriptive captions.
* Resizes images automatically if they exceed size limits before uploading.
* Saves the generated caption into a text file (`.txt`) with the same name as the image (e.g., `my_image.jpg` -> `my_image.txt`).
* Skips processing if a corresponding `.txt` caption file already exists.
* Includes a small delay between API calls to help avoid rate limits.

## Prerequisites

* Python 3.x
* A Fal.ai API Key ([Get one here](https://fal.ai/))

## Setup

1.  **Clone the repository:**
    ```bash
    git clone <your-repo-url>
    cd <your-repo-name>
    ```
2.  **Install dependencies:**
    The script attempts to install Pillow automatically if missing, but you might need `requests` as well.
    ```bash
    pip install requests Pillow
    ```
    *(Alternatively, create a `requirements.txt` file with `requests` and `Pillow` and run `pip install -r requirements.txt`)*

3.  **Configure the script (`caption_images.py`):**
    * Set `IMAGE_FOLDER_NAME`: Change the value of this variable (default is `"images"`) if your image folder has a different name. The folder should be located in the same directory as the script.
    * Set `FAL_API_KEY`: Replace `"Insert your API key here"` with your actual Fal.ai API key.
      ```python
      # ADD YOUR FAL.AI API KEY HERE:
      FAL_API_KEY = "Insert your API key here"
      ```

## Usage

1.  Create the image folder specified by `IMAGE_FOLDER_NAME` (e.g., `images/`) in the same directory as the script.
2.  Place the images you want to caption inside this folder.
3.  Run the script from your terminal:
    ```bash
    python caption_images.py
    ```
4.  The script will process each image (if no `.txt` file exists) and save the generated captions in corresponding `.txt` files within the same folder.

## Dependencies

* `requests`
* `Pillow`