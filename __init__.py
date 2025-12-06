import os
from .Simple_Readable_Metadata_MAX_SG import SimpleReadableMetadataMAXSG
from .Simple_Readable_Metadata_SG import SimpleReadableMetadataSG
from .Simple_Readable_Metadata_Text_Viewer_SG import SimpleReadableMetadataTextViewerSG
from .Simple_Readable_Metadata_Save_Text_SG import SimpleReadableMetadataSaveTextSG
from .Simple_Readable_Metadata_VIDEO_SG import SimpleReadableMetadataVideoSG

NODE_CLASS_MAPPINGS = {
    "SimpleReadableMetadataMAXSG": SimpleReadableMetadataMAXSG,
    "SimpleReadableMetadataSG": SimpleReadableMetadataSG,
    "Simple Readable Metadata Text Viewer-SG": SimpleReadableMetadataTextViewerSG,
    "SimpleReadableMetadataSaveTextSG": SimpleReadableMetadataSaveTextSG,
    "SimpleReadableMetadataVideoSG": SimpleReadableMetadataVideoSG
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "SimpleReadableMetadataMAXSG": "Simple Readable Metadata MAX-SG",
    "SimpleReadableMetadataSG": "Simple Readable Metadata-SG",
    "Simple Readable Metadata Text Viewer-SG": "Simple Readable Metadata 🧾 Text Viewer-SG",
    "SimpleReadableMetadataSaveTextSG": "Simple Readable Metadata Save Text-SG",
    "SimpleReadableMetadataVideoSG": "Simple Readable Metadata (VIDEO)-SG"
}

WEB_DIRECTORY = "./web"
__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS", "WEB_DIRECTORY"]
