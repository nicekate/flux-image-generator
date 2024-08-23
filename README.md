# Flux Image Generator

Flux Image Generator is a Streamlit web application that enables users to generate images using the Flux AI model. This powerful tool offers a user-friendly interface for creating images based on text prompts, with a standout feature of batch image generation. Users can efficiently produce multiple images simultaneously, streamlining the creative process and saving valuable time.

![](http://blog-bucket-20240321.oss-cn-hongkong.aliyuncs.com/blog/h2f4a8.png)

## Features

- Choose between different Flux models
- Generate images from text prompts
- Upload a file with multiple prompts
- Customize generation parameters (seed, number of outputs, aspect ratio, etc.)
- Download individual images or all generated images in a zip file
- Logging for better debugging and monitoring

## Requirements

- Python 3.9+
- Streamlit
- Replicate
- Pillow
- Requests
- Other dependencies listed in `requirements.txt`

## Installation

1. Clone this repository:
   ```
   git clone https://github.com/nicekate/flux-image-generator.git
   cd flux-image-generator
   ```

2. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

3. Set up your Replicate API token:
   
   For Linux and macOS:
   ```
   export REPLICATE_API_TOKEN=your_api_token_here
   ```

   For Windows (Command Prompt):
   ```
   set REPLICATE_API_TOKEN=your_api_token_here
   ```

   For Windows (PowerShell):
   ```
   $env:REPLICATE_API_TOKEN = "your_api_token_here"
   ```

## Usage

1. Run the Streamlit app:
   ```
   streamlit run app.py
   ```

2. Open your web browser and go to the URL displayed in the terminal (usually `http://localhost:8501`).

3. Use the interface to select a model, enter prompts, and generate images.

## How to Use

1. Select the Flux model you want to use from the dropdown menu.
2. Enter a text prompt describing the image you want to generate, or upload a text file with multiple prompts (one per line).
3. (Optional) Expand the "Advanced Settings" section to adjust parameters like random seed, number of outputs, aspect ratio, output format, and quality.
4. Click the "Generate Images" button to start the image generation process.
5. View the generated images on the page. You can download individual images or all images as a zip file.

## Troubleshooting

- If you encounter API errors, make sure you have set the `REPLICATE_API_TOKEN` environment variable correctly.
- Check the application logs for more detailed error messages and debugging information.

## Contributing

Contributions to improve the Flux Image Generator are welcome. Please feel free to submit pull requests or open issues to suggest improvements or report bugs.

## License

[MIT License]
