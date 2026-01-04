import { app } from "../../scripts/app.js";

app.registerExtension({
    name: "SimpleReadableMetadataTextViewerSG",
    async beforeRegisterNodeDef(nodeType, nodeData, appRef) {
        if (nodeData?.name !== "Simple Readable Metadata Text Viewer-SG") return;

        const origOnNodeCreated = nodeType.prototype.onNodeCreated;
        nodeType.prototype.onNodeCreated = function () {
            origOnNodeCreated?.apply(this, arguments);

            // ============ COUNTER ROW (Top) ============
            const counterContainer = document.createElement("div");
            counterContainer.style.position = "absolute";
            counterContainer.style.top = "0";
            counterContainer.style.left = "0";
            counterContainer.style.right = "0";
            counterContainer.style.display = "flex";
            counterContainer.style.justifyContent = "flex-start";
            counterContainer.style.alignItems = "center";
            counterContainer.style.gap = "10px";
            counterContainer.style.padding = "2px 5px";
            counterContainer.style.fontSize = "10px";
            counterContainer.style.fontFamily = "monospace";
            counterContainer.style.height = "20px";
            counterContainer.style.backgroundColor = "rgba(0, 0, 0, 0.3)";
            counterContainer.style.zIndex = "10";
            counterContainer.style.pointerEvents = "none";
            counterContainer.style.overflow = "hidden";
            counterContainer.style.minWidth = "0";

            // Counter display
            const counter = document.createElement("div");
            counter.style.color = "#999";
            counter.style.whiteSpace = "nowrap";
            counter.style.flex = "0 0 auto";
            counter.textContent = "0 chars | 0 words | 0 lines";
            counterContainer.appendChild(counter);

            // ============ BUTTON BAR ROW (Below Counter) ============
            const buttonBarContainer = document.createElement("div");
            buttonBarContainer.style.position = "absolute";
            buttonBarContainer.style.top = "22px";
            buttonBarContainer.style.left = "0";
            buttonBarContainer.style.right = "0";
            buttonBarContainer.style.display = "flex";
            buttonBarContainer.style.gap = "3px";
            buttonBarContainer.style.flexWrap = "nowrap";
            buttonBarContainer.style.alignItems = "center";
            buttonBarContainer.style.padding = "2px 5px";
            buttonBarContainer.style.height = "25px";
            buttonBarContainer.style.backgroundColor = "rgba(0, 0, 0, 0.26)";
            buttonBarContainer.style.zIndex = "10";
            buttonBarContainer.style.pointerEvents = "auto";
            buttonBarContainer.style.overflow = "hidden";
            buttonBarContainer.style.minWidth = "0";

            // Main textarea (declared early for button references)
            const box = document.createElement("textarea");
            box.readOnly = true;
            box.className = "comfy-multiline-input";
            box.placeholder = "No text connected...";
            box.style.resize = "none";
            box.style.boxSizing = "border-box";
            box.style.fontFamily = "monospace";
            box.style.fontSize = "14px";
            box.style.lineHeight = "1.5";
            box.style.whiteSpace = "pre-wrap";
            box.style.overflowWrap = "break-word";
            box.style.width = "100%";
            box.style.height = "100%";
            box.style.paddingTop = "49px"; // 20 (counter) + 25 (button bar) + 4px buffer

            // Highlight overlay div
            const highlightDiv = document.createElement("div");
            highlightDiv.style.position = "absolute";
            highlightDiv.style.top = "0";
            highlightDiv.style.left = "0";
            highlightDiv.style.width = "100%";
            highlightDiv.style.height = "100%";
            highlightDiv.style.pointerEvents = "none";
            highlightDiv.style.fontFamily = "monospace";
            highlightDiv.style.fontSize = "14px";
            highlightDiv.style.lineHeight = "1.5";
            highlightDiv.style.whiteSpace = "pre-wrap";
            highlightDiv.style.padding = "0";
            highlightDiv.style.paddingTop = "49px";
            highlightDiv.style.boxSizing = "border-box";
            highlightDiv.style.color = "transparent";
            highlightDiv.style.overflow = "hidden";
            highlightDiv.style.zIndex = "5";
            highlightDiv.style.display = "none";

            // ============ BUTTONS ============
            // Toggle Theme button
            const themeBtn = document.createElement("button");
            themeBtn.textContent = "🌙";
            themeBtn.title = "Toggle Theme (Dark/Light)";
            themeBtn.style.fontSize = "12px";
            themeBtn.style.padding = "1px 4px";
            themeBtn.style.cursor = "pointer";
            themeBtn.style.minWidth = "24px";
            themeBtn.style.width = "24px";
            themeBtn.style.flexShrink = "0";
            themeBtn.style.flexBasis = "24px";

            this.properties = this.properties || {};
            this.properties.theme = this.properties.theme || "Dark";

            themeBtn.onclick = () => {
                this.properties.theme = this.properties.theme === "Dark" ? "Light" : "Dark";
                themeBtn.textContent = this.properties.theme === "Dark" ? "🌙" : "☀️";
                this._applyTheme(this.properties.theme);
            };

            // Copy button
            const copyBtn = document.createElement("button");
            copyBtn.textContent = "📋";
            copyBtn.title = "Copy to clipboard";
            copyBtn.style.fontSize = "12px";
            copyBtn.style.padding = "1px 4px";
            copyBtn.style.cursor = "pointer";
            copyBtn.style.minWidth = "24px";
            copyBtn.style.width = "24px";
            copyBtn.style.flexShrink = "0";
            copyBtn.style.flexBasis = "24px";

            copyBtn.onclick = () => {
                const start = box.selectionStart;
                const end = box.selectionEnd;
                const textToCopy = (start !== end) ? box.value.substring(start, end) : box.value;
                navigator.clipboard.writeText(textToCopy);
                copyBtn.textContent = "✓";
                setTimeout(() => {
                    copyBtn.textContent = "📋";
                }, 1500);
            };

            // Text Wrap toggle button
            const wrapBtn = document.createElement("button");
            wrapBtn.textContent = "↔️";
            wrapBtn.title = "Toggle Text Wrap";
            wrapBtn.style.fontSize = "12px";
            wrapBtn.style.padding = "1px 4px";
            wrapBtn.style.cursor = "pointer";
            wrapBtn.style.minWidth = "24px";
            wrapBtn.style.width = "24px";
            wrapBtn.style.flexShrink = "0";
            wrapBtn.style.flexBasis = "24px";

            this.properties.word_wrap = this.properties.word_wrap ?? true;
            wrapBtn.style.opacity = this.properties.word_wrap ? "1" : "0.5";

            wrapBtn.onclick = () => {
                this.properties.word_wrap = !this.properties.word_wrap;
                wrapBtn.style.opacity = this.properties.word_wrap ? "1" : "0.5";
                box.style.whiteSpace = this.properties.word_wrap ? "pre-wrap" : "pre";
                box.style.overflowWrap = this.properties.word_wrap ? "break-word" : "normal";
                highlightDiv.style.whiteSpace = this.properties.word_wrap ? "pre-wrap" : "pre";
                highlightDiv.style.overflowWrap = this.properties.word_wrap ? "break-word" : "normal";
            };

            // Text Highlight toggle button
            const highlightBtn = document.createElement("button");
            highlightBtn.textContent = "🔍";
            highlightBtn.title = "Search / Highlight Text";
            highlightBtn.style.fontSize = "12px";
            highlightBtn.style.padding = "1px 4px";
            highlightBtn.style.cursor = "pointer";
            highlightBtn.style.minWidth = "24px";
            highlightBtn.style.width = "24px";
            highlightBtn.style.flexShrink = "0";
            highlightBtn.style.flexBasis = "24px";

            this.properties.text_filter = this.properties.text_filter ?? false;
            highlightBtn.style.opacity = this.properties.text_filter ? "1" : "0.5";

            // Text Filter button
            const filterBtn = document.createElement("button");
            filterBtn.textContent = "🎯";
            filterBtn.title = "Filter / Show Only Matching Lines";
            filterBtn.style.fontSize = "12px";
            filterBtn.style.padding = "1px 4px";
            filterBtn.style.cursor = "pointer";
            filterBtn.style.minWidth = "24px";
            filterBtn.style.width = "24px";
            filterBtn.style.flexShrink = "0";
            filterBtn.style.flexBasis = "24px";

            this.properties.line_filter = this.properties.line_filter ?? false;
            filterBtn.style.opacity = this.properties.line_filter ? "1" : "0.5";

            // Export button
            const exportBtn = document.createElement("button");
            exportBtn.textContent = "💾";
            exportBtn.title = "Export to file";
            exportBtn.style.fontSize = "12px";
            exportBtn.style.padding = "1px 4px";
            exportBtn.style.cursor = "pointer";
            exportBtn.style.minWidth = "24px";
            exportBtn.style.width = "24px";
            exportBtn.style.flexShrink = "0";
            exportBtn.style.flexBasis = "24px";

            exportBtn.onclick = () => {
                const now = new Date();
                const day = String(now.getDate()).padStart(2, '0');
                const month = String(now.getMonth() + 1).padStart(2, '0');
                const year = now.getFullYear();
                const hours = String(now.getHours()).padStart(2, '0');
                const minutes = String(now.getMinutes()).padStart(2, '0');
                const seconds = String(now.getSeconds()).padStart(2, '0');
                const dateTime = `${day}-${month}-${year}_${hours}_${minutes}_${seconds}`;

                const blob = new Blob([box.value], { type: 'text/plain' });
                const url = URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = `comfy_${dateTime}.txt`;
                a.click();
                URL.revokeObjectURL(url);
            };

            // ============ PRETTY JSON TOGGLE BUTTON ============
            let prettyJsonBtn = document.createElement("button");
            prettyJsonBtn.textContent = "{}";
            prettyJsonBtn.title = "Toggle Pretty JSON Format";
            prettyJsonBtn.style.fontSize = "12px";
            prettyJsonBtn.style.padding = "1px 4px";
            prettyJsonBtn.style.cursor = "pointer";
            prettyJsonBtn.style.minWidth = "24px";
            prettyJsonBtn.style.width = "24px";
            prettyJsonBtn.style.flexShrink = "0";
            prettyJsonBtn.style.flexBasis = "24px";

            this.properties.pretty_json_mode = this.properties.pretty_json_mode ?? false;
            prettyJsonBtn.style.opacity = this.properties.pretty_json_mode ? "1" : "0.5";

            prettyJsonBtn.onclick = () => {
                this.properties.pretty_json_mode = !this.properties.pretty_json_mode;
                prettyJsonBtn.style.opacity = this.properties.pretty_json_mode ? "1" : "0.5";

                if (this.properties.pretty_json_mode) {
                    try {
                        const textToParse = this._tv_original_text.trim();
                        if (!textToParse) {
                            this.properties.pretty_json_mode = false;
                            prettyJsonBtn.style.opacity = "0.5";
                            return;
                        }

                        let jsonObj;
                        try {
                            jsonObj = JSON.parse(textToParse);
                        } catch (parseError) {
                            try {
                                jsonObj = eval('(' + textToParse + ')');
                            } catch (evalError) {
                                this.properties.pretty_json_mode = false;
                                prettyJsonBtn.style.opacity = "0.5";
                                return;
                            }
                        }

                        const prettyJson = JSON.stringify(jsonObj, null, 2);
                        this._tv_pretty_json_text = prettyJson;
                        this.properties.pretty_json_text = prettyJson;
                        box.value = prettyJson;
                        this._updateCounter();
                    } catch (err) {
                        this.properties.pretty_json_mode = false;
                        prettyJsonBtn.style.opacity = "0.5";
                        return;
                    }
                } else {
                    box.value = this._tv_original_text;
                    this._updateCounter();
                    if (this.properties.text_filter) {
                        this._applyFilter();
                    }
                    if (this.properties.line_filter) {
                        this._applyLineFilter();
                    }
                }
            };

            // Select All button
            const selectAllBtn = document.createElement("button");
            selectAllBtn.textContent = "☑️";
            selectAllBtn.title = "Select All Text";
            selectAllBtn.style.fontSize = "12px";
            selectAllBtn.style.padding = "1px 4px";
            selectAllBtn.style.cursor = "pointer";
            selectAllBtn.style.minWidth = "24px";
            selectAllBtn.style.width = "24px";
            selectAllBtn.style.flexShrink = "0";

            selectAllBtn.onclick = () => {
                box.select();
                box.focus();
                selectAllBtn.textContent = "✓";
                setTimeout(() => {
                    selectAllBtn.textContent = "☑️";
                }, 1500);
            };

            // Paste button
            const pasteBtn = document.createElement("button");
            pasteBtn.textContent = "📄";
            pasteBtn.title = "Paste from clipboard";
            pasteBtn.style.fontSize = "12px";
            pasteBtn.style.padding = "1px 4px";
            pasteBtn.style.cursor = "pointer";
            pasteBtn.style.minWidth = "24px";
            pasteBtn.style.width = "24px";
            pasteBtn.style.flexShrink = "0";

            pasteBtn.onclick = async () => {
                try {
                    const clipboardText = await navigator.clipboard.readText();
                    const start = box.selectionStart;
                    const end = box.selectionEnd;
                    const currentValue = box.value;
                    const newValue = currentValue.substring(0, start) + clipboardText + currentValue.substring(end);
                    box.value = newValue;

                    const newCursorPos = start + clipboardText.length;
                    box.setSelectionRange(newCursorPos, newCursorPos);
                    box.focus();

                    this._tv_original_text = newValue;
                    this._tv_pretty_json_text = "";
                    this.properties.text = newValue;
                    this.properties.pretty_json_text = "";

                    const textWidget = this.widgets?.find(w => w.name === "text");
                    if (textWidget) {
                        textWidget.value = newValue;
                    }

                    this._updateCounter();

                    if (this._tv_auto_resize !== false) {
                        requestAnimationFrame(() => {
                            const contentSize = this._calculateContentSize();
                            if (contentSize) {
                                this.size = contentSize;
                                this.onResize(this.size);
                                if (this.graph && this.graph.canvas) {
                                    this.graph.canvas.setDirty(true, true);
                                }
                            }
                        });
                    }

                    pasteBtn.textContent = "✓";
                    setTimeout(() => {
                        pasteBtn.textContent = "📄";
                    }, 1500);
                } catch (err) {
                    console.error('Failed to read clipboard:', err);
                    pasteBtn.textContent = "✗";
                    setTimeout(() => {
                        pasteBtn.textContent = "📄";
                    }, 1500);
                }
            };

            // Delete All button
            const deleteAllBtn = document.createElement("button");
            deleteAllBtn.textContent = "🗑️";
            deleteAllBtn.title = "Delete All Text";
            deleteAllBtn.style.fontSize = "12px";
            deleteAllBtn.style.padding = "1px 4px";
            deleteAllBtn.style.cursor = "pointer";
            deleteAllBtn.style.minWidth = "24px";
            deleteAllBtn.style.width = "24px";
            deleteAllBtn.style.flexShrink = "0";
            deleteAllBtn.style.flexBasis = "24px";

            deleteAllBtn.style.opacity = "1";

            // === DELETE CONFIRMATION CONTROLS (Inline) ===
            const deleteConfirmControls = document.createElement("div");
            deleteConfirmControls.style.position = "absolute";
            deleteConfirmControls.style.top = "49px"; 
            deleteConfirmControls.style.left = "0";
            deleteConfirmControls.style.right = "0";
            deleteConfirmControls.style.display = "none";
            deleteConfirmControls.style.flexDirection = "column";
            deleteConfirmControls.style.gap = "10px";
            deleteConfirmControls.style.padding = "12px";
            deleteConfirmControls.style.backgroundColor = "rgba(0, 0, 0, 0.9)";
            deleteConfirmControls.style.border = "3px solid #ff6b6b";
            deleteConfirmControls.style.borderRadius = "4px";
            deleteConfirmControls.style.boxShadow = "0 2px 8px rgba(0, 0, 0, 0.5)";
            deleteConfirmControls.style.zIndex = "15";
            deleteConfirmControls.style.backdropFilter = "blur(4px)";

            // Warning message
            const deleteMessage = document.createElement("div");
            deleteMessage.textContent = "⚠️ Delete all text? This cannot be undone.";
            deleteMessage.style.fontSize = "13px";
            deleteMessage.style.color = "#ff6b6b";
            deleteMessage.style.fontWeight = "bold";
            deleteMessage.style.textAlign = "center";
            deleteMessage.style.fontFamily = "monospace";

            // Button container
            const deleteButtonContainer = document.createElement("div");
            deleteButtonContainer.style.display = "flex";
            deleteButtonContainer.style.gap = "10px";
            deleteButtonContainer.style.justifyContent = "center";

            // Confirm Delete button
            const confirmDeleteBtn = document.createElement("button");
            confirmDeleteBtn.textContent = "Delete All";
            confirmDeleteBtn.style.fontSize = "12px";
            confirmDeleteBtn.style.padding = "6px 16px";
            confirmDeleteBtn.style.cursor = "pointer";
            confirmDeleteBtn.style.border = "2px solid #ff6b6b";
            confirmDeleteBtn.style.borderRadius = "3px";
            confirmDeleteBtn.style.backgroundColor = "#ff6b6b";
            confirmDeleteBtn.style.color = "#fff";
            confirmDeleteBtn.style.fontWeight = "bold";

            // Cancel button
            const cancelDeleteBtn = document.createElement("button");
            cancelDeleteBtn.textContent = "Cancel";
            cancelDeleteBtn.style.fontSize = "12px";
            cancelDeleteBtn.style.padding = "6px 16px";
            cancelDeleteBtn.style.cursor = "pointer";
            cancelDeleteBtn.style.border = "2px solid #555";
            cancelDeleteBtn.style.borderRadius = "3px";
            cancelDeleteBtn.style.backgroundColor = "#333";
            cancelDeleteBtn.style.color = "#fff";
            cancelDeleteBtn.style.fontWeight = "bold";

            // Hover effects
            confirmDeleteBtn.onmouseenter = () => confirmDeleteBtn.style.backgroundColor = "#ff5252";
            confirmDeleteBtn.onmouseleave = () => confirmDeleteBtn.style.backgroundColor = "#ff6b6b";
            cancelDeleteBtn.onmouseenter = () => cancelDeleteBtn.style.backgroundColor = "#666";
            cancelDeleteBtn.onmouseleave = () => cancelDeleteBtn.style.backgroundColor = "#333";

            // Assemble controls
            deleteButtonContainer.appendChild(confirmDeleteBtn);
            deleteButtonContainer.appendChild(cancelDeleteBtn);
            deleteConfirmControls.appendChild(deleteMessage);
            deleteConfirmControls.appendChild(deleteButtonContainer);

            // Delete execution function
            const executeDelete = () => {
                box.value = "";
                if (!this.properties) this.properties = {};
                
                this._tv_original_text = "";
                this._tv_pretty_json_text = "";
                this.properties.text = "";
                this.properties.pretty_json_text = "";
                
                const textWidget = this.widgets?.find(w => w.name === "text");
                if (textWidget) textWidget.value = "";

                this._updateCounter();
                
                // Clear filters
                if (this._tv_filter_input) this._tv_filter_input.value = "";
                if (this._tv_line_filter_input) this._tv_line_filter_input.value = "";
                
                // Reset modes
                this.properties.pretty_json_mode = false;
                if (prettyJsonBtn) prettyJsonBtn.style.opacity = "0.5";
                
                // Clear highlights
                if (this._tv_highlight_div) this._tv_highlight_div.innerHTML = '';
                this._tv_match_positions = [];
                if (matchCounter) matchCounter.textContent = "0 / 0";
                if (lineMatchCounter) lineMatchCounter.textContent = "0 lines";

                // Close dialog
                deleteConfirmControls.style.display = "none";
                deleteAllBtn.style.opacity = "1";
                this._updateTextPadding();

                // Success feedback
                deleteAllBtn.textContent = "✓";
                setTimeout(() => { deleteAllBtn.textContent = "🗑️"; }, 1500);
            };

            // Cancel function
            const cancelDelete = () => {
                deleteConfirmControls.style.display = "none";
                deleteAllBtn.style.opacity = "1";
                this._updateTextPadding();
            };

            // Button handlers
            confirmDeleteBtn.onclick = executeDelete;
            cancelDeleteBtn.onclick = cancelDelete;

            // Main Delete Button Click (Toggle)
            deleteAllBtn.onclick = () => {
                const isVisible = deleteConfirmControls.style.display === "flex";
                
                // Close other controls (like Font Size) if we are opening Delete
                if (!isVisible) {
                    if (typeof textSizeControls !== 'undefined') textSizeControls.style.display = 'none';
                    if (typeof textSizeBtn !== 'undefined') textSizeBtn.style.opacity = '1';
                    if (highlightControls) highlightControls.style.display = 'none';
                    if (filterControls) filterControls.style.display = 'none';
                }

                deleteConfirmControls.style.display = isVisible ? "none" : "flex";
                deleteAllBtn.style.opacity = isVisible ? "1" : "0.5";
                
                this._updateTextPadding();
            };
           
            // ============ TEXT SIZE BUTTON ============
            const textSizeBtn = document.createElement("button");
            textSizeBtn.textContent = "Aa";
            textSizeBtn.title = "Text Size (6-72)";
            textSizeBtn.style.fontSize = "12px";
            textSizeBtn.style.padding = "1px 4px";
            textSizeBtn.style.cursor = "pointer";
            textSizeBtn.style.minWidth = "24px";
            textSizeBtn.style.width = "24px";
            textSizeBtn.style.flexShrink = "0";
            textSizeBtn.style.fontWeight = "bold";
            textSizeBtn.style.flexBasis = "24px";
            textSizeBtn.style.opacity = "1";

            // Text size controls (inline popup)
            const textSizeControls = document.createElement("div");
            textSizeControls.style.position = "absolute";
            textSizeControls.style.top = "49px";
            textSizeControls.style.left = "0";
            textSizeControls.style.right = "0";
            textSizeControls.style.display = "none";
            textSizeControls.style.flexDirection = "row";
            textSizeControls.style.gap = "5px";
            textSizeControls.style.alignItems = "center";
            textSizeControls.style.padding = "8px";
            textSizeControls.style.backgroundColor = "rgba(0, 0, 0, 0.85)";
            textSizeControls.style.border = "3px solid #4CAF50";
            textSizeControls.style.borderRadius = "4px";
            textSizeControls.style.boxShadow = "0 2px 8px rgba(0, 0, 0, 0.5)";
            textSizeControls.style.zIndex = "15";
            textSizeControls.style.backdropFilter = "blur(4px)";

            // Label
            const textSizeLabel = document.createElement("span");
            textSizeLabel.textContent = "Text Size:";
            textSizeLabel.style.fontSize = "13px";
            textSizeLabel.style.color = "#4CAF50";
            textSizeLabel.style.fontWeight = "bold";
            textSizeLabel.style.fontFamily = "monospace";

            // Input field
            const textSizeInput = document.createElement("input");
            textSizeInput.type = "number";
            textSizeInput.min = "6";
            textSizeInput.max = "72";
            textSizeInput.value = this.properties.font_size ?? 14;
            textSizeInput.style.width = "60px";
            textSizeInput.style.height = "28px";
            textSizeInput.style.boxSizing = "border-box";
            textSizeInput.style.fontFamily = "monospace";
            textSizeInput.style.fontSize = "12px";
            textSizeInput.style.padding = "4px";
            textSizeInput.style.border = "2px solid #555";
            textSizeInput.style.borderRadius = "3px";
            textSizeInput.style.backgroundColor = "#1e1e1e";
            textSizeInput.style.color = "#d4d4d4";

            // Apply button
            const applyBtn = document.createElement("button");
            applyBtn.textContent = "Apply";
            applyBtn.style.fontSize = "12px";
            applyBtn.style.padding = "4px 12px";
            applyBtn.style.cursor = "pointer";
            applyBtn.style.border = "2px solid #4CAF50";
            applyBtn.style.borderRadius = "3px";
            applyBtn.style.backgroundColor = "#4CAF50";
            applyBtn.style.color = "#fff";
            applyBtn.style.fontWeight = "bold";

            // Close button
            const closeBtn = document.createElement("button");
            closeBtn.textContent = "✕";
            closeBtn.style.fontSize = "14px";
            closeBtn.style.padding = "4px 8px";
            closeBtn.style.cursor = "pointer";
            closeBtn.style.border = "2px solid #555";
            closeBtn.style.borderRadius = "3px";
            closeBtn.style.backgroundColor = "#333";
            closeBtn.style.color = "#fff";
            closeBtn.style.fontWeight = "bold";

            // Assemble controls
            textSizeControls.appendChild(textSizeLabel);
            textSizeControls.appendChild(textSizeInput);
            textSizeControls.appendChild(applyBtn);
            textSizeControls.appendChild(closeBtn);

            // Apply size function
            const applySize = () => {
                const sizeNum = parseInt(textSizeInput.value);
                if (!isNaN(sizeNum) && sizeNum >= 6 && sizeNum <= 72) {
                    this.properties.font_size = sizeNum;
                    box.style.fontSize = `${sizeNum}px`;
                    if (highlightDiv) highlightDiv.style.fontSize = `${sizeNum}px`;
                    textSizeControls.style.display = 'none';
                    textSizeBtn.style.opacity = '1';
                    this._updateTextPadding();
                } else {
                    textSizeInput.style.borderColor = '#f44336';
                    setTimeout(() => textSizeInput.style.borderColor = '#555', 1000);
                }
            };

            // Close function
            const closeTextSize = () => {
                textSizeControls.style.display = "none";
                textSizeBtn.style.opacity = "1";
                this._updateTextPadding();
            };

            // Button click handlers
            applyBtn.onclick = applySize;
            closeBtn.onclick = closeTextSize;

            // Enter to apply, Escape to close
            textSizeInput.addEventListener("keydown", (e) => {
                if (e.key === "Enter") {
                    e.preventDefault();
                    applySize();
                } else if (e.key === "Escape") {
                    e.preventDefault();
                    closeTextSize();
                }
            });

            // Toggle text size controls
            textSizeBtn.onclick = () => {
                const isVisible = textSizeControls.style.display === "flex";
                textSizeControls.style.display = isVisible ? "none" : "flex";
                textSizeBtn.style.opacity = isVisible ? "1" : "0.5";
                
                if (!isVisible) {
                    textSizeInput.value = this.properties.font_size || 14;
                    setTimeout(() => textSizeInput.focus(), 100);
                    // Force update padding to show controls
                    this._updateTextPadding();
                } else {
                    this._updateTextPadding();
                }
            };      

            // Copy Positive Prompt button
            const copyPosBtn = document.createElement("button");
            copyPosBtn.textContent = "Copy Positive";
            copyPosBtn.title = "Extract & Copy Positive Prompt";
            copyPosBtn.style.fontSize = "10px";
            copyPosBtn.style.padding = "1px 2px";
            copyPosBtn.style.cursor = "pointer";
            copyPosBtn.style.minWidth = "50px";
            copyPosBtn.style.width = "50px";
            copyPosBtn.style.flexShrink = "0";
            copyPosBtn.style.flexBasis = "24px";

            copyPosBtn.onclick = () => {
                const text = box.value;
                let positivePrompt = "";
                
                // METHOD 1: Line-by-line state machine parser (Safest)
                const lines = text.split('\n');
                let capturing = false;
                let buffer = [];
                
                for (let i = 0; i < lines.length; i++) {
                    const line = lines[i];
                    
                    // Start capturing when we see "Positive:"
                    if (line.trim().startsWith("Positive:")) {
                        capturing = true;
                        // Remove "Positive:" prefix from the first line
                        let content = line.substring(line.indexOf("Positive:") + 9).trim();
                        if (content) buffer.push(content);
                        continue;
                    }
                    
                    if (capturing) {
                        // STOP capturing conditions:
                        // 1. Line starts with "Negative:"
                        // 2. Line starts with an Emoji (next section)
                        // 3. Line matches a Section Header style (=== header ===)
                        // 4. Empty line (often separates prompts from next section)
                        
                        const trimmed = line.trim();
                        if (trimmed.startsWith("Negative:") || 
                            trimmed.startsWith("Negative prompt:") ||
                            /^(===|[\u{1F300}-\u{1F9FF}]|Step|Size|Model)/u.test(trimmed)) {
                            break;
                        }
                        
                        // If it's just an empty line, it MIGHT be the end, or just a paragraph break.
                        // But usually ComfyUI prompts are dense blocks.
                        // Let's assume a double-newline (empty line) ends the prompt section.
                        if (trimmed === "") {
                            break; 
                        }
                        
                        buffer.push(line);
                    }
                }
                
                if (buffer.length > 0) {
                    positivePrompt = buffer.join("\n").trim();
                } 
                // METHOD 2: Fallback for A1111 raw format (where prompt is at the very top)
                else if (text.indexOf("Steps:") !== -1 || text.indexOf("Negative prompt:") !== -1) {
                    const negIndex = text.indexOf("Negative prompt:");
                    const stepsIndex = text.indexOf("Steps:");
                    let cutIndex = text.length;
                    
                    if (negIndex !== -1) cutIndex = Math.min(cutIndex, negIndex);
                    if (stepsIndex !== -1) cutIndex = Math.min(cutIndex, stepsIndex);
                    
                    if (cutIndex < text.length) {
                        positivePrompt = text.substring(0, cutIndex).trim();
                    }
                }

                // Clean up
                if (positivePrompt === "(empty)") positivePrompt = "";

                if (positivePrompt) {
                    navigator.clipboard.writeText(positivePrompt);
                    copyPosBtn.textContent = "✓";
                    setTimeout(() => { copyPosBtn.textContent = "+P"; }, 1500);
                } else {
                    copyPosBtn.textContent = "✗";
                    setTimeout(() => { copyPosBtn.textContent = "+P"; }, 1500);
                }
            };



            // Append buttons to button bar in order
            buttonBarContainer.appendChild(deleteAllBtn);
            buttonBarContainer.appendChild(copyBtn);
            buttonBarContainer.appendChild(selectAllBtn);
            buttonBarContainer.appendChild(pasteBtn);
            buttonBarContainer.appendChild(highlightBtn);
            buttonBarContainer.appendChild(filterBtn);
            buttonBarContainer.appendChild(exportBtn);
            buttonBarContainer.appendChild(prettyJsonBtn);
            buttonBarContainer.appendChild(themeBtn);
            buttonBarContainer.appendChild(wrapBtn);
            buttonBarContainer.appendChild(textSizeBtn);
            buttonBarContainer.appendChild(copyPosBtn);           

            // Wrapper for textarea and overlays
            const textareaWrapper = document.createElement("div");
            textareaWrapper.style.position = "relative";
            textareaWrapper.style.width = "100%";
            textareaWrapper.style.height = "100%";
            textareaWrapper.style.paddingBottom = "2px";
            textareaWrapper.style.boxSizing = "border-box";

            textareaWrapper.appendChild(box);
            textareaWrapper.appendChild(highlightDiv);
            textareaWrapper.appendChild(counterContainer);
            textareaWrapper.appendChild(buttonBarContainer);
            textareaWrapper.appendChild(textSizeControls);
            textareaWrapper.appendChild(deleteConfirmControls);


            // ============ HIGHLIGHT CONTROLS ============
            const highlightControls = document.createElement("div");
            highlightControls.style.position = "absolute";
            highlightControls.style.top = "49px";
            highlightControls.style.left = "0";
            highlightControls.style.right = "0";
            highlightControls.style.display = "none";
            highlightControls.style.flexDirection = "row";
            highlightControls.style.gap = "5px";
            highlightControls.style.alignItems = "center";
            highlightControls.style.padding = "8px";
            highlightControls.style.backgroundColor = "rgba(0, 0, 0, 0.85)";
            highlightControls.style.border = "3px solid #FFD700";
            highlightControls.style.borderRadius = "4px";
            highlightControls.style.boxShadow = "0 2px 8px rgba(0, 0, 0, 0.5)";
            highlightControls.style.zIndex = "15";
            highlightControls.style.backdropFilter = "blur(4px)";
            highlightControls.style.height = "32px";

            // Filter input
            const filterInput = document.createElement("input");
            filterInput.type = "text";
            filterInput.placeholder = "Highlight text (regex supported)...";
            filterInput.style.width = "200px";
            filterInput.style.minWidth = "200px";
            filterInput.style.maxWidth = "600px";
            filterInput.style.height = "28px";
            filterInput.style.boxSizing = "border-box";
            filterInput.style.fontFamily = "monospace";
            filterInput.style.fontSize = "12px";
            filterInput.style.padding = "4px";
            filterInput.style.border = "2px solid #555";
            filterInput.style.borderRadius = "3px";

            filterInput.addEventListener('input', function() {
                const charWidth = 8;
                const padding = 50;
                const minWidth = 200;
                const maxWidth = 600;
                const calculatedWidth = Math.min(maxWidth, Math.max(minWidth, this.value.length * charWidth + padding));
                this.style.width = calculatedWidth + 'px';
            });

            // Match counter display
            const matchCounter = document.createElement("span");
            matchCounter.style.fontSize = "13px";
            matchCounter.style.fontWeight = "bold";
            matchCounter.style.color = "#FFD700";
            matchCounter.style.minWidth = "60px";
            matchCounter.style.fontFamily = "monospace";
            matchCounter.style.textShadow = "0 0 2px rgba(0, 0, 0, 0.8)";
            matchCounter.textContent = "0 / 0";

            // Previous match button
            const prevBtn = document.createElement("button");
            prevBtn.textContent = "↑ Prev";
            prevBtn.title = "Previous match (Shift+Enter)";
            prevBtn.style.fontSize = "12px";
            prevBtn.style.padding = "4px 8px";
            prevBtn.style.cursor = "pointer";
            prevBtn.style.border = "2px solid #555";
            prevBtn.style.borderRadius = "3px";
            prevBtn.style.backgroundColor = "#333";
            prevBtn.style.color = "#fff";
            prevBtn.style.fontWeight = "bold";

            // Next match button
            const nextBtn = document.createElement("button");
            nextBtn.textContent = "Next ↓";
            nextBtn.title = "Next match (Enter)";
            nextBtn.style.fontSize = "12px";
            nextBtn.style.padding = "4px 8px";
            nextBtn.style.cursor = "pointer";
            nextBtn.style.border = "2px solid #555";
            nextBtn.style.borderRadius = "3px";
            nextBtn.style.backgroundColor = "#333";
            nextBtn.style.color = "#fff";
            nextBtn.style.fontWeight = "bold";

            highlightControls.appendChild(filterInput);
            highlightControls.appendChild(matchCounter);
            highlightControls.appendChild(prevBtn);
            highlightControls.appendChild(nextBtn);
            textareaWrapper.appendChild(highlightControls);

            // ============ FILTER CONTROLS ============
            const filterControls = document.createElement("div");
            filterControls.style.position = "absolute";
            filterControls.style.top = "49px";
            filterControls.style.left = "0";
            filterControls.style.right = "0";
            filterControls.style.display = "none";
            filterControls.style.flexDirection = "row";
            filterControls.style.gap = "5px";
            filterControls.style.alignItems = "center";
            filterControls.style.padding = "8px";
            filterControls.style.backgroundColor = "rgba(0, 0, 0, 0.85)";
            filterControls.style.border = "3px solid #4CAF50";
            filterControls.style.borderRadius = "4px";
            filterControls.style.boxShadow = "0 2px 8px rgba(0, 0, 0, 0.5)";
            filterControls.style.zIndex = "15";
            filterControls.style.backdropFilter = "blur(4px)";
            filterControls.style.height = "32px";

            // Filter input for line filtering
            const lineFilterInput = document.createElement("input");
            lineFilterInput.type = "text";
            lineFilterInput.placeholder = "Filter lines (regex supported)...";
            lineFilterInput.style.width = "200px";
            lineFilterInput.style.minWidth = "200px";
            lineFilterInput.style.maxWidth = "600px";
            lineFilterInput.style.height = "28px";
            lineFilterInput.style.boxSizing = "border-box";
            lineFilterInput.style.fontFamily = "monospace";
            lineFilterInput.style.fontSize = "12px";
            lineFilterInput.style.padding = "4px";
            lineFilterInput.style.border = "2px solid #555";
            lineFilterInput.style.borderRadius = "3px";

            lineFilterInput.addEventListener('input', function() {
                const charWidth = 8;
                const padding = 50;
                const minWidth = 200;
                const maxWidth = 600;
                const calculatedWidth = Math.min(maxWidth, Math.max(minWidth, this.value.length * charWidth + padding));
                this.style.width = calculatedWidth + 'px';
            });

            // Line match counter
            const lineMatchCounter = document.createElement("span");
            lineMatchCounter.style.fontSize = "13px";
            lineMatchCounter.style.fontWeight = "bold";
            lineMatchCounter.style.color = "#4CAF50";
            lineMatchCounter.style.minWidth = "80px";
            lineMatchCounter.style.fontFamily = "monospace";
            lineMatchCounter.style.textShadow = "0 0 2px rgba(0, 0, 0, 0.8)";
            lineMatchCounter.textContent = "0 lines";

            filterControls.appendChild(lineFilterInput);
            filterControls.appendChild(lineMatchCounter);
            textareaWrapper.appendChild(filterControls);

            // Sync scroll between textarea and highlight div
            box.addEventListener('scroll', () => {
                highlightDiv.scrollTop = box.scrollTop;
                highlightDiv.scrollLeft = box.scrollLeft;
            });

            // Store references
            this._tv_box = box;
            this._tv_counter = counter;
            this._tv_filter_input = filterInput;
            this._tv_highlight_div = highlightDiv;
            this._tv_highlight_controls = highlightControls;
            this._tv_match_counter = matchCounter;
            this._tv_match_positions = [];
            this._tv_current_match_index = -1;
            this._tv_auto_resize = false;
            this._tv_original_text = "";
            this._tv_pretty_json_text = "";
            this._tv_line_filter_input = lineFilterInput;
            this._tv_filter_controls = filterControls;
            this._tv_line_match_counter = lineMatchCounter;
            this._tv_text_size_controls = textSizeControls;
            this._tv_delete_controls = deleteConfirmControls;



            // ============ DYNAMIC PADDING MANAGEMENT ============
            this._updateTextPadding = () => {
                if (!this.properties) return;

                // Check visibility of various controls
                const hasTextSize = (this._tv_text_size_controls && this._tv_text_size_controls.style.display === "flex");
                const hasDelete = (this._tv_delete_controls && this._tv_delete_controls.style.display === "flex");
                const hasSearch = this.properties.text_filter;
                const hasFilter = this.properties.line_filter;

                const basePadding = 49;
                const controlsHeight = 32; 

                let totalPadding = basePadding;

                if (hasDelete) {
                    // Delete dialog is taller than normal controls
                    totalPadding += 80; 
                } else if (hasSearch || hasFilter || hasTextSize) {
                    // Standard single-row controls
                    totalPadding += controlsHeight;
                }

                box.style.paddingTop = `${totalPadding}px`;
                if (this._tv_highlight_div) this._tv_highlight_div.style.paddingTop = `${totalPadding}px`;
                
                // Ensure all controls are positioned correctly below the header
                if (this._tv_highlight_controls) this._tv_highlight_controls.style.top = `${basePadding}px`;
                if (this._tv_filter_controls) this._tv_filter_controls.style.top = `${basePadding}px`;
                if (this._tv_text_size_controls) this._tv_text_size_controls.style.top = `${basePadding}px`;
                if (this._tv_delete_controls) this._tv_delete_controls.style.top = `${basePadding}px`;
            };



            // Navigation functions for textarea mode
            const navigateToMatch = (index) => {
                if (this._tv_match_positions.length === 0) return;

                this._tv_current_match_index = index;
                const pos = this._tv_match_positions[index];
                const textBeforeMatch = box.value.substring(0, pos);
                const lineNumber = textBeforeMatch.split('\n').length - 1;
                const lineHeight = parseFloat(getComputedStyle(box).lineHeight);
                const scrollPosition = lineNumber * lineHeight;

                box.scrollTop = scrollPosition - (box.clientHeight / 2);
                highlightDiv.scrollTop = box.scrollTop;
                matchCounter.textContent = `${index + 1} / ${this._tv_match_positions.length}`;

                this._applyFilter(index);
            };

            prevBtn.onclick = () => {
                if (this._tv_match_positions.length === 0) return;
                const newIndex = (this._tv_current_match_index - 1 + this._tv_match_positions.length) % this._tv_match_positions.length;
                navigateToMatch(newIndex);
            };

            nextBtn.onclick = () => {
                if (this._tv_match_positions.length === 0) return;
                const newIndex = (this._tv_current_match_index + 1) % this._tv_match_positions.length;
                navigateToMatch(newIndex);
            };

            filterInput.addEventListener('keydown', (e) => {
                if (e.key === 'Enter') {
                    e.preventDefault();
                    if (e.shiftKey) {
                        prevBtn.click();
                    } else {
                        nextBtn.click();
                    }
                }
            });

            this._tv_navigate_to_match = navigateToMatch;

            // Text Highlight button click handler
            highlightBtn.onclick = () => {
                this.properties.text_filter = !this.properties.text_filter;
                highlightBtn.style.opacity = this.properties.text_filter ? "1" : "0.5";
                highlightControls.style.display = this.properties.text_filter ? "flex" : "none";
                highlightDiv.style.display = this.properties.text_filter ? "block" : "none";

                this._updateTextPadding();

                if (!this.properties.text_filter) {
                    filterInput.value = "";
                    this._applyFilter();
                } else {
                    setTimeout(() => filterInput.focus(), 100);
                }
            };

            // Text Filter button click handler
            filterBtn.onclick = () => {
                this.properties.line_filter = !this.properties.line_filter;
                filterBtn.style.opacity = this.properties.line_filter ? "1" : "0.5";
                filterControls.style.display = this.properties.line_filter ? "flex" : "none";

                this._updateTextPadding();

                if (!this.properties.line_filter) {
                    lineFilterInput.value = "";
                    this._applyLineFilter();
                } else {
                    setTimeout(() => lineFilterInput.focus(), 100);
                }
            };

            // Initialize properties
            if (!this.properties) {
                this.properties = {};
            }

            this.properties.font_size = this.properties.font_size ?? 14;
            this.properties.theme = this.properties.theme ?? "Dark";
            this.properties.word_wrap = this.properties.word_wrap ?? false;
            this.properties.text_filter = this.properties.text_filter ?? false;
            this.properties.line_filter = this.properties.line_filter ?? false;
            this.properties.pretty_json_mode = this.properties.pretty_json_mode ?? false;

            // Add DOM widgets
            this.addDOMWidget("textDisplay", "customtext", textareaWrapper, {
                getValue: () => box.value,
                setValue: (v) => {
                    box.value = v;
                }
            });

            // Filter input handler
            filterInput.oninput = () => {
                this._tv_current_match_index = -1;
                this._applyFilter();
                if (this._tv_match_positions.length > 0) {
                    this._tv_navigate_to_match(0);
                }
            };

            // Line filter input handler
            lineFilterInput.oninput = () => {
                this._applyLineFilter();
            };

            // Helper function to set text
            this._tv_set = (v) => {
                const text = typeof v === "string" ? v : (Array.isArray(v) ? v.join("\n") : "");
                this._tv_original_text = text;
                this.properties.text = text;
                this._tv_pretty_json_text = "";
                this.properties.pretty_json_text = "";
                this.properties.pretty_json_mode = false;
                if (prettyJsonBtn) {
                    prettyJsonBtn.style.opacity = "0.5";
                }

                box.value = text;
                this._applyFilter();
                this._applyLineFilter();
                this._updateCounter();
            };

            // Apply theme
            this._applyTheme = (theme) => {
                const themes = {
                    "Dark": {
                        bg: "#1e1e1e",
                        color: "#d4d4d4",
                        border: "#3e3e3e"
                    },
                    "Light": {
                        bg: "#ffffff",
                        color: "#000000",
                        border: "#cccccc"
                    }
                };

                const t = themes[theme] || themes["Dark"];
                box.style.backgroundColor = t.bg;
                box.style.color = t.color;
                box.style.border = `1px solid ${t.border}`;
                filterInput.style.backgroundColor = t.bg;
                filterInput.style.color = t.color;
                lineFilterInput.style.backgroundColor = t.bg;
                lineFilterInput.style.color = t.color;
            };

            // Apply text highlighting with navigation
            this._applyFilter = (currentMatchIndex = -1) => {
                const filterValue = filterInput.value;

                if (!this.properties.line_filter) {
                    box.value = this.properties.pretty_json_mode ? this._tv_pretty_json_text : this._tv_original_text;
                }

                this._updateCounter();

                if (!filterValue || !this.properties.text_filter) {
                    highlightDiv.innerHTML = '';
                    this._tv_match_positions = [];
                    matchCounter.textContent = "0 / 0";
                    return;
                }

                try {
                    const regex = new RegExp(filterValue, 'gi');
                    const text = box.value;
                    this._tv_match_positions = [];
                    let match;

                    while ((match = regex.exec(text)) !== null) {
                        this._tv_match_positions.push(match.index);
                    }

                    if (currentMatchIndex === -1) {
                        matchCounter.textContent = `0 / ${this._tv_match_positions.length}`;
                    }

                    let matchIndex = 0;
                    const highlightedText = text.replace(new RegExp(filterValue, 'gi'), (match) => {
                        const isCurrentMatch = matchIndex === currentMatchIndex;
                        matchIndex++;
                        if (isCurrentMatch) {
                            return `<mark style="background-color: #ff6b6b; color: #000;">${match}</mark>`;
                        } else {
                            return `<mark style="background-color: #ffeb3b; color: #000;">${match}</mark>`;
                        }
                    });

                    highlightDiv.innerHTML = highlightedText;
                    highlightDiv.style.fontSize = box.style.fontSize;
                    highlightDiv.scrollTop = box.scrollTop;
                    highlightDiv.scrollLeft = box.scrollLeft;
                } catch (e) {
                    console.warn("Invalid regex pattern");
                    highlightDiv.innerHTML = '';
                    this._tv_match_positions = [];
                    matchCounter.textContent = "0 / 0";
                }
            };

            // Apply line filtering
            this._applyLineFilter = () => {
                const filterValue = this._tv_line_filter_input.value;

                if (!filterValue || !this.properties.line_filter) {
                    box.value = this.properties.pretty_json_mode ? this._tv_pretty_json_text : this._tv_original_text;
                    this._tv_line_match_counter.textContent = "0 lines";
                    this._updateCounter();
                    return;
                }

                try {
                    const regex = new RegExp(filterValue, 'i');
                    const sourceText = this.properties.pretty_json_mode ? this._tv_pretty_json_text : this._tv_original_text;
                    const lines = sourceText.split('\n');
                    const matchedLines = lines.filter(line => regex.test(line));

                    box.value = matchedLines.join('\n');
                    this._tv_line_match_counter.textContent = `${matchedLines.length} lines`;
                    this._updateCounter();

                    if (this.properties.text_filter) {
                        this._applyFilter();
                    }
                } catch (e) {
                    console.warn("Invalid regex pattern");
                    box.value = this.properties.pretty_json_mode ? this._tv_pretty_json_text : this._tv_original_text;
                    this._tv_line_match_counter.textContent = "0 lines";
                    this._updateCounter();
                }
            };

            // Update counter
            this._updateCounter = () => {
                const text = box.value;
                const chars = text.length;
                const words = text.trim() ? text.trim().split(/\s+/).length : 0;
                const lines = text ? text.split('\n').length : 0;
                counter.textContent = `${chars} chars | ${words} words | ${lines} lines`;
            };

            // Initial setup - restore saved text if available
            const savedText = this.properties?.text ?? "";
            if (savedText) {
                this._tv_original_text = savedText;
                this._tv_pretty_json_text = this.properties?.pretty_json_text ?? "";
                box.value = this.properties.pretty_json_mode ? this._tv_pretty_json_text : savedText;
                this._updateCounter();
                
                // Restore filter states if they exist
                if (this.properties.text_filter && this._tv_filter_input && this.properties.filter_text) {
                    this._tv_filter_input.value = this.properties.filter_text;
                    this._tv_highlight_controls.style.display = "flex";
                    this._tv_highlight_div.style.display = "block";
                    this._applyFilter();
                }
                
                if (this.properties.line_filter && this._tv_line_filter_input && this.properties.line_filter_text) {
                    this._tv_line_filter_input.value = this.properties.line_filter_text;
                    this._tv_filter_controls.style.display = "flex";
                    this._applyLineFilter();
                }
                
                this._updateTextPadding();
            } else {
                this._tv_set("");
            }
            
            this._applyTheme(this.properties.theme);
            this.size = [500, 200];
        };

        // Calculate content-based size
        nodeType.prototype._calculateContentSize = function() {
            if (!this._tv_box) return null;

            const text = this._tv_box.value;
            if (!text || text.length === 0) return [500, 200];

            const lines = text.split('\n');
            const longestLine = Math.max(...lines.map(l => l.length), 1);
            const charWidth = 8.5;
            const baseLineHeight = 21;
            const headerHeight = 35;
            const widgetHeight = 40;
            const margin = 15;
            const textareaPadding = 10;
            const maxWidth = 2000;
            const maxHeight = 2000;

            let contentWidth = (longestLine * charWidth) + (textareaPadding * 2) + (margin * 2);
            contentWidth = Math.max(400, Math.min(contentWidth, maxWidth));

            const textareaWidth = contentWidth - (margin * 2) - (textareaPadding * 2);
            const charsPerLine = Math.floor(textareaWidth / charWidth);

            let totalVisualLines = 0;
            for (const line of lines) {
                if (line.length === 0) {
                    totalVisualLines += 1;
                } else {
                    totalVisualLines += Math.ceil(line.length / charsPerLine);
                }
            }

            let contentHeight = (totalVisualLines * baseLineHeight) + headerHeight + widgetHeight + margin + (textareaPadding * 2);
            contentHeight = Math.max(300, Math.min(contentHeight, maxHeight));

            return [contentWidth, contentHeight];
        };

        // Sync textarea size
        nodeType.prototype._syncTextareaSize = function() {
            if (!this._tv_box || !this.size) return;

            const nodeWidth = this.size[0];
            const nodeHeight = this.size[1];
            const headerHeight = 30;
            const widgetHeight = 15;
            const leftMargin = 10;
            const rightMargin = 10;
            const bottomMargin = 5;

            const textareaWidth = nodeWidth - leftMargin - rightMargin;
            const textareaHeight = nodeHeight - headerHeight - widgetHeight - bottomMargin;

            this._tv_box.style.width = `${Math.max(50, textareaWidth)}px`;
            this._tv_box.style.height = `${Math.max(40, textareaHeight)}px`;

            if (this._tv_highlight_div) {
                this._tv_highlight_div.style.width = `${Math.max(50, textareaWidth)}px`;
                this._tv_highlight_div.style.height = `${Math.max(40, textareaHeight)}px`;
            }
        };

        // Override onResize
        const origOnResize = nodeType.prototype.onResize;
        nodeType.prototype.onResize = function(size) {
            if (origOnResize) {
                origOnResize.apply(this, arguments);
            }
            this._syncTextareaSize();
        };

        // Serialize node state
        const origOnSerialize = nodeType.prototype.onSerialize;
        nodeType.prototype.onSerialize = function(info) {
            if (origOnSerialize) {
                origOnSerialize.apply(this, arguments);
            }
            
            info.properties = info.properties || {};
            info.properties.text = this._tv_original_text || "";
            info.properties.pretty_json_text = this._tv_pretty_json_text || "";
            info.properties.theme = this.properties.theme;
            info.properties.word_wrap = this.properties.word_wrap;
            info.properties.text_filter = this.properties.text_filter;
            info.properties.line_filter = this.properties.line_filter;
            info.properties.pretty_json_mode = this.properties.pretty_json_mode;
            info.properties.font_size = this.properties.font_size;
            
            // Save filter inputs
            if (this._tv_filter_input) {
                info.properties.filter_text = this._tv_filter_input.value;
            }
            if (this._tv_line_filter_input) {
                info.properties.line_filter_text = this._tv_line_filter_input.value;
            }
        };

        // Deserialize node state
        const origOnConfigure = nodeType.prototype.onConfigure;
        nodeType.prototype.onConfigure = function(info) {
            if (origOnConfigure) {
                origOnConfigure.apply(this, arguments);
            }
            
            if (info.properties) {
                // Restore text content
                if (info.properties.text) {
                    this._tv_original_text = info.properties.text;
                    this._tv_pretty_json_text = info.properties.pretty_json_text || "";
                    
                    if (this._tv_box) {
                        if (info.properties.pretty_json_mode) {
                            this._tv_box.value = this._tv_pretty_json_text;
                        } else {
                            this._tv_box.value = this._tv_original_text;
                        }
                        this._updateCounter();
                    }
                }
                if (info.properties.font_size) {
                    this.properties.font_size = info.properties.font_size;

                    // Apply saved font size
                    if (this._tv_box) this._tv_box.style.fontSize = `${this.properties.font_size}px`;
                    if (this._tv_highlight_div) this._tv_highlight_div.style.fontSize = `${this.properties.font_size}px`;
                    if (this._tv_markdown_div) this._tv_markdown_div.style.fontSize = `${this.properties.font_size}px`;
                }

                // Restore filter states
                if (this._tv_filter_input && info.properties.filter_text) {
                    this._tv_filter_input.value = info.properties.filter_text;
                    this._applyFilter();
                }
                
                if (this._tv_line_filter_input && info.properties.line_filter_text) {
                    this._tv_line_filter_input.value = info.properties.line_filter_text;
                    this._applyLineFilter();
                }
                
                // Restore UI states
                if (this.properties.text_filter && this._tv_highlight_controls) {
                    this._tv_highlight_controls.style.display = "flex";
                    this._tv_highlight_div.style.display = "block";
                }
                
                if (this.properties.line_filter && this._tv_filter_controls) {
                    this._tv_filter_controls.style.display = "flex";
                }
                
                this._updateTextPadding();
            }
        };

        // Override onExecuted
        const origOnExecuted = nodeType.prototype.onExecuted;
        nodeType.prototype.onExecuted = function (msg) {
            try {
                const textData = msg?.text;
                if (textData && Array.isArray(textData) && textData.length > 0) {
                    this._tv_set?.(textData[0]);
                }
            } catch (e) {
                console.error("TextViewer onExecuted error:", e);
            }

            try {
                origOnExecuted?.apply(this, arguments);
            } catch {}
        };
    }
});
