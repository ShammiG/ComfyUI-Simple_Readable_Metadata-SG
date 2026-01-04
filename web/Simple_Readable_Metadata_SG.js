import { app } from "../../scripts/app.js";

app.registerExtension({
    name: "SimpleReadableMetadataSG.display",
    async beforeRegisterNodeDef(nodeType, nodeData, app) {
        if (nodeData.name === "SimpleReadableMetadataSG") {
            const onNodeCreated = nodeType.prototype.onNodeCreated;
            nodeType.prototype.onNodeCreated = function () {
                const result = onNodeCreated ? onNodeCreated.apply(this, arguments) : undefined;

                // Set minimum width only on initial creation
                const minWidth = 400;
                if (this.size[0] < minWidth) {
                    this.size[0] = minWidth;
                }

                return result;
            };

            // Persistence handling
            const onConfigure = nodeType.prototype.onConfigure;
            nodeType.prototype.onConfigure = function(info) {
                onConfigure?.apply(this, arguments);
                if (info.imagePropertiesText) this.imagePropertiesText = info.imagePropertiesText;
                if (info.imageMetadataText) this.imageMetadataText = info.imageMetadataText;
            };

            const onSerialize = nodeType.prototype.onSerialize;
            nodeType.prototype.onSerialize = function(info) {
                const data = onSerialize ? onSerialize.apply(this, arguments) : info;
                if (this.imagePropertiesText) data.imagePropertiesText = this.imagePropertiesText;
                if (this.imageMetadataText) data.imageMetadataText = this.imageMetadataText;
                return data;
            };

            // Capture data from Python execution
            const onExecuted = nodeType.prototype.onExecuted;
            nodeType.prototype.onExecuted = function (message) {
                onExecuted?.apply(this, arguments);
                
                // Python sends everything in message.text as an array            
                if (message.text && Array.isArray(message.text)) {
                    // Split into Properties (lines 0-2) and Metadata (lines 4+)
                    this.imagePropertiesText = message.text.slice(0, 3); // Lines 0,1,2
                    this.imageMetadataText = message.text.slice(4);      // Lines 4,5,6,...
                }
            };

            // Draw on canvas
            const origDrawForeground = nodeType.prototype.onDrawForeground;
            nodeType.prototype.onDrawForeground = function (ctx) {
                origDrawForeground?.apply(this, arguments);

                // Get Current Dropdown Value
                const showInfoWidget = this.widgets?.find((w) => w.name === "show_info");
                const showMode = showInfoWidget ? showInfoWidget.value : "both";

                if (showMode === "none") return;

                ctx.save();
                ctx.font = "12px monospace";
                ctx.fillStyle = "#ccc";
                const textX = 10;
                const lineHeight = 18;
                let currentY = 25; // Start Y position

                // A. Draw Properties (Resolution, Ratio, File Size)
                if ((showMode === "both" || showMode === "properties") && this.imagePropertiesText) {
                    this.imagePropertiesText.forEach((line) => {
                        ctx.fillText(line, textX, currentY);
                        currentY += lineHeight;
                    });
                    
                    // Add spacing if we're showing both sections
                    if (showMode === "both" && this.imageMetadataText) {
                        currentY += 5; 
                    }
                }

                // B. Draw Metadata (Model, Seed, Sampler, etc.)
                if ((showMode === "both" || showMode === "metadata") && this.imageMetadataText) {
                    this.imageMetadataText.forEach((line) => {
                        ctx.fillText(line, textX, currentY);
                        currentY += lineHeight;
                    });
                }

                ctx.restore();
            };
        }
    },
});
