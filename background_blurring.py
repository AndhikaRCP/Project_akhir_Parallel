from rembg import remove as removebg
from PIL import Image, ImageFilter
from io import BytesIO

class BackgroundBlurring :
    def blurring_bg(image, blur_radius=10):
        try:
            input_data = BytesIO()
            image.save(input_data, format='PNG')
            input_data.seek(0)
            foreground_img = Image.open(BytesIO(removebg(input_data.read(), alpha_matting=True)))
            blurred_original = image.filter(ImageFilter.GaussianBlur(radius=blur_radius))
            final_img = Image.alpha_composite(blurred_original.convert('RGBA'), foreground_img)
            
            return final_img
        except Exception as e:
            print(f"Error processing image: {e}")
            return None

