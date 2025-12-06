import torch
import os
import folder_paths
from PIL import Image, ImageOps
import numpy as np
import hashlib
import json
import re

class SimpleReadableMetadataSG:
    """Load image with drag-and-drop, automatically extract properties and metadata"""

    CATEGORY = "image/analysis"

    @classmethod
    def INPUT_TYPES(cls):
        input_dir = folder_paths.get_input_directory()
        files = [f for f in os.listdir(input_dir) if os.path.isfile(os.path.join(input_dir, f))]
        return {
            "required": {
                "image": (sorted(files), {"image_upload": True}),
                "emoji_in_readable_text": ("BOOLEAN", {"default": True})
            },
            "ui": {
                "image": {"min_width": 450},
            },
        }

    RETURN_TYPES = ("STRING", "IMAGE", "MASK", "STRING", "STRING", "STRING", "INT", "STRING")
    RETURN_NAMES = ("Simple_Readable_Metadata", "image", "mask", "metadata_raw", "Positive_Prompt", "Negative_Prompt", "seed", "file_name_text")
    FUNCTION = "load_analyze_extract"
    OUTPUT_NODE = True

    @classmethod
    def IS_CHANGED(cls, image, emoji_in_readable_text):
        image_path = folder_paths.get_annotated_filepath(image)
        m = hashlib.sha256()
        with open(image_path, 'rb') as f:
            m.update(f.read())
        return m.digest().hex()

    @classmethod
    def VALIDATE_INPUTS(cls, image, emoji_in_readable_text):
        if not folder_paths.exists_annotated_filepath(image):
            return "Invalid image file: {}".format(image)
        return True

    def is_node_reference(self, value):
        """Check if a value is a node reference like [node_id, output_index]"""
        try:
            if isinstance(value, list):
                if len(value) == 2:
                    if isinstance(value[0], (str, int)) and isinstance(value[1], int):
                        return True
        except:
            pass
        return False

    def safely_convert_to_string(self, value):
        """Safely convert any value to string - GUARANTEED TO RETURN STRING"""
        try:
            if self.is_node_reference(value):
                return "N/A"
            if isinstance(value, str):
                return value
            elif isinstance(value, list):
                if len(value) > 0:
                    return self.safely_convert_to_string(value[0])
                return "N/A"
            elif value is None:
                return "N/A"
            else:
                return str(value)
        except:
            return "N/A"

    def safely_process_value(self, value):
        """Master wrapper - ensures value is ALWAYS a string before any operations"""
        return self.safely_convert_to_string(value)

    def _get_prompt_data_from_image(self, img):
        """Helper method to extract prompt data from both PNG and WebP formats"""
        try:
            # First check direct img.info (works for PNG)
            if hasattr(img, 'info') and img.info:
                if "prompt" in img.info:
                    try:
                        prompt_str = img.info["prompt"]
                        if isinstance(prompt_str, str):
                            return json.loads(prompt_str)
                        return prompt_str
                    except:
                        pass

                # Check EXIF data for WebP
                if "exif" in img.info:
                    try:
                        exif_bytes = img.info["exif"]
                        if isinstance(exif_bytes, bytes):
                            exif_string = exif_bytes.decode('utf-8', errors='ignore')
                            # Look for prompt: marker
                            if "prompt:" in exif_string:
                                prompt_start = exif_string.find("prompt:")
                                if prompt_start != -1:
                                    prompt_data = exif_string[prompt_start + 7:]
                                    prompt_data = prompt_data.split('\x00')[0]
                                    try:
                                        return json.loads(prompt_data)
                                    except:
                                        pass
                    except Exception as e:
                        print(f"Error parsing WebP EXIF for prompt: {e}")
        except Exception as e:
            print(f"Error extracting prompt data: {e}")
        return None

    def extract_model_name(self, img):
        """Extract model name from image metadata"""
        model_name = "N/A"
        try:
            if not hasattr(img, 'info') or not img.info:
                return model_name

            # Try to get prompt data (works for both PNG and WebP)
            prompt_data = self._get_prompt_data_from_image(img)
            if prompt_data:
                try:
                    for node_id, node_data in prompt_data.items():
                        class_type = node_data.get('class_type', '')
                        inputs = node_data.get('inputs', {})

                        if 'CheckpointLoader' in class_type and 'ckpt_name' in inputs:
                            model_name = inputs['ckpt_name']
                            break
                        if 'UNETLoader' in class_type and 'unet_name' in inputs:
                            model_name = f"{inputs['unet_name']} (UNET)"
                            break
                        if 'Loader' in class_type:
                            if 'ckpt_name' in inputs:
                                model_name = inputs['ckpt_name']
                                break
                            elif 'unet_name' in inputs:
                                model_name = f"{inputs['unet_name']} (UNET)"
                                break
                            elif 'model_name' in inputs:
                                model_name = inputs['model_name']
                                break
                except Exception as e:
                    print(f"Error parsing prompt metadata: {e}")

            # Try workflow format (PNG direct access)
            if model_name == "N/A" and 'workflow' in img.info:
                try:
                    workflow_data = json.loads(img.info['workflow'])
                    for node in workflow_data.get('nodes', []):
                        node_type = node.get('type', '')
                        if 'Checkpoint' in node_type or 'Loader' in node_type:
                            widgets = node.get('widgets_values', [])
                            if widgets and len(widgets) > 0:
                                model_name = widgets[0]
                                break
                except Exception as e:
                    print(f"Error parsing workflow metadata: {e}")

            # Try A1111 format (PNG direct access)
            if model_name == "N/A" and 'parameters' in img.info:
                try:
                    params = img.info['parameters']
                    model_pattern = r'Model:\s*([^,\n]+)'
                    match = re.search(model_pattern, params)
                    if match:
                        model_name = match.group(1).strip()
                except Exception as e:
                    print(f"Error parsing A1111 metadata: {e}")

        except Exception as e:
            print(f"Error extracting model metadata: {e}")

        return model_name

    def extract_generation_params(self, img):
        """Extract generation parameters (seed, steps, cfg, sampler, scheduler) from image metadata"""
        params = {
            'seed': 'N/A',
            'steps': 'N/A',
            'cfg': 'N/A',
            'sampler': 'N/A',
            'scheduler': 'N/A'
        }

        try:
            if not hasattr(img, 'info') or not img.info:
                return params

            # Try to get prompt data (works for both PNG and WebP)
            prompt_data = self._get_prompt_data_from_image(img)
            if prompt_data:
                try:
                    for node_id, node_data in prompt_data.items():
                        class_type = node_data.get('class_type', '')
                        inputs = node_data.get('inputs', {})

                        # KSampler node has all the info we need
                        if class_type == "KSampler":
                            params['seed'] = inputs.get('seed', 'N/A')
                            params['steps'] = inputs.get('steps', 'N/A')
                            params['cfg'] = inputs.get('cfg', 'N/A')
                            params['sampler'] = inputs.get('sampler_name', 'N/A')
                            params['scheduler'] = inputs.get('scheduler', 'N/A')
                            return params

                        # Check individual nodes for distributed sampler setup
                        if 'seed' in inputs or 'noise_seed' in inputs:
                            params['seed'] = inputs.get('seed', inputs.get('noise_seed', params['seed']))
                        if 'steps' in inputs:
                            params['steps'] = inputs.get('steps', params['steps'])
                        if 'cfg' in inputs:
                            params['cfg'] = inputs.get('cfg', params['cfg'])
                        if 'sampler_name' in inputs:
                            params['sampler'] = inputs.get('sampler_name', params['sampler'])
                        if 'scheduler' in inputs:
                            params['scheduler'] = inputs.get('scheduler', params['scheduler'])

                except Exception as e:
                    print(f"Error parsing ComfyUI generation params: {e}")

            # Try A1111/Forge format (PNG direct access)
            if 'parameters' in img.info and any(v == 'N/A' for v in params.values()):
                try:
                    metadata_text = img.info['parameters']

                    seed_match = re.search(r'Seed:\s*(\d+)', metadata_text)
                    if seed_match:
                        params['seed'] = int(seed_match.group(1))

                    steps_match = re.search(r'Steps:\s*(\d+)', metadata_text)
                    if steps_match:
                        params['steps'] = int(steps_match.group(1))

                    cfg_match = re.search(r'CFG scale:\s*([\d.]+)', metadata_text)
                    if cfg_match:
                        params['cfg'] = float(cfg_match.group(1))

                    sampler_match = re.search(r'Sampler:\s*([^,\n]+)', metadata_text)
                    if sampler_match:
                        params['sampler'] = sampler_match.group(1).strip()

                    scheduler_match = re.search(r'Schedule type:\s*([^,\n]+)', metadata_text)
                    if scheduler_match:
                        params['scheduler'] = scheduler_match.group(1).strip()

                except Exception as e:
                    print(f"Error parsing A1111 generation params: {e}")

        except Exception as e:
            print(f"Error extracting generation parameters: {e}")

        return params

    def load_analyze_extract(self, image, emoji_in_readable_text=True):
        """Combined function that loads image, analyzes properties, and extracts metadata"""
        try:
            image_path = folder_paths.get_annotated_filepath(image)
            img = Image.open(image_path)

            model_name = self.extract_model_name(img)
            gen_params = self.extract_generation_params(img)

            img = ImageOps.exif_transpose(img)

            metadata_raw = self.extract_raw_metadata(img)

            if img.mode == 'I':
                img = img.point(lambda i: i * (1 / 255))

            original_img = img
            if img.mode != 'RGB':
                img = img.convert('RGB')

            image_tensor = torch.from_numpy(np.array(img).astype(np.float32) / 255.0).unsqueeze(0)

            if 'A' in original_img.getbands():
                mask = np.array(original_img.getchannel('A')).astype(np.float32) / 255.0
                mask = 1. - torch.from_numpy(mask)
            else:
                mask = torch.zeros((original_img.size[1], original_img.size[0]), dtype=torch.float32, device="cpu")

            # Build display info for UI
            batch_size, height, width, channels = image_tensor.shape
            total_pixels = width * height
            resolution_mp = float(total_pixels / 1_000_000)

            # Get actual file size
            try:
                file_size_bytes = os.path.getsize(image_path)
                file_size_mb = float(file_size_bytes) / (1024 * 1024)
                self._current_image_path = os.path.basename(image_path)
                self._current_file_size = file_size_mb
                file_name_text_without_ext = os.path.splitext(os.path.basename(image_path))[0]
            except:
                file_size_mb = 0.0
                file_name_text_without_ext = "unknown"

            def gcd(a, b):
                while b:
                    a, b = b, a % b
                return a

            def find_closest_standard_ratio(decimal_ratio):
                standard_ratios = [
                    (1.0, '1:1'), (1.25, '5:4'), (1.33333, '4:3'),
                    (1.5, '3:2'), (1.6, '16:10'), (1.66667, '5:3'),
                    (1.77778, '16:9'), (1.88889, '17:9'), (2.0, '2:1'),
                    (2.33333, '21:9'), (2.35, '2.35:1'), (2.39, '2.39:1'),
                    (2.4, '12:5'),
                ]

                closest_diff = float('inf')
                closest_ratio = None
                error_threshold = 0.05

                for std_value, std_string in standard_ratios:
                    diff = abs(std_value - decimal_ratio)
                    if diff < closest_diff:
                        closest_diff = diff
                        closest_ratio = std_string

                if closest_diff <= error_threshold:
                    return closest_ratio
                return None

            divisor = gcd(width, height)
            width_ratio = float(width // divisor)
            height_ratio = float(height // divisor)
            aspect_ratio_decimal = width / height
            closest_standard = find_closest_standard_ratio(aspect_ratio_decimal)

            # Store image/tensor info for readable format reuse
            self._last_width = width
            self._last_height = height
            self._last_resolution_mp = resolution_mp
            self._last_width_ratio = width_ratio
            self._last_height_ratio = height_ratio
            self._last_aspect_ratio_decimal = aspect_ratio_decimal
            self._last_closest_standard = closest_standard
            self._last_file_size_mb = file_size_mb

            line1 = f"{width}x{height} | {resolution_mp:.2f}MP "

            if closest_standard and closest_standard != f"{int(width_ratio)}:{int(height_ratio)}":
                line2 = f"Ratio: {int(width_ratio)}:{int(height_ratio)} or {aspect_ratio_decimal:.2f}:1 or ~{closest_standard}"
            else:
                line2 = f"Ratio: {int(width_ratio)}:{int(height_ratio)} or {aspect_ratio_decimal:.2f}:1"

            line3 = f"File Size: {file_size_mb:.2f}MB"

            lines = [line1, line2, line3]
            lines.append("")  # Add empty line for spacing

            line4 = f"Model: {model_name}"
            lines.append(line4)

            line5 = f"Seed: {gen_params['seed']} | Steps: {gen_params['steps']} | CFG: {gen_params['cfg']}"
            lines.append(line5)

            line6 = f"Sampler: {gen_params['sampler']} | Scheduler: {gen_params['scheduler']}"
            lines.append(line6)

            Simple_Readable_Metadata, positive, negative = self.parse_metadata(metadata_raw, emoji_in_readable_text)

            # Convert seed to integer, use 0 if N/A
            seed_value = gen_params['seed']
            if seed_value == 'N/A' or seed_value is None:
                seed_int = 0
            else:
                try:
                    seed_int = int(seed_value)
                except (ValueError, TypeError):
                    seed_int = 0

            return {
                "ui": {"text": lines},
                "result": (Simple_Readable_Metadata, image_tensor, mask, metadata_raw, positive, negative, seed_int, file_name_text_without_ext)
            }

        except Exception as e:
            print(f"Error in load_analyze_extract: {e}")
            raise

    def extract_raw_metadata(self, img):
        """Extract raw metadata in format compatible with conversion - supports PNG and WebP"""
        png_info = img.info if hasattr(img, 'info') else {}

        if not png_info:
            return "No metadata found in image"

        # Check for ComfyUI prompt metadata (works for PNG)
        if "prompt" in png_info:
            try:
                prompt_data = png_info["prompt"]
                if isinstance(prompt_data, str):
                    json.loads(prompt_data)  # Validate JSON
                    return prompt_data
                else:
                    return json.dumps(prompt_data)
            except:
                pass

        # Check for A1111/Forge parameters (works for PNG)
        if "parameters" in png_info:
            return png_info["parameters"]

        # Check for EXIF data in WebP
        if "exif" in png_info:
            try:
                exif_bytes = png_info["exif"]
                if isinstance(exif_bytes, bytes):
                    # Decode the EXIF bytes to string
                    exif_string = exif_bytes.decode('utf-8', errors='ignore')

                    # Look for prompt: or workflow: markers in the EXIF data
                    if "prompt:" in exif_string:
                        # Extract the JSON after "prompt:"
                        prompt_start = exif_string.find("prompt:")
                        if prompt_start != -1:
                            # Extract everything after "prompt:"
                            prompt_data = exif_string[prompt_start + 7:]  # Skip "prompt:"

                            # Find the end of the JSON (look for the null terminator or end)
                            # Try to extract valid JSON
                            try:
                                # Remove any trailing null bytes or extra data
                                prompt_data = prompt_data.split('\x00')[0]
                                # Validate it's proper JSON
                                json.loads(prompt_data)
                                return prompt_data
                            except:
                                pass

                    # If no valid prompt found, try to extract workflow
                    if "workflow:" in exif_string:
                        workflow_start = exif_string.find("workflow:")
                        if workflow_start != -1:
                            workflow_data = exif_string[workflow_start + 9:]  # Skip "workflow:"
                            try:
                                workflow_data = workflow_data.split('\x00')[0]
                                workflow_json = json.loads(workflow_data)
                                # Return workflow as a fallback
                                return json.dumps({"workflow": workflow_json})
                            except:
                                pass

            except Exception as e:
                print(f"Error parsing WebP EXIF metadata: {e}")

        # Fallback: Try using PIL's getexif() method for standard EXIF tags
        if hasattr(img, 'getexif'):
            try:
                exif_data = img.getexif()
                if exif_data:
                    # Try to find UserComment tag (0x9286)
                    user_comment = exif_data.get(0x9286)
                    if user_comment:
                        if isinstance(user_comment, bytes):
                            user_comment = user_comment.decode('utf-8', errors='ignore')
                        try:
                            json.loads(user_comment)
                            return user_comment
                        except:
                            return user_comment
            except Exception as e:
                print(f"Error reading EXIF via getexif(): {e}")

        return "No ComfyUI or WebUI format metadata found. Image may be from a different source."

    def parse_metadata(self, metadata_raw, include_emojis=True):
        """Main parsing function that detects format and routes to appropriate converter"""
        try:
            # FIRST: Handle bytes (WebP EXIF data can be bytes)
            if isinstance(metadata_raw, (bytes, bytearray)):
                try:
                    metadata_raw = metadata_raw.decode("utf-8", errors="ignore")
                except Exception:
                    metadata_raw = str(metadata_raw)

            # SECOND: Convert to string safely (handles dict/list/node references)
            metadata_raw = self.safely_process_value(metadata_raw)

            # THIRD: Now detect format and parse
            format_type = self.detect_format(metadata_raw)

            if format_type == "comfyui":
                Simple_Readable_Metadata = self.parse_comfyui_format(
                    metadata_raw,
                    include_emojis,
                    image_path=getattr(self, '_current_image_path', None),
                    file_size_mb=getattr(self, '_current_file_size', None)
                )
            elif format_type == "webui":
                Simple_Readable_Metadata = self.parse_webui_format(metadata_raw, include_emojis)
            else:
                Simple_Readable_Metadata = "Unable to detect metadata format. Please ensure the input is from ComfyUI or WebUI Forge/A1111."

            positive, negative = self.extract_individual_params(metadata_raw, format_type)

            positive = self.safely_convert_to_string(positive)
            negative = self.safely_convert_to_string(negative)

            return (Simple_Readable_Metadata, positive, negative)

        except Exception as e:
            print(f"Error in parse_metadata: {e}")
            return (f"Error parsing metadata: {str(e)}", "N/A", "N/A")

    def detect_format(self, text):
        """Detect whether the input is ComfyUI JSON or WebUI text format"""
        try:
            text = self.safely_process_value(text).strip()
            if text.startswith("Prompt: "):
                text = text[8:]

            # Try JSON first
            try:
                json.loads(text)
                return "comfyui"
            except json.JSONDecodeError:
                pass

            # Then try A1111/WebUI pattern detection
            if (re.search(r'Steps:\s*\d+', text) or 
                re.search(r'Sampler:\s*\w+', text) or 
                re.search(r'CFG scale:\s*[\d.]+', text)):
                return "webui"

            return "unknown"
        except Exception as e:
            print(f"Error detecting format: {e}")
            return "unknown"

    def parse_webui_format(self, text, include_emojis=True):
        """Parse A1111/WebUI Forge text format metadata"""
        try:
            text = self.safely_process_value(text)

            emoji_map = {
                "sampling": "🎯",
                "dimensions": "📏",
                "prompts": "📝",
                "models": "🧠",
                "lora": "🎨",
                "advanced": "⚙️"
            } if include_emojis else {k: "" for k in ["sampling", "dimensions", "prompts", "models", "lora", "advanced"]}

            output = []
            output.append("=== WebUI Forge/A1111 Generation Parameters ===\n")

            # Parse lines first to extract metadata_line
            lines = text.strip().split('\n')
            positive_prompt = ""
            negative_prompt = ""
            metadata_line = ""

            for i, line in enumerate(lines):
                if line.startswith("Negative prompt:"):
                    negative_prompt = line.replace("Negative prompt:", "").strip()
                elif re.search(r'Steps:\s*\d+', line):
                    metadata_line = line
                elif not metadata_line and not line.startswith("Negative prompt:"):
                    positive_prompt += line + " "

            positive_prompt = positive_prompt.strip()

            # NOW extract model name from metadata for display at the top
            model_name_display = "N/A"
            if metadata_line:
                model_match = re.search(r'Model:\s*([^,\n]+)', metadata_line)
                if model_match:
                    model_name_display = model_match.group(1).strip()

            # Display model at the top
            output.append(f"{emoji_map['models']} MODEL: {model_name_display}\n")

            output.append(f"{emoji_map['prompts']} PROMPTS:")
            output.append(f"  Positive: {positive_prompt if positive_prompt else '(empty)'}")
            output.append(f"  Negative: {negative_prompt if negative_prompt else '(empty)'}")
            output.append("")

            if metadata_line:
                params = {}
                patterns = {
                    'steps': r'Steps:\s*(\d+)',
                    'sampler': r'Sampler:\s*([^,]+)',
                    'cfg': r'CFG scale:\s*([\d.]+)',
                    'seed': r'Seed:\s*(\d+)',
                    'size': r'Size:\s*(\d+x\d+)',
                    'model': r'Model:\s*([^,]+)',
                    'model_hash': r'Model hash:\s*([^,]+)',
                    'denoising': r'Denoising strength:\s*([\d.]+)',
                    'clip_skip': r'Clip skip:\s*(\d+)',
                    'scheduler': r'Schedule type:\s*([^,]+)',
                    'version': r'Version:\s*([^,]+)',
                }

                for key, pattern in patterns.items():
                    match = re.search(pattern, metadata_line)
                    if match:
                        params[key] = match.group(1).strip()

                output.append(f"{emoji_map['sampling']} SAMPLING SETTINGS:")
                if 'seed' in params:
                    output.append(f"  Seed: {params['seed']}")
                if 'steps' in params:
                    output.append(f"  Steps: {params['steps']}")
                if 'cfg' in params:
                    output.append(f"  CFG Scale: {params['cfg']}")
                if 'sampler' in params:
                    output.append(f"  Sampler: {params['sampler']}")
                if 'scheduler' in params:
                    output.append(f"  Scheduler: {params['scheduler']}")
                if 'denoising' in params:
                    output.append(f"  Denoise: {params['denoising']}")
                output.append("")

                if 'size' in params:
                    output.append(f"{emoji_map['dimensions']} IMAGE DIMENSIONS:")
                    output.append(f"  Resolution: {params['size']}")
                    output.append("")

                if 'model' in params or 'model_hash' in params:
                    output.append(f"{emoji_map['models']} MODELS & COMPONENTS:")
                    if 'model' in params:
                        output.append(f"  Checkpoint: {params['model']}")
                    if 'model_hash' in params:
                        output.append(f"  Model Hash: {params['model_hash']}")
                    output.append("")

                # Extract LoRAs
                lora_pattern = r'<lora:([^:]+):([\d.]+)>'
                lora_matches = re.findall(lora_pattern, text)
                if lora_matches:
                    output.append(f"{emoji_map['lora']} LORA MODELS:")
                    for lora_name, lora_strength in lora_matches:
                        output.append(f"  {lora_name} (Strength: {lora_strength})")
                    output.append("")

                # Advanced settings
                if metadata_line:
                    params_check = {}
                    patterns = {
                        'clip_skip': r'Clip skip:\s*(\d+)',
                        'version': r'Version:\s*([^,]+)',
                    }

                    for key, pattern in patterns.items():
                        match = re.search(pattern, metadata_line)
                        if match:
                            params_check[key] = match.group(1).strip()

                    if 'clip_skip' in params_check or 'version' in params_check:
                        output.append(f"{emoji_map['advanced']} ADVANCED SETTINGS:")
                        if 'clip_skip' in params_check:
                            output.append(f"  Clip Skip: {params_check['clip_skip']}")
                        if 'version' in params_check:
                            output.append(f"  WebUI Version: {params_check['version']}")
                        output.append("")

            return "\n".join(output)

        except Exception as e:
            print(f"Error parsing WebUI format: {e}")
            return f"Error parsing WebUI metadata: {str(e)}"

    def parse_comfyui_format(self, metadata_raw, include_emojis=True, image_path=None, file_size_mb=None):
        """Parse ComfyUI JSON format metadata"""
        try:
            # Safely convert to string FIRST
            metadata_raw = self.safely_process_value(metadata_raw)

            clean_text = metadata_raw.strip()
            if clean_text.startswith("Prompt: "):
                clean_text = clean_text[8:]

            try:
                data = json.loads(clean_text)
            except json.JSONDecodeError as e:
                return f"Error parsing JSON: {str(e)}\n\nPlease ensure the input is valid JSON format."

            # NOW create output and emoji_map AFTER data is ready
            output = []

            emoji_map = {
                "sampling": "🎯",
                "dimensions": "📏",
                "prompts": "📝",
                "models": "🧠",
                "lora": "🎨",
                "advanced": "⚙️"
            } if include_emojis else {k: "" for k in ["sampling", "dimensions", "prompts", "models", "lora", "advanced"]}

            output.append("=== ComfyUI Generation Parameters ===\n")

            # Extract latent dimensions
            latent_data = None
            width = 'N/A'
            height = 'N/A'
            batch_size = 'N/A'

            for node_id, node_data in data.items():
                try:
                    class_type = node_data.get("class_type", "")
                    if "LatentImage" in class_type or "EmptyLatent" in class_type:
                        latent_data = node_data["inputs"]
                        width = self.resolve_node_reference(data, latent_data.get('width', 'N/A'))
                        height = self.resolve_node_reference(data, latent_data.get('height', 'N/A'))
                        batch_size = latent_data.get('batch_size', 'N/A')
                        break
                except Exception as e:
                    continue

            if latent_data:
                # Calculate megapixels
                try:
                    width_int = int(width) if width != "N/A" else 0
                    height_int = int(height) if height != "N/A" else 0
                    total_pixels = width_int * height_int
                    resolution_mp = float(total_pixels) / 1_000_000
                except:
                    resolution_mp = 0.0

                # Calculate aspect ratio
                def gcd(a, b):
                    while b:
                        a, b = b, a % b
                    return a

                def find_closest_standard_ratio(decimal_ratio):
                    standard_ratios = [
                        (1.0, "1:1"), (1.25, "5:4"), (1.33333, "4:3"),
                        (1.5, "3:2"), (1.6, "16:10"), (1.66667, "5:3"),
                        (1.77778, "16:9"), (1.88889, "17:9"), (2.0, "2:1"),
                        (2.33333, "21:9"), (2.35, "2.35:1"), (2.39, "2.39:1"),
                        (2.4, "12:5"),
                    ]

                    closest_diff = float('inf')
                    closest_ratio = None
                    error_threshold = 0.05

                    for std_value, std_string in standard_ratios:
                        diff = abs(std_value - decimal_ratio)
                        if diff < closest_diff:
                            closest_diff = diff
                            closest_ratio = std_string

                    if closest_diff <= error_threshold:
                        return closest_ratio
                    return None

                try:
                    divisor = gcd(width_int, height_int)
                    width_ratio = float(width_int) / divisor
                    height_ratio = float(height_int) / divisor
                    aspect_ratio_decimal = width_int / height_int
                    closest_standard = find_closest_standard_ratio(aspect_ratio_decimal)

                    # Build ratio string
                    exact_ratio = f"{int(width_ratio)}:{int(height_ratio)}"
                    decimal_ratio = f"{aspect_ratio_decimal:.2f}:1"

                    if closest_standard and closest_standard != exact_ratio:
                        ratio_display = f"{exact_ratio} or {decimal_ratio} or ~{closest_standard}"
                    else:
                        ratio_display = f"{exact_ratio} or {decimal_ratio}"
                except:
                    ratio_display = "N/A"

                # Dimensions, resolution, ratio, and file size
                file_size_str = f" | {file_size_mb:.2f}MB" if file_size_mb is not None else ""
                output.append(f"{width}x{height} | {resolution_mp:.2f}MP | Ratio: {ratio_display}{file_size_str}")
                output.append("")

            # Extract model name for display at the top
            model_name_display = "N/A"
            for node_id, node_data in data.items():
                class_type = node_data.get("class_type", "")
                inputs = node_data.get("inputs", {})

                if 'CheckpointLoader' in class_type and 'ckpt_name' in inputs:
                    model_name_display = inputs['ckpt_name']
                    break
                elif 'UNETLoader' in class_type and 'unet_name' in inputs:
                    model_name_display = f"{inputs['unet_name']} (UNET)"
                    break
                elif 'Loader' in class_type:
                    if 'ckpt_name' in inputs:
                        model_name_display = inputs['ckpt_name']
                        break
                    elif 'unet_name' in inputs:
                        model_name_display = f"{inputs['unet_name']} (UNET)"
                        break

            output.append(f"{emoji_map['models']} MODEL: {model_name_display}")
            output.append("")

            # Extract sampling parameters
            sampling_params = {
                'seed': 'N/A',
                'steps': 'N/A',
                'cfg': 'N/A',
                'sampler': 'N/A',
                'scheduler': 'N/A',
                'denoise': 'N/A'
            }

            ksampler_data = None
            for node_id, node_data in data.items():
                try:
                    if node_data.get("class_type") == "KSampler":
                        ksampler_data = node_data.get("inputs", {})
                        sampling_params['seed'] = self.safely_process_value(ksampler_data.get('seed', 'N/A'))
                        sampling_params['steps'] = self.safely_process_value(ksampler_data.get('steps', 'N/A'))
                        sampling_params['cfg'] = self.safely_process_value(ksampler_data.get('cfg', 'N/A'))
                        sampling_params['sampler'] = self.safely_process_value(ksampler_data.get('sampler_name', 'N/A'))
                        sampling_params['scheduler'] = self.safely_process_value(ksampler_data.get('scheduler', 'N/A'))
                        sampling_params['denoise'] = self.safely_process_value(ksampler_data.get('denoise', 'N/A'))
                        break
                except Exception as e:
                    continue

            # If no KSampler found, look for distributed nodes
            if not ksampler_data:
                for node_id, node_data in data.items():
                    try:
                        class_type = node_data.get("class_type", "")
                        inputs = node_data.get("inputs", {})

                        if "Noise" in class_type and "noise_seed" in inputs:
                            sampling_params['seed'] = self.safely_process_value(inputs.get('noise_seed', 'N/A'))
                        elif "Noise" in class_type and "seed" in inputs:
                            sampling_params['seed'] = self.safely_process_value(inputs.get('seed', 'N/A'))

                        if "Scheduler" in class_type:
                            if 'steps' in inputs:
                                sampling_params['steps'] = self.safely_process_value(inputs.get('steps', 'N/A'))
                            if 'scheduler' in inputs:
                                sampling_params['scheduler'] = self.safely_process_value(inputs.get('scheduler', 'N/A'))
                            if 'denoise' in inputs:
                                sampling_params['denoise'] = self.safely_process_value(inputs.get('denoise', 'N/A'))

                        if "CFG" in class_type and 'cfg' in inputs:
                            sampling_params['cfg'] = self.safely_process_value(inputs.get('cfg', 'N/A'))

                        if "KSamplerSelect" in class_type and 'sampler_name' in inputs:
                            sampling_params['sampler'] = self.safely_process_value(inputs.get('sampler_name', 'N/A'))
                        elif "Sampler" in class_type and 'sampler_name' in inputs:
                            sampling_params['sampler'] = self.safely_process_value(inputs.get('sampler_name', 'N/A'))
                    except Exception as e:
                        continue

            if any(v != 'N/A' for v in sampling_params.values()):
                output.append(f"{emoji_map['sampling']} SAMPLING SETTINGS:")
                output.append(f"  Seed: {sampling_params['seed']}")
                output.append(f"  Steps: {sampling_params['steps']}")
                output.append(f"  CFG Scale: {sampling_params['cfg']}")
                output.append(f"  Sampler: {sampling_params['sampler']}")
                output.append(f"  Scheduler: {sampling_params['scheduler']}")
                output.append(f"  Denoise: {sampling_params['denoise']}")
                output.append("")

            # Extract prompts
            positive_prompt = ""
            negative_prompt = ""
            positive_candidates = []
            negative_candidates = []

            for node_id, node_data in data.items():
                try:
                    class_type = node_data.get("class_type", "")
                    inputs = node_data.get("inputs", {})

                    if "CLIPTextEncode" in class_type or "TextEncode" in class_type or "Prompt" in class_type:
                        title = node_data.get("_meta", {}).get("title", "").lower()
                        text_value = inputs.get("text", "")

                        if self.is_node_reference(text_value):
                            continue

                        text_value = self.safely_process_value(text_value)

                        if not text_value or text_value == "N/A" or not text_value.strip():
                            continue

                        is_negative = "negative" in title or "neg" in title
                        is_positive = ("positive" in title or "prompt" in title) and not is_negative

                        if is_negative:
                            negative_candidates.append(text_value)
                        elif is_positive:
                            positive_candidates.append(text_value)
                        else:
                            if not positive_candidates and not negative_candidates:
                                positive_candidates.append(text_value)
                except Exception as e:
                    continue

            if positive_candidates:
                positive_prompt = positive_candidates[0]
            if negative_candidates:
                negative_prompt = negative_candidates[0]

            output.append(f"{emoji_map['prompts']} PROMPTS:")
            output.append(f"  Positive: {positive_prompt if positive_prompt else '(empty)'}")
            if negative_prompt:
                output.append(f"  Negative: {negative_prompt}")
            output.append("")

                        # Extract LoRA models
            loras = []
            lora_files = set()
            processed_keys = set()
            
            for node_id, node_data in data.items():
                try:
                    class_type = node_data.get("class_type", "")
                    inputs = node_data.get("inputs", {})
                    
                    if "lora" in class_type.lower():
                        for key in inputs:
                            node_key = f"{node_id}_{key}"
                            if node_key in processed_keys:
                                continue
                            
                            key_lower = key.lower()
                            if 'lora' in key_lower and inputs.get(key) not in [None, "", "None"]:
                                lora_value = inputs.get(key, "")
                                
                                # Handle dict-wrapped LoRA values
                                if isinstance(lora_value, dict):
                                    if 'on' in lora_value and not lora_value.get('on'):
                                        processed_keys.add(node_key)
                                        continue
                                    if 'lora' in lora_value:
                                        actual_lora_name = lora_value.get('lora', '')
                                        actual_strength = lora_value.get('strength', 1.0)
                                        if actual_lora_name and actual_lora_name != "None":
                                            display_name = os.path.basename(self.safely_process_value(actual_lora_name))
                                            loras.append(f"  {display_name} (Strength: {actual_strength})")
                                            lora_files.add(actual_lora_name)
                                        processed_keys.add(node_key)
                                        continue
                                
                                # Skip numeric values
                                if isinstance(lora_value, (int, float)):
                                    continue
                                if isinstance(lora_value, str) and lora_value.replace('.', '').replace('-', '').replace('_', '').isdigit():
                                    continue
                                if isinstance(lora_value, dict) and lora_value.get('type'):
                                    processed_keys.add(node_key)
                                    continue
                                
                                # Find corresponding strength value
                                strength = 1.0
                                
                                if '_' in key:
                                    parts = key.rsplit('_', 1)
                                    if len(parts) == 2:
                                        prefix, suffix = parts
                                        strength_patterns = [
                                            f"strength_{suffix}",
                                            f"strength{suffix}",
                                            f"{prefix}_strength_{suffix}",
                                            f"str_{suffix}",
                                        ]
                                        
                                        for pattern in strength_patterns:
                                            if pattern in inputs:
                                                strength = inputs.get(pattern, 1.0)
                                                processed_keys.add(pattern)
                                                break
                                
                                if strength == 1.0:
                                    strength_patterns = [
                                        "strength_model",
                                        "strength",
                                        "model_strength",
                                        "lora_strength"
                                    ]
                                    
                                    for pattern in strength_patterns:
                                        if pattern in inputs:
                                            strength = inputs.get(pattern, 1.0)
                                            processed_keys.add(pattern)
                                            break
                                
                                numbers = re.findall(r'\d+', key)
                                if numbers and strength == 1.0:
                                    num = numbers[-1]
                                    possible_keys = [
                                        f"strength_{num}",
                                        f"strength{num}",
                                        f"str_{num}",
                                        f"lora_strength_{num}"
                                    ]
                                    
                                    for possible_key in possible_keys:
                                        if possible_key in inputs:
                                            strength = inputs.get(possible_key, 1.0)
                                            processed_keys.add(possible_key)
                                            break
                                
                                if lora_value and lora_value != "None":
                                    display_name = os.path.basename(self.safely_process_value(lora_value))
                                    loras.append(f"  {display_name} (Strength: {strength})")
                                    lora_files.add(lora_value)
                                
                                processed_keys.add(node_key)
                
                except Exception as e:
                    print(f"Error processing LoRA: {e}")
                    continue
           
            # Extract models
            models = {}
            model_keywords = {
                'checkpoint': ['ckpt_name', 'checkpoint_name', 'model_name', 'checkpoint'],
                'unet': ['unet_name', 'unet', 'diffusion_model'],
                'clip': ['clip_name', 'clip_name1', 'clip_name2', 'clip', 'text_encoder'],
                'vae': ['vae_name', 'vae', 'autoencoder'],
                't5': ['t5_name', 't5', 't5xxl'],
                'controlnet': ['control_net_name', 'controlnet_name', 'controlnet'],
                'upscaler': ['upscale_model', 'upscaler_name', 'upscaler'],
                'embeddings': ['embedding_name', 'embedding'],
                'hypernetwork': ['hypernetwork_name', 'hypernetwork'],
            }
            
            for node_id, node_data in data.items():
                try:
                    class_type = node_data.get("class_type", "")
                    inputs = node_data.get("inputs", {})
                    
                    # Skip LoRA nodes
                    if "lora" in class_type.lower():
                        continue
                    
                    if "loader" in class_type.lower() or "load" in class_type.lower() or any(keyword in class_type.lower() for keyword in ['checkpoint', 'unet', 'clip', 'vae', 'model']):
                        for model_type, param_names in model_keywords.items():
                            for param_name in param_names:
                                if param_name in inputs:
                                    model_value = inputs.get(param_name)
                                    
                                    # Skip node references
                                    if isinstance(model_value, list) and len(model_value) == 2:
                                        continue
                                    
                                    # Handle dict-wrapped values
                                    if isinstance(model_value, dict):
                                        if 'on' in model_value and not model_value.get('on'):
                                            continue
                                        model_value = model_value.get('model', model_value.get('name', model_value.get('value', '')))
                                    
                                    if isinstance(model_value, list):
                                        continue
                                    
                                    # Don't add LoRA files to models
                                    if model_value in lora_files:
                                        continue
                                    
                                    if model_value and model_value != "None":
                                        display_type = model_type.upper()
                                        
                                        # Special handling for CLIP
                                        if model_type == 'clip':
                                            if param_name == 'clip_name1':
                                                display_type = "CLIP-1"
                                            elif param_name == 'clip_name2':
                                                display_type = "CLIP-2"
                                            elif param_name.startswith('clip_name') and param_name[-1].isdigit():
                                                num = param_name.replace('clip_name', '')
                                                display_type = f"CLIP-{num}"
                                            else:
                                                display_type = "CLIP"
                                        
                                        if display_type not in models:
                                            models[display_type] = self.safely_process_value(model_value)
                                        
                                        if model_type != 'clip':
                                            break
                
                except Exception as e:
                    print(f"Error processing model node: {e}")
                    continue

            # LORA MODELS section
            if loras:
                output.append(f"{emoji_map['lora']} LORA MODELS:")
                seen = set()
                unique_loras = []
                for lora in loras:
                    if lora not in seen:
                        seen.add(lora)
                        unique_loras.append(lora)
                output.extend(unique_loras)
                output.append("")
            
            # MODELS & COMPONENTS section
            if models:
                output.append(f"{emoji_map['models']} MODELS & COMPONENTS:")
                sorted_models = sorted(models.items(), key=lambda x: (
                    0 if x[0] == "Checkpoint" else
                    1 if x[0] == "UNET" else
                    2 if x[0].startswith("CLIP") else
                    3 if x[0] == "VAE" else
                    4, x[0]
                ))
                
                for model_type, model_name in sorted_models:
                    output.append(f"  {model_type}: {model_name}")
                output.append("")
            
            return "\n".join(output)
          
        except Exception as e:
            print(f"Error in parse_comfyui_format: {e}")
            return f"Error processing parameters: {str(e)}"

    def resolve_node_reference(self, data, reference):
        """Helper function to resolve node references like ['124', 0]"""
        if isinstance(reference, list) and len(reference) == 2:
            node_id = str(reference[0])
            if node_id in data:
                node_data = data[node_id]
                if node_data.get("class_type") == "easy int":
                    return node_data["inputs"].get("value")
            # If we can't resolve the reference, return a string representation
            return f"[Node Reference: {reference[0]}]"
        return reference

    def extract_individual_params(self, text, format_type):
        """Extract individual parameters for output connections"""
        positive = ""
        negative = ""

        try:
            text = self.safely_process_value(text)

            if format_type == "comfyui":
                clean_text = text.strip()
                if clean_text.startswith("Prompt: "):
                    clean_text = clean_text[8:]

                try:
                    data = json.loads(clean_text)

                    for node_id, node_data in data.items():
                        try:
                            class_type = node_data.get("class_type", "")

                            if "CLIPTextEncode" in class_type or "TextEncode" in class_type or "Prompt" in class_type:
                                title = node_data.get("_meta", {}).get("title", "").lower()

                                # Try multiple text field names
                                text_content = None
                                for text_key in ["text", "prompt", "conditioning", "string"]:
                                    if text_key in node_data["inputs"]:
                                        text_content = node_data["inputs"].get(text_key)
                                        break

                                if text_content is None:
                                    continue

                                if self.is_node_reference(text_content):
                                    continue

                                text_content = self.safely_process_value(text_content)

                                if not text_content or not text_content.strip():
                                    continue

                                # Better title matching logic
                                is_negative = any(neg_word in title for neg_word in ["negative", "neg"])
                                is_positive = any(pos_word in title for pos_word in ["positive", "pos", "prompt"]) and not is_negative

                                if is_positive or ("prompt" in title and not is_negative):
                                    if not positive:
                                        positive = text_content
                                elif is_negative:
                                    negative = text_content
                                elif not positive and not negative:
                                    # If no title hints, assume first one is positive
                                    positive = text_content

                        except Exception as e:
                            continue

                except Exception as e:
                    print(f"Error parsing JSON in extract_individual: {e}")

            elif format_type == "webui":
                lines = text.strip().split('\n')
                metadata_line = ""

                for line in lines:
                    if line.startswith("Negative prompt:"):
                        negative = line.replace("Negative prompt:", "").strip()
                    elif re.search(r'Steps:\s*\d+', line):
                        metadata_line = line
                    elif not metadata_line and not line.startswith("Negative prompt:"):
                        positive += line + " "

                positive = positive.strip()

        except Exception as e:
            print(f"Error in extract_individual_params: {e}")

        return positive, negative


# Node registration
NODE_CLASS_MAPPINGS = {
    "SimpleReadableMetadataSG": SimpleReadableMetadataSG
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "SimpleReadableMetadataSG": "Simple Readable Metadata-SG"
}

__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS"]
