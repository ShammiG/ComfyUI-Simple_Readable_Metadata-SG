import json

class SavePositivePromptSG:
    def __init__(self):
        pass
    
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "text": ("STRING", {"forceInput": True, "tooltip": "FINAL TEXT to be connected to CLIP Text Encode Positive node's box"}),
            },
            "hidden": {
                "unique_id": "UNIQUE_ID",
                "prompt": "PROMPT",
                "extra_pnginfo": "EXTRA_PNGINFO",
            },
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("connect_to_CLIP_text_encode",)
    OUTPUT_TOOLTIPS = ("Connect this to your POSITIVE CLIP Text Encode node input.",)
    FUNCTION = "execute"
    CATEGORY = "utils/metadata"
    OUTPUT_NODE = True

    def execute(self, text, unique_id=None, prompt=None, extra_pnginfo=None):
        if prompt is not None and unique_id is not None:
            # Try both string and int keys to be safe
            node_data = prompt.get(str(unique_id))
            if not node_data:
                node_data = prompt.get(int(unique_id))

            if node_data:
                if "inputs" not in node_data:
                    node_data["inputs"] = {}
                # Overwrite the link with the actual text
                node_data["inputs"]["text"] = text
                
                # Force title metadata
                if "_meta" not in node_data: node_data["_meta"] = {}
                node_data["_meta"]["title"] = "Positive Prompt (Saved)"

        if extra_pnginfo is not None:
            extra_pnginfo[f"PositivePrompt_{unique_id}"] = text

        return {"ui": {"text": [text]}, "result": (text,)}

class SaveNegativePromptSG:
    def __init__(self):
        pass
    
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "text": ("STRING", {"forceInput": True, "tooltip": "FINAL TEXT to be connected to CLIP Text Encode Negative node's box"}),
            },
            "hidden": {
                "unique_id": "UNIQUE_ID",
                "prompt": "PROMPT",
                "extra_pnginfo": "EXTRA_PNGINFO",
            },
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("connect_to_CLIP_text_encode",)
    OUTPUT_TOOLTIPS = ("Connect this to your NEGATIVE CLIP Text Encode node input.",)
    FUNCTION = "execute"
    CATEGORY = "utils/metadata"
    OUTPUT_NODE = True

    def execute(self, text, unique_id=None, prompt=None, extra_pnginfo=None):
        if prompt is not None and unique_id is not None:
            # Try both string and int keys
            node_data = prompt.get(str(unique_id))
            if not node_data:
                node_data = prompt.get(int(unique_id))

            if node_data:
                if "inputs" not in node_data:
                    node_data["inputs"] = {}
                # Overwrite the link with the actual text
                node_data["inputs"]["text"] = text
                
                # Force title metadata
                if "_meta" not in node_data: node_data["_meta"] = {}
                node_data["_meta"]["title"] = "Negative Prompt (Saved)"

        if extra_pnginfo is not None:
            extra_pnginfo[f"NegativePrompt_{unique_id}"] = text

        return {"ui": {"text": [text]}, "result": (text,)}

NODE_CLASS_MAPPINGS = {
    "SavePositivePromptSG": SavePositivePromptSG,
    "SaveNegativePromptSG": SaveNegativePromptSG
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "SavePositivePromptSG": "Save Positive Prompt (Metadata)-SG",
    "SaveNegativePromptSG": "Save Negative Prompt (Metadata)-SG"
}
