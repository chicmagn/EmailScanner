from google_helper import GoogleHelper
import os
import fitz
from openai_helper import OpenAIHelper

google = GoogleHelper()
ai = OpenAIHelper()

def extract_vin_from_pdf(filepath):
    """Extract VINs from a PDF file."""
    try:
        # Open the PDF
        pdf_document = fitz.open(filepath)

        # Iterate through each page
        for page_number in range(len(pdf_document)):
            page = pdf_document.load_page(page_number)  # 0-based index
            page_pix_data = page.get_pixmap()  # Render page to a pixmap
            image_path = f'temp\\page_{page_number + 1}.png'
            page_pix_data.save(image_path)  # Save the pixmap as an image
            # Detect VIN from the image
            vin = ai.extract_vin_from_image(image_path)
            print(vin)
            if vin == "FALSE" or vin == None:
                print(f"Failed to detect VIN from page {page_number}.")
            else:
                # print(f"Detected VIN from page {page_number}: {vin}")
                save_vin(vin)
                
            os.remove(image_path)
        # Close the document
        pdf_document.close()
    except Exception as e:
        print(e)
        
def analyze():    
    store_dir = 'attachments'
    temp_dir = 'temp'
    client = google.authenticate_gsheet()
    google.open_sheet(client)
    # if not os.path.exists(store_dir):
    #     os.makedirs(store_dir)
    # if not os.path.exists(temp_dir):
    #     os.makedirs(temp_dir)
    # threads = google.do_google_stuff()
    # # Process messages
    # for message in threads:
    #     vin = ai.extract_vin_from_message(message)
    #     if vin == "FALSE" or vin == None:
    #         # print(f"Failed to detect VIN from image.")
    #         pass
    #     else:
    #         # print(f"Detected VIN from page {page_number}: {vin}")
    #         save_vin(vin)
            
    # Process downloaded attachments
    # for filename in os.listdir(store_dir):
    #     filepath = os.path.join(store_dir, filename)
        
    #     if filename.lower().endswith('.pdf'):
    #         print(filepath)
    #         extract_vin_from_pdf(filepath)
    #     elif filename.lower().endswith(('.png', '.jpg', '.jpeg')):
    #         vin = ai.extract_vin_from_image(filepath)
    #         if vin == "FALSE" or vin == None:
    #             # print(f"Failed to detect VIN from image.")
    #             pass
    #         else:
    #             # print(f"Detected VIN from page {page_number}: {vin}")
    #             save_vin(vin)
    #     else:
    #         print(f'Unsupported file type: {filename}')
    #         continue
    
def save_vin(text_to_append):
    # Define the file name
    file_name = 'result.txt'

    # Open the file in append mode
    with open(file_name, 'a') as file:
        file.write(text_to_append + "\n")
        
if __name__ == "__main__":
    analyze()