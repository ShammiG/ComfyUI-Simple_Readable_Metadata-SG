import torch
import os
import folder_paths
import numpy as np
import cv2
import json
import re
import subprocess
from types import SimpleNamespace
from PIL import Image, ImageSequence

class SimpleReadableMetadataVideoSG:
    """
    Load video, extract frames.
    - Output 1 (String): Full detailed metadata (Prompts, Lora, etc.)
    - Node Display: Concise metadata (Res, Ratio, Model, Seed, Sampler)
    """
    
    CATEGORY = "image/video"

    @classmethod
    def INPUT_TYPES(cls):
        input_dir = folder_paths.get_input_directory()
        files = [f for f in os.listdir(input_dir) if os.path.isfile(os.path.join(input_dir, f))]
        return {
            "required": {
                "video": (sorted(files), {"video_upload": True}),
                "force_rate": ("INT", {"default": 0, "min": 0, "max": 60, "step": 1, "display": "number", "tooltip": "Target FPS. 0 = Original."}),
                "max_frames": ("INT", {"default": 0, "min": 0, "max": 10000, "step": 1, "display": "number", "tooltip": "Limit total frames. 0 = All."}),
                "resize_long_edge": ("INT", {"default": 0, "min": 0, "max": 4096, "step": 64, "display": "number", "tooltip": "Resize longest side. 0 = Original."}),
                "emoji_in_readable_text": ("BOOLEAN", {"default": True})
            },
            "ui": {
                "text": {"min_width": 450},
            },
        }

    RETURN_TYPES = ("STRING", "IMAGE", "MASK", "INT", "INT", "STRING", "STRING", "STRING", "STRING", "INT")
    RETURN_NAMES = ("Simple_Readable_Metadata", "frames", "mask", "frame_count", "fps", "filename_text", "metadata_raw", "Positive_Prompt", "Negative_Prompt", "seed")
    FUNCTION = "load_video_analyze"
    OUTPUT_NODE = True

    @classmethod
    def IS_CHANGED(cls, video, force_rate, max_frames, resize_long_edge, emoji_in_readable_text):
        video_path = folder_paths.get_annotated_filepath(video)
        if os.path.exists(video_path):
            stat = os.stat(video_path)
            return f"{video}_{stat.st_mtime}_{stat.st_size}_{force_rate}_{max_frames}_{resize_long_edge}"
        return "N/A"

    @classmethod
    def VALIDATE_INPUTS(cls, video, **kwargs):
        if not folder_paths.exists_annotated_filepath(video):
            return "Invalid video file: {}".format(video)
        return True
 
    # ============================METADATA EXTRACTION UTILS====================================

    def extract_raw_video_metadata(self, video_path):
        """Smart metadata extraction based on file type."""
        ext = os.path.splitext(video_path)[1].lower()
        
        # STRATEGY A: PIL (WebP, APNG, GIF)
        if ext in ['.webp', '.png', '.gif']:
            try:
                with Image.open(video_path) as img:
                    if 'prompt' in img.info: return img.info['prompt']
                    if 'workflow' in img.info: return json.dumps({"workflow_only": img.info['workflow']})
                    if 'exif' in img.info:
                        try:
                             exif_data = img.info['exif']
                             if isinstance(exif_data, bytes):
                                 exif_str = exif_data.decode('utf-8', errors='ignore')
                                 if "prompt:" in exif_str: return exif_str.split("prompt:")[1].split("\x00")[0]
                        except: pass
            except: pass

        # STRATEGY B: FFPROBE
        try:
            command = ['ffprobe', '-v', 'quiet', '-print_format', 'json', '-show_format', '-show_streams', video_path]
            result = subprocess.run(command, capture_output=True, text=True, encoding='utf-8')
            if result.returncode == 0:
                data = json.loads(result.stdout)
                sources = []
                if 'format' in data and 'tags' in data['format']: sources.append(data['format']['tags'])
                if 'streams' in data:
                    for stream in data['streams']:
                        if stream.get('codec_type') == 'video' and 'tags' in stream: sources.append(stream['tags'])
                
                for tags in sources:
                    for key in ['comment', 'prompt', 'workflow', 'description', 'user_data']:
                        for t_key, t_val in tags.items():
                            if t_key.lower() == key:
                                clean_val = t_val.strip()
                                if clean_val.startswith('{') or "Prompt:" in clean_val: return clean_val
        except: pass
        return None

    def get_concise_display_info(self, metadata_raw):
        """Extracts specific fields for the CONCISE NODE DISPLAY (UI)."""
        info = {
            "model": "N/A",
            "seed": "N/A",
            "steps": "N/A",
            "cfg": "N/A",
            "sampler": "N/A",
            "scheduler": "N/A"
        }
        
        if not metadata_raw: return info

        try:
            if metadata_raw.strip().startswith("Prompt:"): metadata_raw = metadata_raw.strip()[7:]
            data = json.loads(metadata_raw)

            # 1. MODEL EXTRACTION
            
            # A) Workflow format (Nodes list)
            if "nodes" in data and isinstance(data["nodes"], list):
                for node in data["nodes"]:
                    nt = node.get("type", "").lower()
                    
                    # SKIP undesired loaders
                    if "lora" in nt or "clip" in nt or "control" in nt or "vae" in nt:
                        continue

                    # Look for Checkpoint or Loader
                    if "checkpoint" in nt or "loader" in nt:
                        vals = node.get("widgets_values")
                        if vals and isinstance(vals, list) and len(vals) > 0:
                            val = str(vals[0]).lower()
                            if ".safetensors" in val or ".ckpt" in val or ".gguf" in val or ".pt" in val:
                                info["model"] = vals[0]
                                break 

            # B) Prompt format (Dict of nodes)
            if info["model"] == "N/A":
                for k, v in data.items():
                    ct = v.get("class_type", "").lower()
                    
                    # SKIP undesired loaders
                    if "lora" in ct or "clip" in ct or "control" in ct or "vae" in ct:
                        continue
                        
                    inputs = v.get("inputs", {})
                    
                    # CheckpointLoader (Standard)
                    if "ckpt_name" in inputs: 
                        info["model"] = inputs["ckpt_name"]
                        break
                    
                    # UNETLoader
                    if "unet_name" in inputs:
                        info["model"] = f"{inputs['unet_name']} (UNET)"
                        break
                    
                    # GGUF Loader
                    if "gguf_name" in inputs:
                        info["model"] = f"{inputs['gguf_name']} (GGUF)"
                        break

                    # Generic Model/Checkpoint keys (fallback)
                    if "model_name" in inputs:
                        info["model"] = inputs["model_name"]
                        break
                    
                    if "checkpoint" in inputs and isinstance(inputs["checkpoint"], str):
                        info["model"] = inputs["checkpoint"]
                        break

            # 2. SAMPLING
            if isinstance(data, dict) and "nodes" not in data:
                for k, v in data.items():
                    if "Sampler" in v.get("class_type", ""):
                        inputs = v.get("inputs", {})
                        info["seed"] = inputs.get("seed", inputs.get("noise_seed", "N/A"))
                        info["steps"] = inputs.get("steps", "N/A")
                        info["cfg"] = inputs.get("cfg", "N/A")
                        info["sampler"] = inputs.get("sampler_name", "N/A")
                        info["scheduler"] = inputs.get("scheduler", "N/A")
                        break
        except: pass
        return info

    def extract_full_readable_text(self, metadata_raw, include_emojis=True):
        """Generates the FULL DETAILED text output for the STRING output."""
        if not metadata_raw: return "No metadata found."
        try:
            if metadata_raw.strip().startswith("Prompt:"): metadata_raw = metadata_raw.strip()[7:]
            data = json.loads(metadata_raw)
            
            lines = []
            emoji_map = {"models": "🧠", "sampling": "🎯", "prompts": "📝", "lora": "🎨"} if include_emojis else {k: "" for k in ["models", "sampling", "prompts", "lora"]}
            
            # Model (Reuse concise logic to get the MAIN model name)
            info = self.get_concise_display_info(metadata_raw)
            lines.append(f"{emoji_map['models']} MODEL: {info['model']}\n")

            # Sampling
            if isinstance(data, dict) and "nodes" not in data: 
                for k, v in data.items():
                    if "Sampler" in v.get("class_type", ""):
                        inputs = v["inputs"]
                        lines.append(f"{emoji_map['sampling']} SAMPLING SETTINGS:")
                        lines.append(f" Seed      : {inputs.get('seed', inputs.get('noise_seed', 'N/A'))}")
                        lines.append(f" Steps     : {inputs.get('steps', 'N/A')}")
                        lines.append(f" CFG Scale : {inputs.get('cfg', 'N/A')}")
                        lines.append(f" Sampler   : {inputs.get('sampler_name', 'N/A')}")
                        lines.append(f" Scheduler : {inputs.get('scheduler', 'N/A')}\n")
                        break

            # Prompts
            lines.append(f"{emoji_map['prompts']} PROMPTS:")
            pos, neg = [], []
            if isinstance(data, dict) and "nodes" not in data:
                for k, v in data.items():
                    if "CLIPTextEncode" in v.get("class_type", ""):
                        t = v["inputs"].get("text", "").strip()
                        if "negative" in v.get("_meta", {}).get("title", "").lower(): neg.append(t)
                        else: pos.append(t)
            lines.append(f" Positive: {', '.join(pos) if pos else '(empty)'}")
            lines.append(f" Negative: {', '.join(neg) if neg else '(empty)'}\n")

            # Components
            lines.append(f"{emoji_map['models']} MODELS & COMPONENTS:")
            if isinstance(data, dict) and "nodes" not in data:
                for k, v in data.items():
                    ct = v.get("class_type", "")
                    inputs = v.get("inputs", {})
                    if "CheckpointLoader" in ct: lines.append(f" Checkpoint: {inputs.get('ckpt_name')}")
                    if "LoaderGGUF" in ct: lines.append(f" GGUF: {inputs.get('gguf_name')}")
                    if "LoraLoader" in ct: lines.append(f" LoRA: {inputs.get('lora_name')} (Str: {inputs.get('strength_model')})")
                    if "VAELoader" in ct: lines.append(f" VAE: {inputs.get('vae_name')}")

            return "\n".join(lines)
        except:
            return metadata_raw 

    def extract_individual_params(self, metadata_raw):
        pos, neg, seed = "", "", 0
        try:
            if metadata_raw and metadata_raw.strip().startswith("{"):
                data = json.loads(metadata_raw)
                if isinstance(data, dict) and "nodes" not in data:
                    for k, v in data.items():
                         if "Sampler" in v.get("class_type", ""):
                             seed = int(v["inputs"].get("seed", v["inputs"].get("noise_seed", 0)))
                             break
                    for k, v in data.items():
                        if "CLIPTextEncode" in v.get("class_type", ""):
                            inputs = v.get("inputs", {})
                            title = v.get("_meta", {}).get("title", "").lower()
                            text = inputs.get("text", "")
                            if "negative" in title: neg += text + " "
                            else: pos += text + " "
        except: pass
        return pos.strip(), neg.strip(), seed

    def gcd(self, a, b):
        while b: a, b = b, a % b
        return a
        
    def find_closest_standard_ratio(self, decimal_ratio):
        standard_ratios = [(1.0, '1:1'), (1.25, '5:4'), (1.33333, '4:3'), (1.5, '3:2'), (1.6, '16:10'), (1.77778, '16:9'), (2.33333, '21:9')]
        closest, min_diff = None, float('inf')
        for val, lbl in standard_ratios:
            diff = abs(val - decimal_ratio)
            if diff < min_diff: min_diff, closest = diff, lbl
        return closest if min_diff <= 0.05 else None


    # ==================================== MAIN EXECUTION========================================

    def load_video_analyze(self, video, force_rate, max_frames, resize_long_edge, emoji_in_readable_text=True):
        video_path = folder_paths.get_annotated_filepath(video)
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened(): raise RuntimeError(f"Could not open video: {video_path}")

        original_fps = cap.get(cv2.CAP_PROP_FPS)
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        
        frames = []
        step = 1
        if force_rate > 0 and force_rate < original_fps: step = max(1, int(original_fps / force_rate))
        effective_fps = original_fps / step if step > 1 else original_fps
        if force_rate > 0: effective_fps = force_rate

        count = 0
        output_count = 0
        while True:
            ret, frame = cap.read()
            if not ret: break
            if count % step == 0:
                if resize_long_edge > 0:
                    h, w = frame.shape[:2]
                    if max(h, w) > resize_long_edge:
                        scale = resize_long_edge / max(h, w)
                        frame = cv2.resize(frame, (int(w * scale), int(h * scale)), interpolation=cv2.INTER_AREA)
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB).astype(np.float32) / 255.0
                frames.append(torch.from_numpy(frame))
                output_count += 1
                if max_frames > 0 and output_count >= max_frames: break
            count += 1
        cap.release()
        
        if not frames: raise RuntimeError("No frames extracted.")
        output_frames = torch.stack(frames)
        mask = torch.ones((output_frames.shape[0], output_frames.shape[1], output_frames.shape[2]), dtype=torch.float32)

        # --- METADATA LOGIC ---
        
        # 1. Physical Stats
        resolution_mp = (width * height) / 1_000_000
        try: file_size_mb = os.path.getsize(video_path) / (1024 * 1024)
        except: file_size_mb = 0.0
        
        divisor = self.gcd(width, height)
        ar_dec = width / height
        std_ratio = self.find_closest_standard_ratio(ar_dec)
        ratio_str = f"{width//divisor}:{height//divisor}"
        if std_ratio and std_ratio != ratio_str: ratio_str += f" or {std_ratio}"
        else: ratio_str += f" or {ar_dec:.2f}:1"

        # 2. Extract Raw Metadata
        metadata_raw = self.extract_raw_video_metadata(video_path)
        
        # 3. GENERATE UI DISPLAY TEXT 
        gen_info = self.get_concise_display_info(metadata_raw)
        ui_lines = []
        ui_lines.append(f"{width}x{height} | {resolution_mp:.2f}MP")
        ui_lines.append(f"Ratio: {ratio_str}")
        ui_lines.append(f"File Size: {file_size_mb:.2f}MB")
        ui_lines.append("") 
        ui_lines.append(f"Model: {gen_info['model']}")
        ui_lines.append(f"Seed: {gen_info['seed']} | Steps: {gen_info['steps']} | CFG: {gen_info['cfg']}")
        ui_lines.append(f"Sampler: {gen_info['sampler']} | Scheduler: {gen_info['scheduler']}")

        # 4. GENERATE OUTPUT STRING (Full/Rich)
        full_readable_text = f"=== Video Information ===\nFilename: {os.path.basename(video_path)}\n{width}x{height} | {resolution_mp:.2f}MP | {file_size_mb:.2f}MB\nFPS: {int(effective_fps)} | Duration: {(count/original_fps if original_fps else 0):.1f}s\n\n"
        if metadata_raw:
            full_readable_text += self.extract_full_readable_text(metadata_raw, emoji_in_readable_text)
        else:
            full_readable_text += "(No embedded ComfyUI generation metadata detected in file)"

        # Return Values
        pos, neg, seed = self.extract_individual_params(metadata_raw)
        
        return {
            "ui": {"text": ui_lines},
            "result": (
                full_readable_text,    
                output_frames, 
                mask, 
                len(frames), 
                int(effective_fps), 
                os.path.basename(video_path), 
                metadata_raw if metadata_raw else "", 
                pos, 
                neg, 
                seed
            )
        }

NODE_CLASS_MAPPINGS = {
    "SimpleReadableMetadataVideoSG": SimpleReadableMetadataVideoSG
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "SimpleReadableMetadataVideoSG": "Simple Readable Metadata (Video)-SG"
}
