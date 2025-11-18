# ComfyUI Simple Readable Metadata-SG     
View Image Metadata of ComfyUI **as well as of ForgeUI or Automatic 1111 generated images** in Easily Readable Format         
**Supports PNG as well as WEBP formats**

**Has three nodes:**        
**1. Simple_Readable_Metadata-SG**            
**2. Simple_Readable_Metadata_MAX-SG**              
**3. Simple_Readable_Metadata_Text_Viewer_SG**          
<br>
***● Text Viewer has addtional features, check more details below***        
# Nodes info:
**View Image Metadata in Easy Readable Format: like Prompt , LoRa, Model used, Seed, Steps, CFG, Sampler, Scheduler etc. Also supports outputs for these as well as showing Raw Metadata.** 
<br>
<img width="1471" height="944" alt="Screenshot 2025-11-18 223046" src="https://github.com/user-attachments/assets/42f86f57-071d-485f-8fbd-76814fc4170f" />

<br>
<br>

# Update : 
**1. Added support for WEBP format:** Now also extracts and displays metadata from WEBP images.           
**2. Filename and Filesize:** Also shows filename and filesize at the top, in the output of Simple_Readable_Metadata      
**3. New output for filename:** New output for filename (can be connnected to SaveImage node or text viewer node.)
<br>
<br>

# Details:

**1. Simple_Readable_Metadata-SG** : Has limited outputs        
<br>

<img width="1334" height="519" alt="Screenshot 2025-11-15 104842" src="https://github.com/user-attachments/assets/7f914696-dbc2-4773-b265-a6ccc9d10915" />     
<br>
<br>

**2. Simple_Readable_Metadata_MAX-SG** : Has **Lot** of outputs
<br>

<img width="1229" height="770" alt="Screenshot 2025-11-15 104947" src="https://github.com/user-attachments/assets/d0b55db6-001c-495d-b835-cd0b6975ac94" />
<br>
<br>

**3. Simple_Readable_Metadata_Text_Viewer-SG:** Text Viewer with export text to file, copy text, select text, delete text, day/night theme etc.
<br>

<img width="713" height="983" alt="Screenshot 2025-11-15 113923" src="https://github.com/user-attachments/assets/186e207e-a38c-4228-a025-de214553e851" />
<br>
<br>

**Text Viewer Features:**       
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
      
**3.** **Restart ComfyUI**             
  Search and add the desired node to your workflow.
<br>
<br>

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

# Appreciate and support my work on [Patreon](https://www.patreon.com/c/ShammiG)
<br>
<br>

**This was made possible with the help of Perplexity Pro : Claude 4.5 Sonet**      
   Big Shoutout to them.









