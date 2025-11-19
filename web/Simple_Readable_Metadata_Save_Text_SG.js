import { app } from "../../scripts/app.js";

app.registerExtension({
    name: "SimpleReadableMetadataSaveTextSG.AutoNumbering",
    async beforeRegisterNodeDef(nodeType, nodeData, app) {
        if (nodeData.name === "SimpleReadableMetadataSaveTextSG") {
            const onNodeCreated = nodeType.prototype.onNodeCreated;
            
            nodeType.prototype.onNodeCreated = function() {
                const result = onNodeCreated ? onNodeCreated.apply(this, arguments) : undefined;
                
                // Find widgets
                const filenamePrefixWidget = this.widgets?.find(w => w.name === "filename_prefix");
                const fileFormatWidget = this.widgets?.find(w => w.name === "file_format");
                
                // Add helpful tooltip
                if (filenamePrefixWidget) {
                    filenamePrefixWidget.options = filenamePrefixWidget.options || {};
                    filenamePrefixWidget.options.placeholder = "Enter filename prefix (e.g., output/myfile)";
                }
                
                // Set initial node size
                const nodeWidth = 320;
                const nodeHeight = 120;
                this.setSize([nodeWidth, nodeHeight]);
                
                // Store the original onResize
                const originalOnResize = this.onResize;
                
                // Override onResize to maintain minimum size
                this.onResize = function(size) {
                    size[0] = Math.max(size[0], 280);
                    size[1] = Math.max(size[1], 100);
                    if (originalOnResize) {
                        originalOnResize.apply(this, [size]);
                    }
                };
                
                return result;
            };
            
            // Handle the output similar to SaveImage
            const onExecuted = nodeType.prototype.onExecuted;
            nodeType.prototype.onExecuted = function(message) {
                if (onExecuted) {
                    onExecuted.apply(this, arguments);
                }
                
                if (message?.text_files) {
                    console.log("[SaveTextFile] Files saved:", message.text_files);
                }
            };
        }
    }
});
