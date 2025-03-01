import random
import requests
import json
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
import os
import subprocess
from pathlib import Path
import time
from io import BytesIO
import re
import signal
import sys

# Create necessary directories
os.makedirs('temp', exist_ok=True)
os.makedirs('output', exist_ok=True)
os.makedirs('temp/frames', exist_ok=True)
os.makedirs('assets', exist_ok=True)

def get_arabic_font():
    """Try different methods to get an Arabic-compatible font"""
    # Use the custom font path
    custom_path = r"/Users/fadil/OneDrive/Desktop/Amiri Regular.ttf"
    
    if os.path.exists(custom_path):
        return custom_path
    
    # Fallback options if the custom font is not found
    possible_paths = [
          # Windows (good Arabic support),
        'assets/arabic_font.ttf'  # Custom fallback
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            return path
    
    # If no font found, download a suitable one
    try:
        print("Downloading Arabic font...")
        font_url = "https://github.com/khaledhosny/amiri/raw/main/amiri-regular.ttf"
        response = requests.get(font_url)
        if response.status_code == 200:
            os.makedirs('assets', exist_ok=True)
            with open('assets/arabic_font.ttf', 'wb') as f:
                f.write(response.content)
            return 'assets/arabic_font.ttf'
    except Exception as e:
        print(f"Error downloading font: {e}")
    
    return None

def create_epic_background(width, height):
    """Create an epic, celestial background with particles and light rays"""
    # Base dark gradient background
    background = Image.new('RGB', (width, height), color=(10, 10, 30))
    draw = ImageDraw.Draw(background)
    
    # Create gradient effect
    for y in range(height):
        darkness = int(10 + (y / height) * 30)
        draw.line([(0, y), (width, y)], fill=(darkness, darkness, darkness + 20))
    
    # Add stars/particles (small white dots)
    for _ in range(500):
        x = random.randint(0, width)
        y = random.randint(0, height)
        size = random.randint(1, 3)
        brightness = random.randint(150, 255)
        draw.ellipse((x, y, x+size, y+size), fill=(brightness, brightness, brightness))
    
    # Add light rays emanating from center top
    center_x = width // 2
    for _ in range(20):
        angle = random.uniform(0, 3.14)  # Semi-circle angle
        length = random.randint(height//3, height//2)
        end_x = center_x + int(length * 1.5 * (random.random() - 0.5))
        end_y = int(length * 0.8)
        
        # Draw ray with gradient transparency
        for i in range(100):
            alpha = int(100 - i)
            if alpha <= 0:
                break
            ray_width = 3 + int(i/10)
            x_offset = int((end_x - center_x) * (i/100))
            y_offset = int((end_y) * (i/100))
            
            draw.ellipse(
                (center_x + x_offset - ray_width, 50 + y_offset - ray_width,
                 center_x + x_offset + ray_width, 50 + y_offset + ray_width),
                fill=(50, 50, 70, alpha)
            )
    
    # Apply blur for glow effect
    background = background.filter(ImageFilter.GaussianBlur(radius=2))
    
    # Enhance contrast
    enhancer = ImageEnhance.Contrast(background)
    background = enhancer.enhance(1.2)
    
    return background

def create_decorative_frame(width, height):
    """Create decorative Islamic-style border frame overlay"""
    frame = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(frame)
    
    # Border thickness
    border = 40
    inner_border = 20
    
    # Outer border
    draw.rectangle([(0, 0), (width, height)], outline=(210, 180, 140, 200), width=border)
    
    # Inner border with slightly different color
    draw.rectangle([(border+10, border+10), (width-border-10, height-border-10)], 
                  outline=(180, 160, 120, 180), width=inner_border)
    
    # Corner decorations
    corner_size = 150
    
    # Draw decorative corners
    for x, y in [(0, 0), (width-corner_size, 0), (0, height-corner_size), (width-corner_size, height-corner_size)]:
        # Draw circular pattern in corners
        center_x, center_y = x + corner_size//2, y + corner_size//2
        for r in range(20, 80, 15):
            draw.arc([center_x-r, center_y-r, center_x+r, center_y+r], 0, 360, fill=(200, 170, 100, 150), width=3)
        
        # Draw diagonal lines
        for i in range(0, corner_size, 20):
            draw.line([(x+i, y), (x, y+i)], fill=(220, 190, 120, 150), width=2)
    
    # Add subtle patterns along borders
    pattern_spacing = 80
    pattern_size = 30
    
    # Top and bottom borders
    for x in range(corner_size, width-corner_size, pattern_spacing):
        # Top border pattern
        draw.arc([x-pattern_size//2, border//2-pattern_size//2, 
                  x+pattern_size//2, border//2+pattern_size//2], 
                 0, 360, fill=(230, 200, 150, 180), width=2)
        
        # Bottom border pattern
        draw.arc([x-pattern_size//2, height-border//2-pattern_size//2, 
                  x+pattern_size//2, height-border//2+pattern_size//2], 
                 0, 360, fill=(230, 200, 150, 180), width=2)
    
    # Left and right borders
    for y in range(corner_size, height-corner_size, pattern_spacing):
        # Left border pattern
        draw.arc([border//2-pattern_size//2, y-pattern_size//2, 
                  border//2+pattern_size//2, y+pattern_size//2], 
                 0, 360, fill=(230, 200, 150, 180), width=2)
        
        # Right border pattern
        draw.arc([width-border//2-pattern_size//2, y-pattern_size//2, 
                  width-border//2+pattern_size//2, y+pattern_size//2], 
                 0, 360, fill=(230, 200, 150, 180), width=2)
    
    return frame

def wrap_text(draw, text, font, max_width):
    """Wrap text so it fits within the max width"""
    words = text.split()
    lines = []
    current_line = ""
    
    for word in words:
        test_line = current_line + " " + word if current_line else word
        bbox = draw.textbbox((0, 0), test_line, font=font)
        text_width = bbox[2] - bbox[0]
        
        if text_width <= max_width:
            current_line = test_line
        else:
            lines.append(current_line)
            current_line = word

    if current_line:  # Add the last line if it's not empty
        lines.append(current_line)
    return lines

def auto_scale_font(draw, text, max_width, max_height, initial_size, font_path):
    """Automatically scale the font size down to fit within max_width & max_height"""
    font_size = initial_size
    
    # Default font fallback if font_path is not found
    if not os.path.exists(font_path):
        print(f"Warning: Font path {font_path} not found, using default font")
        # Use a very basic fallback font that should exist
        font = ImageFont.load_default()
        lines = wrap_text(draw, text, font, max_width)
        return font, lines
    
    font = ImageFont.truetype(font_path, font_size)

    while font_size > 10:
        lines = wrap_text(draw, text, font, max_width)
        
        # Calculate line heights more safely
        line_heights = []
        for line in lines:
            bbox = font.getbbox(line)
            if bbox:
                line_heights.append(bbox[3] - bbox[1])
        
        if not line_heights:  # If we couldn't calculate heights, use a fallback
            total_height = font_size * len(lines)
        else:
            total_height = sum(line_heights)

        if total_height <= max_height:
            return font, lines  # If it fits, return the font and wrapped lines
        
        font_size -= 2  # Reduce font size and retry
        font = ImageFont.truetype(font_path, font_size)

    return font, lines  # Return the smallest possible fitting font

def draw_text_with_shadow(draw, position, text, font, fill_color=(255, 255, 255), shadow_color=(0, 0, 0), shadow_offset=2):
    """Draw text with shadow effect for better visibility"""
    x, y = position
    # Draw shadow
    draw.text((x+shadow_offset, y+shadow_offset), text, font=font, fill=shadow_color)
    # Draw main text
    draw.text((x, y), text, font=font, fill=fill_color)

def add_light_glow(image, text_mask, intensity=1.3):
    """Add a subtle glow effect around text using a mask"""
    # Create a new transparent image for the glow
    glow = Image.new('RGBA', image.size, (0, 0, 0, 0))
    glow_draw = ImageDraw.Draw(glow)
    
    # Draw the glow (expanded text in a light color)
    glow_draw.bitmap((0, 0), text_mask, fill=(255, 255, 200, 100))
    
    # Blur the glow
    glow = glow.filter(ImageFilter.GaussianBlur(radius=10))
    
    # Enhance the glow brightness
    enhancer = ImageEnhance.Brightness(glow)
    glow = enhancer.enhance(intensity)
    
    # Composite the glow onto the original image
    return Image.alpha_composite(image.convert('RGBA'), glow)

def create_frame(width, height, texts, positions, font_paths, font_sizes):
    """Create a single frame with wrapped and auto-scaled text with epic styling"""
    # Create epic background
    image = create_epic_background(width, height)
    
    # Convert to RGBA for compositing
    image = image.convert('RGBA')
    
    # Create a decorative border frame
    frame_overlay = create_decorative_frame(width, height)
    
    # Composite the frame onto the background
    image = Image.alpha_composite(image, frame_overlay)
    
    draw = ImageDraw.Draw(image)

    # Calculate text areas with proper padding for the border
    effective_width = width - 200  # Account for decorative border
    
    # Create text mask for glow effects
    text_mask = Image.new('L', (width, height), 0)
    mask_draw = ImageDraw.Draw(text_mask)

    # Process each text element
    for i, (text, position, font_path, initial_size) in enumerate(zip(texts, positions, font_paths, font_sizes)):
        # Skip empty text
        if not text:
            continue
            
        # Special smaller size for verse number
        if i == 1:  # Verse number
            max_height = 50  # Smaller height for verse number
        else:
            max_height = 200
            
        # Auto-scale the font
        font, wrapped_lines = auto_scale_font(draw, text, effective_width, max_height, initial_size, font_path)
        
        # Calculate y position for centered text
        # Use a safer way to calculate text height
        if hasattr(font, 'getbbox'):
            # For newer PIL versions
            try:
                line_heights = [font.getbbox(line)[3] - font.getbbox(line)[1] for line in wrapped_lines]
                total_text_height = sum(line_heights)
                line_height = total_text_height / len(wrapped_lines) if wrapped_lines else 0
            except (TypeError, AttributeError):
                # Fallback if getbbox fails
                line_height = font.size
                total_text_height = line_height * len(wrapped_lines)
        else:
            # Fallback for older PIL versions
            line_height = font.size
            total_text_height = line_height * len(wrapped_lines)
            
        y_offset = position - total_text_height // 2  # Centering

        # Draw each line with shadow for better visibility
        for line in wrapped_lines:
            # Get text width
            if hasattr(font, 'getbbox'):
                try:
                    bbox = draw.textbbox((0, 0), line, font=font)
                    text_width = bbox[2] - bbox[0]
                except (TypeError, AttributeError):
                    # Fallback
                    text_width = draw.textlength(line, font=font)
            else:
                # Even older PIL versions
                text_width = font.getsize(line)[0]
                
            x = (width - text_width) // 2  # Center horizontally
            
            # Draw text shadow on the main image
            draw_text_with_shadow(draw, (x, y_offset), line, font)
            
            # Also draw on the mask for glow effect
            mask_draw.text((x, y_offset), line, font=font, fill=255)
            
            y_offset += line_height  # Move to next line

    # Convert to RGB for saving
    # First add glow effect to text if possible
    try:
        image_with_glow = add_light_glow(image, text_mask)
        # Convert to RGB for final processing
        final_image = image_with_glow.convert('RGB')
    except Exception as e:
        print(f"Warning: Could not add glow effect: {e}")
        # Fallback to basic RGB conversion
        final_image = image.convert('RGB')
    
    # REMOVED vignette effect that was causing the black dome issue
    
    return final_image

def download_audio(url, output_path):
    """Download audio file"""
    response = requests.get(url)
    if response.status_code == 200:
        with open(output_path, 'wb') as f:
            f.write(response.content)
        return True
    return False

def enhance_audio(input_path, output_path):
    """Enhance audio quality without reverb"""
    # Check if ffmpeg is available
    try:
        subprocess.run(['ffmpeg', '-version'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
    except (subprocess.SubprocessError, FileNotFoundError):
        print("Warning: FFmpeg not found, using original audio")
        import shutil
        shutil.copy(input_path, output_path)
        return False
    
    # FFmpeg command to enhance audio without reverb
    # MODIFIED: Removed reverb effects (aecho) and simplified the audio processing
    cmd = [
        'ffmpeg', '-y',
        '-i', input_path,
        '-af', 'acompressor=threshold=0.125:ratio=2:attack=25:release=250:makeup=1.5,highpass=f=80,lowpass=f=16000,loudnorm',
        '-b:a', '256k',
        output_path
    ]
    
    try:
        subprocess.run(cmd, check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error enhancing audio: {e}")
        # Fallback to original audio
        import shutil
        shutil.copy(input_path, output_path)
        return False

def sanitize_filename(text):
    """Convert Arabic text to a safe filename"""
    # Remove special characters and limit length
    if not text:
        return "quran_verse"
    
    # Keep only the first few words (to avoid very long filenames)
    words = text.split()
    short_text = " ".join(words[:3]) if len(words) > 3 else text
    
    # Remove invalid filename characters
    invalid_chars = r'[<>:"/\\|?*\n\r\t]'
    sanitized = re.sub(invalid_chars, '', short_text)
    
    # Limit length (to avoid path too long errors)
    if len(sanitized) > 50:
        sanitized = sanitized[:50]
        
    # Ensure it's not empty
    if not sanitized.strip():
        return "quran_verse"
        
    return sanitized

def create_video(verse_data, surah_data):
    """Create epic video from frames and audio with enhanced effects"""
    width, height = 1920, 1080
    
    # Use the custom Arabic font path
    arabic_font_path = r"/Users/fadil/OneDrive/Desktop/Amiri Regular.ttf"
    
    # Verify the font exists, use fallback if necessary
    if not os.path.exists(arabic_font_path):
        print(f"Warning: Custom Arabic font not found at {arabic_font_path}, using fallback")
        arabic_font_path = get_arabic_font()
    
    # Try to find a suitable English font
    english_font_paths = [
        '/usr/share/fonts/truetype/msttcorefonts/Georgia.ttf',
        '/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf',
        '/System/Library/Fonts/Georgia.ttf',
        'C:/Windows/Fonts/georgia.ttf',
        'C:/Windows/Fonts/times.ttf',
        '/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf',
        '/usr/share/fonts/truetype/freefont/FreeSerif.ttf',
    ]
    
    english_font_path = None
    for path in english_font_paths:
        if os.path.exists(path):
            english_font_path = path
            break
    
    if not english_font_path:
        print("Warning: No English font found, using Arabic font for English text")
        english_font_path = arabic_font_path
    
    # Prepare text content with proper formatting
    # Fix for Arabic surah name: Make sure we're using surahNameArabic, with fallbacks
    surah_name_arabic = (
        surah_data.get('surahNameArabicLong') or 
        surah_data.get('surahNameArabic') or 
        f"سورة {surah_data.get('surahNo', '?')}"
    )
    
    arabic = verse_data.get('arabic1', '')  # Arabic text
    
    # Get English text safely
    english_text = verse_data.get('english', 'Translation not available')
    # Clean the English text
    english_text = english_text.replace('˹', '').replace('˺', '')
    
    # Safer way to get verse number
    verse_number = verse_data.get('ayahNo', '?')
    
    # Translation name
    translation_name = surah_data.get('surahNameTranslation', '')
    
    # Text configurations for more epic presentation
    texts = [
        f"{surah_name_arabic}" + (f" - {translation_name}" if translation_name else ""),  # Title - using Arabic name
        f"Verse {verse_number}",  # Verse Number (smaller)
        arabic,  # Arabic Text (larger)
        english_text,  # English Translation
        "QuranIlm • Divine Words"  # Enhanced footer
    ]
    
    # Adjusted positions for better spacing and prominence
    positions = [120, 190, 400, 750, height - 80]
    
    # Font sizes (initial sizes, will be auto-scaled)
    font_sizes = [60, 36, 100, 50, 40]  # Smaller verse number
    
    # Use proper font paths with fallbacks - use Arabic font for Arabic text and title
    font_paths = [
        arabic_font_path,         # Title (Arabic) - using the specified font
        english_font_path,        # Verse number
        arabic_font_path,         # Arabic text - using the specified font
        english_font_path,        # English translation
        english_font_path         # Footer
    ]

    # Create epic frame
    frame = create_frame(width, height, texts, positions, font_paths, font_sizes)
    
    # Save frame with proper error handling
    try:
        # Create the directory if it doesn't exist
        os.makedirs('temp/frames', exist_ok=True)
        frame_path = "temp/frames/frame.png"
        frame.save(frame_path)
        
        # Verify the frame was actually created
        if not os.path.exists(frame_path) or os.path.getsize(frame_path) == 0:
            raise Exception("Frame not properly saved")
            
        print(f"Frame successfully saved to {frame_path}")
    except Exception as e:
        print(f"Error saving frame: {e}")
        return None

    # Download audio
    raw_audio_path = 'temp/audio_raw.mp3'
    enhanced_audio_path = 'temp/audio_enhanced.mp3'
    
    # Get audio URL safely
    audio_url = None
    try:
        audio_url = verse_data.get('audio', {}).get('2', {}).get('url')
    except (KeyError, AttributeError):
        print("Warning: Could not find audio URL in verse data")
    
    if not audio_url:
        print("Error: No audio URL available")
        return None
    
    # Download and enhance audio
    if download_audio(audio_url, raw_audio_path):
        enhance_audio(raw_audio_path, enhanced_audio_path)
    else:
        print("Error: Failed to download audio")
        return None
    
    # Get audio duration using ffprobe
    try:
        duration_cmd = [
            'ffprobe', '-i', enhanced_audio_path,
            '-show_entries', 'format=duration',
            '-v', 'quiet', '-of', 'csv=p=0'
        ]
        duration = float(subprocess.check_output(duration_cmd).decode().strip())
    except (subprocess.SubprocessError, ValueError, FileNotFoundError) as e:
        print(f"Error getting audio duration: {e}")
        # Fallback to a default duration
        duration = 10.0
    
    # Create output directory if it doesn't exist
    os.makedirs('output', exist_ok=True)
    
    # Create a sanitized filename from the Arabic text
    arabic_filename = sanitize_filename(arabic)
    
    # Create video using ffmpeg with enhanced effects
    # Use Arabic text as part of the filename
    output_path = f'output/{arabic_filename}_S{verse_data.get("surahNo", "unknown")}_V{verse_data.get("ayahNo", "unknown")}.mp4'
    
    # Simplified FFmpeg command for better compatibility
    cmd = [
        'ffmpeg', '-y',  # Overwrite output file if it exists
        '-loop', '1',    # Loop the image
        '-i', 'temp/frames/frame.png',  # Input image
        '-i', enhanced_audio_path,  # Input enhanced audio
        '-c:v', 'libx264',  # Video codec
        '-tune', 'stillimage',  # Optimize for still image
        '-crf', '23',  # Reasonable quality
        '-c:a', 'aac',    # Audio codec
        '-b:a', '192k',   # Audio bitrate
        '-pix_fmt', 'yuv420p',  # Pixel format for compatibility
        '-shortest',      # Duration determined by shortest input
        output_path
    ]
    
    try:
        subprocess.run(cmd, check=True)
        print(f"Video successfully created at {output_path}")
    except subprocess.CalledProcessError as e:
        print(f"Error creating video: {e}")
        return None
    
    # Try a simpler command if the first one fails
    if not os.path.exists(output_path) or os.path.getsize(output_path) == 0:
        print("Retrying with simpler FFmpeg command...")
        simple_cmd = [
            'ffmpeg', '-y',
            '-loop', '1',
            '-i', 'temp/frames/frame.png',
            '-i', enhanced_audio_path,
            '-c:v', 'libx264',
            '-c:a', 'aac',
            '-b:a', '192k',
            '-shortest',
            output_path
        ]
        try:
            subprocess.run(simple_cmd, check=True)
        except subprocess.CalledProcessError as e:
            print(f"Error creating video with simple command: {e}")
            return None
    
    # Cleanup
    try:
        os.remove(raw_audio_path)
        os.remove(enhanced_audio_path)
        os.remove('temp/frames/frame.png')
    except (OSError, FileNotFoundError) as e:
        print(f"Warning during cleanup: {e}")
    
    return output_path

def signal_handler(sig, frame):
    """Handle Ctrl+C gracefully"""
    print("\n\nGracefully stopping... Please wait for current video to complete.")
    global should_continue
    should_continue = False

def process_random_verse(surahs):
    """Process a random verse and create a video"""
    # Get random verse
    surah_index = random.randint(0, len(surahs) - 1)
    surah = surahs[surah_index]
    
    # Fix: Check for key existence before using
    surah_name = surah.get('surahNameEnglish', surah.get('surahNameTranslation', f"Surah {surah_index + 1}"))
    
    # Select a surah and verse
    surah_number = surah.get('surahNo', surah_index + 1)
    total_ayah = surah.get('totalAyah', 1)
    
    if total_ayah > 1:
        selected_ayah = random.randint(1, total_ayah)
    else:
        selected_ayah = 1
    
    # Fetch verse data
    url = f"https://quranapi.pages.dev/api/{surah_number}/{selected_ayah}.json"
    print(f"Fetching verse data from: {url}")
    
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            verse_data = response.json()
            
            print(f"Creating epic video for Surah {surah_name} verse {selected_ayah}...")
            
            # Create enhanced video
            start_time = time.time()
            output_path = create_video(verse_data, surah)
            
            if output_path and os.path.exists(output_path):
                print(f"✨ Epic Quranic video created successfully: {output_path}")
                print(f"Time taken: {time.time() - start_time:.2f} seconds")
                print(f"Video features: decorative borders, particle effects, dynamic lighting, clean audio")
                return True
            else:
                print("Failed to create video")
                return False
        else:
            print(f"Failed to fetch verse data: {response.status_code}")
            return False
    except requests.RequestException as e:
        print(f"Error fetching verse data: {e}")
        return False

def main():
    global should_continue
    should_continue = True
    
    # Set up signal handler for Ctrl+C
    signal.signal(signal.SIGINT, signal_handler)
    
    try:
        print("Starting Continuous Epic Quranic Verse Video Generator...")
        print("Press Ctrl+C to stop the program safely.")
        
        # Validate that the surahs data file exists
        if not os.path.exists('paste.txt'):
            print("Error: paste.txt file not found")
            return
        
        # Load surah data with proper error handling
        try:
            with open('paste.txt', 'r', encoding='utf-8') as f:
                surahs = json.load(f)
        except json.JSONDecodeError:
            print("Error: paste.txt is not valid JSON")
            return
        except UnicodeDecodeError:
            # Try with different encodings
            try:
                with open('paste.txt', 'r', encoding='latin-1') as f:
                    surahs = json.load(f)
            except:
                print("Error: Could not decode paste.txt file")
                return
        
        if not surahs or not isinstance(surahs, list):
            print("Error: Invalid surahs data format")
            return
        
        # Continuously generate videos
        video_count = 0
        while should_continue:
            print(f"\n===== Starting video #{video_count + 1} =====")
            success = process_random_verse(surahs)
            
            if success:
                video_count += 1
                print(f"Total videos created: {video_count}")
            
            # Wait a bit before starting the next one
            # This helps prevent rate limiting and gives system resources a break
            if should_continue:
                print("Waiting 5 seconds before starting next video...")
                time.sleep(5)
        
        print(f"Program completed. Total videos created: {video_count}")
        
    except Exception as e:
        print(f"An unexpected error occurred: {str(e)}")

if __name__ == "__main__":
    main()
