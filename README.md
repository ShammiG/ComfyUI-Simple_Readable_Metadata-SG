# ComfyUI Simple Readable Metadata-SG     
**Extract and View Image as well as Video Metadata of ComfyUI as well as of ForgeUI or Automatic 1111 generated images in Easily Readable Format as well as raw metadata**             
**Supports PNG as well as WEBP formats for images and  mp4 and webm for video**

#    ❗Attention❗
**Switch Node 2.0 OFF, If comfyUI version 0.3.76 or newer**
<br>

![dsf](https://github.com/user-attachments/assets/127e3340-237c-4364-8f65-910fab6c1b9a)

**Reason:** With new ComfyUI update, it changed the frontend from Lite graph rendering to Vue with **nodes 2.0**.         
&emsp;&emsp;&emsp; &nbsp; So, now it requires rewriting and troubleshooting with about 2000 lines of code!      
&emsp;&emsp;&emsp; &nbsp; which i am not currently leaned towards into.

---
Simple Readable Metadata-SG Nodes Info
---
# Big Update: New Node to Save Prompt directly in metadata, show ALL embedded text in workflow from already generated images and more ( 4 Jan. 2025)
  **Check Details Below**      
   
---
Nodes Info:
---

**Has Six nodes:**        
**1. Simple_Readable_Metadata-SG**            
**2.** Simple_Readable_Metadata_**VIDEO_SG**              
**3.** Simple_Readable_Metadata_**Text_Viewer_SG**      
**4.** Simple_Readable_Metadata_**Save_Text_SG**      
**5.** Simple_Readable_Metadata_**MAX-SG**          
**6.** Simple_Readable_Metadata_**Save_Prompt_SG** 
<br>

***● Text Viewer has addtional features, check more details below***        
# Nodes info:
**View Image Metadata in Easy Readable Format: like Prompt , LoRa, Model used, Seed, Steps, CFG, Sampler, Scheduler etc. Also supports outputs for these as well as showing Raw Metadata.** 

<br>
<img width="1405" height="1018" alt="node Info" src="https://github.com/user-attachments/assets/afad5169-86e2-4816-9811-a3e6db25e705" />

<br>
<br>

# Update 2.5.0:       
By default, if comfyUI CLIP Text Encode Node's text box's input is connected, it will show up as (empty) in the Simple_Readable_Metadata output.         
These two fixes try to overcome that. **One for future, One for old.**          
● **Simple_Readable_Metadata_Save_Prompt_SG:** A **new node** for future workflows inject Positive prompt in metadata.                
Basically add this to the Final Text output just before the CLIP Text Encode Prompt Node's text box.                        
This will add the prompt to the metadata such that it is readable by Simple_Readable_Metadata.       
● **Implement Show All Text in Workflow:** A similar attempt to be able to see prompt from **old images** whose CLIP text encode box had input connected.         
This basically dumps all the text info present in the workflow, so you can look for prompts.         
● **Copy Positive Button in Text Viewer Node:** **Copies Positive Prompt directly** without the need to select it (bothered me personally a lot).           
Make sure to verify the final copied text.         
● **Added show_info options for display:** You can optionally show/hide properties, metadata or both.

# Update 2.0.0:
● **Added New Node: Simple_Readable_Metadata (Video):** Extract prompt, model used, lora used, scheduler, sampler, steps, CFG **now for mp4 and webm videos too**       
● **Updated Text Viewer to include font size:** Updated the text viewer, now you can select font size. [it's included from ComfyUI-Text Tools-SG](https://github.com/ShammiG/ComfyUI_Text_Tools_SG)          
● **added filename_output to all extracting nodes**

# Update 1.5.0:

**Added new node: Simple_Readable_Metadata_Save text** -- Save text in .txt or .json format (optional pretty json) [included Part of ComfyUI-Text Tools-SG](https://github.com/ShammiG/ComfyUI_Text_Tools_SG)
<br>
# Update 1.0.1: 

● **Added support for WEBP format:** Now also extracts and displays metadata from WEBP images.           
● **Filename and Filesize:** Also shows filename and filesize at the top, in the output of Simple_Readable_Metadata      
● **New output for filename:** New output for filename (can be connnected to SaveImage node or text viewer node.)
<br>
<br>

# All Nodes' Details:

**1. Simple_Readable_Metadata-SG** : Has limited outputs for image      
<br>

<img width="1334" height="519" alt="Screenshot 2025-11-15 104842" src="https://github.com/user-attachments/assets/7f914696-dbc2-4773-b265-a6ccc9d10915" />     
<br>
<br>

**2. Simple_Readable_Metadata_VIDEO_SG:** Now extract all the prompt info and everything **for videos too.**       

<br>

https://github.com/user-attachments/assets/450e6d77-3634-45b2-b4f5-aa130d32f402

**3. Simple_Readable_Metadata_Save_Text_SG:** Node for saving text file or in json for raw metadata 


**4. Simple_Readable_Metadata_MAX-SG** : Has **Lot** of outputs
<br>

<img width="1229" height="770" alt="Screenshot 2025-11-15 104947" src="https://github.com/user-attachments/assets/d0b55db6-001c-495d-b835-cd0b6975ac94" />
<br>
<br>

**5. Simple_Readable_Metadata_Text_Viewer-SG:** Text Viewer with export text to file, copy text, select text, delete text, day/night theme etc.

<br>

<img width="783" height="1188" alt="Screenshot 2025-12-06 201653" src="https://github.com/user-attachments/assets/a99605e6-f748-405d-a7e5-3bfe2d9d7818" />

<br>
<br>

**Text Viewer Features:** 

***NEW:*** **Copy Positive:** **Copies Positive Prompt directly** without the need to select it            
🗑️&emsp;&emsp;**Delete all displayed text**          
📋&emsp;&emsp;**Copy all or selected text**          
✔️&emsp;&emsp;**Select all text**          
📄&emsp;&emsp;**Paste text**          
🔍&emsp;&emsp;**Search / Highlight Word/s**          
🎯&emsp;&emsp;**Filter lines with Word/s**          
💾&emsp;&emsp;**Export viewed text to file**          
&ensp;{} &emsp;&emsp;**Toggle Pretty Json**          
🌙&emsp;&emsp;**Switch Day/Night Theme**          
↔️&ensp; &ensp;**Toggle Text Wrapping**          
          
***❗NOTE Pasted/ Viewed Text WILL BE Over-written if input node is connected***
<br>
<br>

● Also supports Raw_Metadata output with toggle for pretty json
<br>

<img width="1675" height="845" alt="Screenshot 2025-11-15 122254" src="https://github.com/user-attachments/assets/ad483df2-348f-43cf-bf34-b01466165207" />
<br>
<br>

● Also shows img2img workflows like Image editing workflows/ models , loras etc.
<br>

<img width="1553" height="871" alt="Screenshot 2025-11-15 104247" src="https://github.com/user-attachments/assets/03fb93bc-fee0-4f9d-9f0f-a23a9301aea3" />
<br>
<br>

● View Upscale Model used info:
<br>

<img width="1829" height="916" alt="Screenshot 2025-11-15 103602" src="https://github.com/user-attachments/assets/5f0424ae-980a-48dd-a1d0-7a76cba976e3" />
<br>
<br>

# Installation:   
<br>

**OPTION 1 :** If you have [ComfyUI-Manager](https://github.com/Comfy-Org/ComfyUI-Manager):       
        
**1.** Click on Manager>Custom Nodes Manager           
            
**2.** you can directly search ComfyUI-Simple_Readable_Metadata-SG or my Username ShammiG and click install.           
              
**3.** Restart comfyUI from manager:     
<br> 

**OPTION 2 :** If you don't have comfyUI Manager installed:           
          
**1.** Open command prompt inside ComfyUI/custom_nodes directory.              
       
**2.** Clone this repository into your **ComfyUI/custom_nodes** directory:    
       
    git clone https://github.com/ShammiG/ComfyUI-Image_Properties_SG.git            
          
**3.**  Install **requirements.txt**
      
**4.** **Restart ComfyUI**             
  Search and add the desired node to your workflow.
<br>
<br>

# 👑 Appreciate and support my work on --> [Patreon](https://www.patreon.com/c/ShammiG)
<br>
              
# 🥛 Buy Me a LASSI ----> [BuyMeCoffee](buymeacoffee.com/shammig)      
<br>
<br


     
# Also checkout my other nodes: 
[ComfyUI-Show-Clock-in-CMD-Console-SG](https://github.com/ShammiG/ComfyUI-Show-Clock-in-CMD-Console-SG)
<br>

<img width="1124" height="963" alt="Show clock in CMD console comfyUI" src="https://github.com/user-attachments/assets/6b8825ed-94fb-4baa-9e0f-05bd731740a8" />
<br>
<br>

[ComfyUI-Image_Properties_SG](https://github.com/ShammiG/ComfyUI-Image_Properties_SG)
<br>

![Load Image And View Properties](https://github.com/user-attachments/assets/24bfdde5-98ee-46e7-aec4-230d9f3fe6ec)
<br>
<br>

**This was made possible with the help of Perplexity Pro : Claude 4.5 Sonet**      
   Big Shoutout to them.









