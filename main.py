from flask import Flask, render_template, request, send_file, jsonify
from werkzeug.utils import secure_filename
from PIL import Image
import os
from io import BytesIO
from pyunpack import Archive
from rembg import remove as removebg
import tempfile
import cv2
from image_colorize import ImageColorize
import numpy as np
from background_blurring import BackgroundBlurring
import zipfile

app = Flask(__name__, template_folder="pages")

# List format yang ado di Pillow
FORMAT_MAPPING = {
    '.blp': 'BLP',
    '.bmp': 'BMP',
    '.dib': 'BMP',
    '.bufr': 'BUFR',
    '.cur': 'CUR',
    '.pcx': 'PCX',
    '.dcx': 'DCX',
    '.dds': 'DDS',
    '.ps': 'EPS',
    '.eps': 'EPS',
    '.fit': 'FITS',
    '.fits': 'FITS',
    '.fli': 'FLI',
    '.flc': 'FLI',
    '.fpx': 'FPX',
    '.ftc': 'FTEX',
    '.ftu': 'FTEX',
    '.gbr': 'GBR',
    '.gif': 'GIF',
    '.grib': 'GRIB',
    '.h5': 'HDF5',
    '.hdf': 'HDF5',
    '.png': 'PNG',
    '.apng': 'PNG',
    '.jp2': 'JPEG2000',
    '.j2k': 'JPEG2000',
    '.jpc': 'JPEG2000',
    '.jpf': 'JPEG2000',
    '.jpx': 'JPEG2000',
    '.jpe': 'JPEG',
    '.jpg': 'JPEG',
    '.jpeg': 'JPEG',
    '.mpo': 'MPO',
    '.msp': 'MSP',
    '.palm': 'PALM',
    '.pcd': 'PCD',
    '.pdf': 'PDF',
    '.pxr': 'PIXAR',
    '.pbm': 'PPM',
    '.pgm': 'PPM',
    '.ppm': 'PPM',
    '.psd': 'PSD',
    '.bw': 'SGI',
    '.rgb': 'SGI',
    '.rgba': 'SGI',
    '.sgi': 'SGI',
    '.ras': 'SUN',
    '.tga': 'TGA',
    '.icb': 'TGA',
    '.vda': 'TGA',
    '.vst': 'TGA',
    '.tif': 'TIFF',
    '.tiff': 'TIFF',
    '.webp': 'WEBP'
}

def get_pillow_format(file_ext):
    file_ext = file_ext.lower()
    return FORMAT_MAPPING.get(f'.{file_ext}', 'JPEG') 

def processImageBasedOnSelectedFeature(image, selectedFeature="", imageExt=""):
    if selectedFeature == "remove_bg":
        image = removebg(image)
        imageExt = "png"
    elif selectedFeature == "blurring_bg":
        image = BackgroundBlurring.blurring_bg(image)
        imageExt = "png"
    elif selectedFeature == "colorize":
        image = np.array(image)
        image = ImageColorize.imageColorize(image)
    elif selectedFeature == "grayscale":
        if isinstance(image, Image.Image):
            image = image.convert('L')

    if isinstance(image, np.ndarray):
        _, buffer = cv2.imencode(f'.{imageExt}', image)
        image_io = BytesIO(buffer)
    elif isinstance(image, Image.Image):
        image_io = BytesIO()
        pillow_format = get_pillow_format(imageExt)
        image.save(image_io, format=pillow_format)
        image_io.seek(0)
    return image_io, imageExt

@app.route('/')
def index():
    return render_template('upload.html')

@app.route('/upload', methods=['POST'])
def upload():
    if 'imageFile' not in request.files:
        return jsonify(status="error", message="No file part")
    file = request.files['imageFile']
    
    if file.filename == '':
        return jsonify(status="error", message="No selected file")
    else:
        isImageFile = file.content_type.__contains__("image/")
        selectedFeature = request.form.get("selectFitur")
        if isImageFile:
            image = Image.open(file.stream)
            imageExt = os.path.splitext(file.filename)[1][1:]  
            imageNameWithNoExt = os.path.splitext(file.filename)[0]  
            image_io, newImageExt = processImageBasedOnSelectedFeature(image, selectedFeature, imageExt)
            output_path = os.path.join(tempfile.gettempdir(), f'{imageNameWithNoExt}.{newImageExt}')
            with open(output_path, 'wb') as f:
                f.write(image_io.getbuffer())
            return jsonify(status="success", filename=f'{imageNameWithNoExt}.{newImageExt}')
        else:
            if file:
                filename = secure_filename(file.filename)
                file_ext = filename.rsplit('.', 1)[1].lower()
                
                if file_ext in ['zip', 'rar', '7z']:
                    with tempfile.TemporaryDirectory() as temp_dir:
                        archive_path = os.path.join(temp_dir, filename)
                        file.save(archive_path)
                        Archive(archive_path).extractall(temp_dir)
                        
                        processed_images = []
                        for root, _, files in os.walk(temp_dir):
                            for f in files:
                                file_path = os.path.join(root, f)
                                try:
                                    img = Image.open(file_path)
                                    imageExt = f.rsplit('.', 1)[1].lower()
                                    imageNameWithNoExt = f.rsplit('.')[0].lower()
                                    image_io, newImageExt = processImageBasedOnSelectedFeature(img, selectedFeature, imageExt)
                                    newImageName = f'{imageNameWithNoExt}.{newImageExt}'
                                    processed_images.append((newImageName, image_io))
                                except IOError:
                                    continue
                        
                        zip_io = BytesIO()
                        with zipfile.ZipFile(zip_io, 'w') as zip_file:
                            for file_name, image_io in processed_images:
                                zip_file.writestr(file_name, image_io.getvalue())
                        zip_io.seek(0)
                        zip_path = os.path.join(tempfile.gettempdir(), 'processed_images.zip')
                        with open(zip_path, 'wb') as f:
                            f.write(zip_io.getbuffer())
                        
                        return jsonify(status="success", filename='processed_images.zip')
            
            return jsonify(status="error", message="File not supported")

@app.route('/success')
def success():
    filename = request.args.get('filename')
    return render_template('success.html', filename=filename)

@app.route('/download/<filename>')
def download(filename):
    file_path = os.path.join(tempfile.gettempdir(), filename)
    return send_file(file_path, as_attachment=True, download_name=filename)

if __name__ == '__main__':
    app.run(debug=True)
