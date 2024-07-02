import os
from rembg import remove

def remove_background_sequential(image_path):
    input_path = os.path.join("input", image_path)
    output_path = os.path.join("output", f"no_bg_{os.path.basename(image_path)}")

    try:
        with open(input_path, 'rb') as input_file, open(output_path, 'wb') as output_file:
            input_data = input_file.read()
            output_data = remove(input_data)
            output_file.write(output_data)
        
        return f"Processed {image_path} sequentially"
    except Exception as e:
        return f"Failed to process {image_path} sequentially: {str(e)}"

if __name__ == "__main__":
    os.makedirs("output", exist_ok=True)
    
    image_paths = [filename for filename in os.listdir("input") if filename.lower().endswith(('.jpeg', '.jpg', '.png'))]

    for image_path in image_paths:
        result = remove_background_sequential(image_path)
        print(result)

    print("Finished processing all images sequentially.")
