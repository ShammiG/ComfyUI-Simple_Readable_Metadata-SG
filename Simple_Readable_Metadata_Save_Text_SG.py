import os
import json
import folder_paths
from datetime import datetime
import re

class SimpleReadableMetadataSaveTextSG:
    """
    A ComfyUI node for saving text content to .txt, .json, or .md files
    """
    
    def __init__(self):
        self.output_dir = folder_paths.get_output_directory()
        self.type = "output"
        self.prefix_append = ""
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "text": ("STRING", {"forceInput": True, "multiline": True}),
                "filename_prefix": ("STRING", {"default": "ComfyUI_text"}),
                "file_format": (["txt", "json", "md"], {"default": "txt"}),
                "pretty_json": ("BOOLEAN", {"default": True}),
            },
        }
    
    RETURN_TYPES = ()
    FUNCTION = "save_text"
    OUTPUT_NODE = True
    CATEGORY = "utils"
    
    def parse_filename(self, filename_prefix):
        """
        Parse filename prefix to support ComfyUI naming schemes like %date%, %time%, etc.
        """
        # Replace %date:format% patterns (handles both date AND time components)
        def replace_date(match):
            format_str = match.group(1)
            # Convert all common format codes to Python strftime
            conversions = {
                'yyyy': '%Y', 
                'yy': '%y',
                'MM': '%m', 
                'dd': '%d',
                'HH': '%H', 
                'hh': '%H',  # Both uppercase and lowercase hours
                'mm': '%M',  # Minutes when after HH/hh
                'ss': '%S'
            }
            for old, new in conversions.items():
                format_str = format_str.replace(old, new)
            return datetime.now().strftime(format_str)
        
        filename_prefix = re.sub(r'%date:([^%]+)%', replace_date, filename_prefix)
        
        # Replace %time:format% patterns
        def replace_time(match):
            format_str = match.group(1)
            conversions = {
                'HH': '%H', 
                'hh': '%H',
                'mm': '%M', 
                'ss': '%S'
            }
            for old, new in conversions.items():
                format_str = format_str.replace(old, new)
            return datetime.now().strftime(format_str)
        
        filename_prefix = re.sub(r'%time:([^%]+)%', replace_time, filename_prefix)
        
        # Default replacements
        if '%date%' in filename_prefix:
            filename_prefix = filename_prefix.replace('%date%', datetime.now().strftime('%Y-%m-%d'))
        if '%time%' in filename_prefix:
            filename_prefix = filename_prefix.replace('%time%', datetime.now().strftime('%H-%M-%S'))
        if '%timestamp%' in filename_prefix:
            filename_prefix = filename_prefix.replace('%timestamp%', str(int(datetime.now().timestamp())))
        
        return filename_prefix
    
    def save_text(self, text, filename_prefix="ComfyUI_text", file_format="txt", pretty_json=True):
        """
        Save text content to a file with automatic numbering like SaveImage
        """
        # Parse the filename prefix for special patterns
        filename_prefix = self.parse_filename(filename_prefix)
        
        # Get the output directory
        output_dir = folder_paths.get_output_directory()
        
        # Handle subfolder in filename_prefix (e.g., "folder/prefix")
        if os.path.sep in filename_prefix or '/' in filename_prefix:
            # Normalize path separators
            filename_prefix = filename_prefix.replace('/', os.path.sep)
            subfolder = os.path.dirname(filename_prefix)
            filename_prefix = os.path.basename(filename_prefix)
            
            # Create subfolder if it doesn't exist
            full_output_dir = os.path.join(output_dir, subfolder)
            os.makedirs(full_output_dir, exist_ok=True)
        else:
            full_output_dir = output_dir
            subfolder = ""
        
        # Find the next available counter number
        counter = 1
        while True:
            filename = f"{filename_prefix}_{counter:05d}.{file_format}"
            full_path = os.path.join(full_output_dir, filename)
            if not os.path.exists(full_path):
                break
            counter += 1
        
        # Process content based on file format
        try:
            if file_format == "json" and pretty_json:
                # Try to parse and pretty-print JSON
                try:
                    json_data = json.loads(text)
                    content_to_save = json.dumps(json_data, indent=2, ensure_ascii=False)
                except json.JSONDecodeError:
                    # If not valid JSON, save as-is
                    content_to_save = text
            else:
                content_to_save = text
            
            # Write the file
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(content_to_save)
            
            # Return info similar to SaveImage node
            results = [{
                "filename": filename,
                "subfolder": subfolder,
                "type": self.type
            }]
            
            return {"ui": {"text_files": results}}
        
        except Exception as e:
            error_msg = f"Error saving file: {str(e)}"
            print(error_msg)
            return {"ui": {"text_files": []}}

# Node registration
NODE_CLASS_MAPPINGS = {
    "SimpleReadableMetadataSaveTextSG": SimpleReadableMetadataSaveTextSG
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "SimpleReadableMetadataSaveTextSG": "Simple Readable Metadata Save Text-SG"
}
