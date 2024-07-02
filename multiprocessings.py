import os
from rembg import remove
from multiprocessing import Pool,cpu_count

def remove_background_multiprocess(image_path):
    input_path = os.path.join("input", image_path)
    output_path = os.path.join("output", f"no_bg_process_{os.path.basename(image_path)}")

    try:
        with open(input_path, 'rb') as input_file, open(output_path, 'wb') as output_file:
            input_data = input_file.read()
            output_data = remove(input_data)
            output_file.write(output_data)
        
        return f"Processed {image_path} with multiprocessing"
    except Exception as e:
        return f"Failed to process {image_path} with multiprocessing: {str(e)}"

if __name__ == "__main__":
    os.makedirs("output", exist_ok=True)
    
    image_paths = [filename for filename in os.listdir("input") if filename.lower().endswith(('.jpeg', '.jpg', '.png'))]

    num_processes = cpu_count()  # Jumlah proses maksimum yang ingin Anda gunakan
    print(f"Using {num_processes} processes for multiprocessing.")

    with Pool(processes=4) as pool_process:
        results_process = pool_process.map(remove_background_multiprocess, image_paths)
        
    for result in results_process:
        print(result)

    print("Finished processing all images with multiprocessing.")
