import { app } from "../../scripts/app.js";

app.registerExtension({
    name: "SimpleReadableMetadataVideoSG.display",
    async beforeRegisterNodeDef(nodeType, nodeData, app) {
        if (nodeData.name === "SimpleReadableMetadataVideoSG") {
            const onNodeCreated = nodeType.prototype.onNodeCreated;
            nodeType.prototype.onNodeCreated = function () {
                const result = onNodeCreated ? onNodeCreated.apply(this, arguments) : undefined;

                const minWidth = 400; 
                if (this.size[0] < minWidth) {
                    this.size[0] = minWidth;
                }

                const videoWidget = this.widgets?.find((w) => w.name === "video");

                if (videoWidget) {
                    const self = this;
                    let lastValue = videoWidget.value;

                    // Create a timer to check for value changes
                    const checkInterval = setInterval(() => {
                        if (videoWidget.value !== lastValue) {
                            lastValue = videoWidget.value;
                            if (videoWidget.value && typeof videoWidget.value === 'string') {
                                // Load basic metadata for preview
                                const videoEl = document.createElement('video');
                                videoEl.preload = "metadata";
                                const videoUrl = `/view?filename=${encodeURIComponent(videoWidget.value)}&type=input&subfolder=`;
                                
                                videoEl.onloadedmetadata = function() {
                                    const width = videoEl.videoWidth;
                                    const height = videoEl.videoHeight;
                                    const resolution_mp = (width * height / 1_000_000).toFixed(2);

                                    const line1 = `${width}x${height} | ${resolution_mp}MP`;
                                    const line2 = "Ratio: Calculating...";
                                    const line3 = "(Run node to see full metadata)";

                                    // Update display
                                    self.imageParamsText = [line1, line2, line3];
                                    app.graph.setDirtyCanvas(true, true);
                                };
                                videoEl.src = videoUrl;
                            }
                        }
                    }, 500);

                    const onRemoved = this.onRemoved;
                    this.onRemoved = function() {
                        clearInterval(checkInterval);
                        if (onRemoved) {
                            onRemoved.apply(this, arguments);
                        }
                    };
                }

                return result;
            };

            const onConfigure = nodeType.prototype.onConfigure;
            nodeType.prototype.onConfigure = function(info) {
                onConfigure?.apply(this, arguments);
                if (info.imageParamsText) {
                    this.imageParamsText = info.imageParamsText;
                }
            };

            const onSerialize = nodeType.prototype.onSerialize;
            nodeType.prototype.onSerialize = function(info) {
                const data = onSerialize ? onSerialize.apply(this, arguments) : info;
                if (this.imageParamsText) {
                    data.imageParamsText = this.imageParamsText;
                }
                return data;
            };

            const onExecuted = nodeType.prototype.onExecuted;
            nodeType.prototype.onExecuted = function (message) {
                onExecuted?.apply(this, arguments);
                if (message.text) {
                    this.imageParamsText = message.text;
                }
            };

            const origDrawForeground = nodeType.prototype.onDrawForeground;
            nodeType.prototype.onDrawForeground = function (ctx) {
                origDrawForeground?.apply(this, arguments);

                if (this.imageParamsText) {
                    ctx.save();
                    ctx.font = "12px monospace";
                    ctx.fillStyle = "#ccc";
                    const textX = 10;
                    const lineHeight = 18;
                    
                    // Position text at top
                    const startY = 25;

                    // Draw each line
                    this.imageParamsText.forEach((line, index) => {
                        const yPos = startY + (index * lineHeight);
                        ctx.fillText(line, textX, yPos);
                    });
                    ctx.restore();
                }
            };
        }
    }
});
