import streamlit as st
import replicate
import io
import base64
from zipfile import ZipFile
import requests
import asyncio
from PIL import Image
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Set page title
st.set_page_config(page_title="Flux Image Generator", layout="wide")

# Title
st.title("Flux Image Generator")

# Select model
model = st.selectbox(
    "Select Model",
    ["black-forest-labs/flux-schnell", "black-forest-labs/flux-dev"],
    help="Choose the Flux model to use"
)

# Input prompt
prompt = st.text_area("Enter Prompt", help="Describe the image you want to generate")

# Upload txt file
uploaded_file = st.file_uploader("Upload Prompt File (one prompt per line)", type="txt")

# Set parameters
with st.expander("Advanced Settings"):
    seed = st.number_input("Random Seed", min_value=0, help="Set a random seed for reproducible results")
    num_outputs = st.slider("Number of Outputs per Prompt", min_value=1, max_value=4, value=1, help="Number of images to generate for each prompt")
    aspect_ratio = st.selectbox(
        "Aspect Ratio",
        ["16:9", "1:1", "21:9", "2:3", "3:2", "4:5", "5:4", "9:16", "9:21"],
        index=0,
        help="Aspect ratio of the generated images"
    )
    output_format = st.selectbox("Output Format", ["png", "webp", "jpg"], index=0, help="Format of the output images")
    output_quality = st.slider("Output Quality", min_value=0, max_value=100, value=100, help="Quality of the output images, from 0 to 100. 100 is best quality, 0 is worst. Not relevant for .png output")
    disable_safety_checker = st.checkbox("Disable Safety Checker", help="Disable the safety checker for generated images. This feature is only available through the API.")

async def generate_image_async(prompt, model, input_data, timeout=45):
    try:
        prediction = await replicate.predictions.async_create(
            model=model,
            input=input_data
        )
        start_time = asyncio.get_event_loop().time()
        while prediction.status != "succeeded":
            if asyncio.get_event_loop().time() - start_time > timeout:
                raise asyncio.TimeoutError(f"Image generation timed out ({timeout} seconds)")
            await asyncio.sleep(1)
            prediction = await replicate.predictions.async_get(prediction.id)
        
        logger.info(f"API response: {prediction.output}")
        logger.info(f"Full API response: {prediction}")

        if prediction.output:
            if isinstance(prediction.output, list):
                return prediction.output[0] if prediction.output else None
            elif isinstance(prediction.output, str):
                return prediction.output
            else:
                logger.error(f"Unknown API response format: {type(prediction.output)}")
                return None
        else:
            logger.error("API response is empty")
            return None
    except asyncio.TimeoutError as e:
        logger.error(str(e))
        return None
    except Exception as e:
        logger.error(f"Error generating image: {str(e)}")
        return None

def get_image_download_link(img_url, filename):
    response = requests.get(img_url)
    response.raise_for_status()
    img_data = response.content
    b64 = base64.b64encode(img_data).decode()
    file_size = len(img_data)
    logger.info(f"Downloaded image size: {file_size} bytes")
    return f'<a href="data:image/png;base64,{b64}" download="{filename}">Download Image ({file_size/1024:.2f} KB)</a>'

# Generate button
if st.button("Generate Images"):
    prompts = []
    if uploaded_file:
        prompts = [line.decode("utf-8").strip() for line in uploaded_file]
    elif prompt:
        prompts = [prompt]
    
    if not prompts:
        st.error("Please enter a prompt or upload a prompt file")
    else:
        with st.spinner(f"Generating {len(prompts) * num_outputs} images..."):
            async def generate_all_images():
                tasks = []
                for current_prompt in prompts:
                    for _ in range(num_outputs):
                        input_data = {
                            "prompt": current_prompt,
                            "seed": seed if seed else None,
                            "aspect_ratio": aspect_ratio,
                            "output_format": output_format,
                            "output_quality": output_quality,
                            "disable_safety_checker": disable_safety_checker
                        }
                        input_data = {k: v for k, v in input_data.items() if v is not None}
                        tasks.append(generate_image_async(current_prompt, model, input_data, timeout=45))
                return await asyncio.gather(*tasks)

            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            generated_images = loop.run_until_complete(generate_all_images())
            
            # Display generated images
            for i, image_url in enumerate(generated_images):
                if image_url:
                    logger.info(f"Processing image URL: {image_url}")
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        try:
                            if not image_url.startswith(('http://', 'https://')):
                                raise ValueError(f"Invalid URL: {image_url}")
                            
                            response = requests.get(image_url)
                            response.raise_for_status()
                            
                            image = Image.open(io.BytesIO(response.content))
                            logger.info(f"Image {i+1} dimensions: {image.size}")
                            st.image(image, caption=f"Generated Image {i+1}", use_column_width=True)
                            logger.info(f"Successfully displayed image {i+1}")
                        except requests.RequestException as e:
                            logger.error(f"Error downloading image: {str(e)}")
                            st.error(f"Unable to load image {i+1}: {str(e)}")
                        except ValueError as e:
                            logger.error(str(e))
                            st.error(f"Invalid image URL {i+1}: {str(e)}")
                        except Exception as e:
                            logger.error(f"Unknown error processing image: {str(e)}")
                            st.error(f"Error processing image {i+1}: {str(e)}")
                    with col2:
                        st.markdown(get_image_download_link(image_url, f"generated_image_{i+1}.{output_format}"), unsafe_allow_html=True)
                        st.text_area("Prompt", prompts[i // num_outputs], height=100)
                else:
                    logger.warning(f"URL for image {i+1} is empty")
        
        # Batch download
        if len(generated_images) > 1:
            zip_buffer = io.BytesIO()
            with ZipFile(zip_buffer, 'w') as zip_file:
                for i, image_url in enumerate(generated_images):
                    if image_url:
                        response = requests.get(image_url)
                        zip_file.writestr(f"generated_image_{i+1}.{output_format}", response.content)
            
            zip_buffer.seek(0)
            b64 = base64.b64encode(zip_buffer.getvalue()).decode()
            href = f'<a href="data:application/zip;base64,{b64}" download="generated_images.zip">Download All Images</a>'
            st.markdown(href, unsafe_allow_html=True)

# Add instructions
st.markdown("""
## Instructions
- Select the Flux model you want to use.
- Enter a prompt describing the image you want to generate in the text box, or upload a txt file with multiple prompts (one per line).
- If needed, expand "Advanced Settings" to adjust other parameters.
- Click the "Generate Images" button to start the generation process.
- Generated images will be displayed on the page, and you can download each image individually or all images in batch.

Note: Make sure you have set the REPLICATE_API_TOKEN environment variable, otherwise the API call will fail.
""")