class SimpleReadableMetadataTextViewerSG:
    CATEGORY = "text/utils"
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "text": ("STRING", {"default": "", "forceInput": True})
            }
        }
    
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("text",)
    FUNCTION = "texteditor"
    OUTPUT_NODE = True
    
    def texteditor(self, text: str, **kwargs):
        return {
            "ui": {
                "text": [text]
            },
            "result": (text,)
        }

NODE_CLASS_MAPPINGS = {
    "Simple Readable Metadata Text Viewer-SG": SimpleReadableMetadataTextViewerSG
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "Simple Readable Metadata Text Viewer-SG": "Simple Readable Metadata 🧾 Text Viewer-SG"
}
