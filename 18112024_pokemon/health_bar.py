from PIL import Image, ImageDraw
from dataclasses import dataclass
from typing import Tuple, Literal
from dotenv import load_dotenv
import os
from imagekitio import ImageKit
from imagekitio.models.UploadFileRequestOptions import UploadFileRequestOptions
import base64
from io import BytesIO
import time

load_dotenv()

@dataclass
class HealthBar:
    x: int
    y: int
    width: int = 290
    height: int = 16
    align_right: bool = False

    def draw_func(self, draw: ImageDraw.Draw, current_health: float, max_health: float) -> None:
        """Draw a health bar on the given ImageDraw object."""
        health_ratio = current_health / max_health
        filled_width = int(self.width * health_ratio)

        # Draw outline
        draw.rounded_rectangle(
            [self.x - 2, self.y - 2, self.x + self.width + 2, self.y + self.height + 2],
            radius=30, outline="white", width=2
        )
        
        # Draw white background
        draw.rectangle(
            [self.x, self.y, self.x + self.width, self.y + self.height],
            fill="white"
        )
        
        # Draw health portion if there's any health left
        if filled_width > 0:
            # Determine color and radius based on health ratio
            color = self._get_health_color(health_ratio)
            radius = 10 if health_ratio <= 0.2 else 30
            
            # Calculate x position based on alignment
            filled_x = self.x + (self.width - filled_width) if self.align_right else self.x
            
            draw.rounded_rectangle(
                [filled_x, self.y, filled_x + filled_width, self.y + self.height],
                radius=radius, fill=color, outline=color
            )

    @staticmethod
    def _get_health_color(ratio: float) -> Literal["red", "yellow", "green"]:
        if ratio <= 0.2:
            return "red"
        elif ratio <= 0.5:
            return "yellow"
        return "green"

def upload_to_imagekit(file_path: str) -> str:
    """
    Upload an image to ImageKit and return the URL.
    Requires IMAGEKIT_PRIVATE_KEY, IMAGEKIT_PUBLIC_KEY, and IMAGEKIT_URL_ENDPOINT in .env
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
    
    try:
        # Read and encode the file
        with open(file_path, 'rb') as f:
            file_data = f.read()
            base64_data = base64.b64encode(file_data).decode('utf-8')
            print(f"Original file size: {len(file_data)}, Base64 size: {len(base64_data)}")

        imagekit = ImageKit(
            private_key=os.getenv('IMAGEKIT_PRIVATE_KEY'),
            public_key=os.getenv('IMAGEKIT_PUBLIC_KEY'),
            url_endpoint=os.getenv('IMAGEKIT_URL_ENDPOINT')
        )
        
        print("Attempting to upload file...")
        upload_response = imagekit.upload(
            file=base64_data,
            file_name=os.path.basename(file_path),
            options=UploadFileRequestOptions(
                use_unique_file_name=True,
                is_private_file=False,
            )
        )
        
        print(f"Upload response received: {upload_response.__dict__}")

        if upload_response.error is not None:
            raise Exception(f"ImageKit upload error: {upload_response.error}")

        if not upload_response.url:
            raise Exception("Upload succeeded but no URL was returned")

        return upload_response.url

    except Exception as e:
        print(f"Detailed error during upload: {str(e)}")
        raise

def overlay_health_bars(
    background_image_path: str,
    enemy_health: float,
    enemy_max_health: float,
    user_health: float,
    user_max_health: float,
    upload: bool = True
) -> str:
    """
    Overlay health bars on the background image and upload directly to ImageKit.
    Returns the ImageKit URL.
    """
    # Open the background image
    background = Image.open(background_image_path).convert("RGBA")
    
    # Create transparent overlay
    overlay = Image.new("RGBA", background.size, (255, 255, 255, 0))
    draw = ImageDraw.Draw(overlay)

    # Create and draw health bars
    enemy_bar = HealthBar(x=176, y=134, align_right=True)
    user_bar = HealthBar(x=782, y=801)

    enemy_bar.draw_func(draw, enemy_health, enemy_max_health)
    user_bar.draw_func(draw, user_health, user_max_health)

    # Combine images
    combined = Image.alpha_composite(background, overlay)
    
    # Convert to RGB
    final_image = combined.convert("RGB")
    
    if upload:
        try:
            # Save to bytes buffer instead of file
            buffer = BytesIO()
            final_image.save(buffer, format="PNG")
            image_bytes = buffer.getvalue()
            buffer.close()
            
            # Convert to base64 and upload
            base64_data = base64.b64encode(image_bytes).decode('utf-8')
            
            imagekit = ImageKit(
                private_key=os.getenv('IMAGEKIT_PRIVATE_KEY'),
                public_key=os.getenv('IMAGEKIT_PUBLIC_KEY'),
                url_endpoint=os.getenv('IMAGEKIT_URL_ENDPOINT')
            )
            
            upload_response = imagekit.upload(
                file=base64_data,
                file_name=f"battle_image_{int(time.time())}.png",
                options=UploadFileRequestOptions(
                    use_unique_file_name=True,
                    is_private_file=False,
                )
            )
            
            if upload_response.error is not None:
                raise Exception(f"ImageKit upload error: {upload_response.error}")
            
            url = upload_response.url
        except Exception as e:
            print(f"Failed to upload image: {e}")
            raise
        finally:
            # Clean up
            background.close()
            overlay.close()
            combined.close()
            final_image.close()
            
        return url
    
    raise ValueError("Must upload=True when not saving locally") 