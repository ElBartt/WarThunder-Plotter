/**
 * WT Plotter - Match visualization
 * Canvas-based rendering of positions with filtering and live updates.
 */

class MatchViewer {
    constructor(canvasId, matchId, options = {}) {
        this.canvas = document.getElementById(canvasId);
        this.ctx = this.canvas.getContext('2d');
        this.matchId = matchId;
        this.isLive = options.isLive || false;
        this.pollInterval = options.pollInterval || 500; // 0.5s default
        
        // State
        this.positions = [];
        this.pois = [];
        this.mapImage = null;
        this.lastTimestamp = 0;
        this.pollTimer = null;
        
        // Live status (updated during polling)
        this.liveArmyType = 'tank';
        this.liveVehicleType = '';
        
        // Zoom and pan state
        this.zoom = 1.0;
        this.minZoom = 0.5;
        this.maxZoom = 5.0;
        this.panX = 0;
        this.panY = 0;
        this.isPanning = false;
        this.lastMouseX = 0;
        this.lastMouseY = 0;
        
        // Filters (all enabled by default) - based on War Thunder team colors
        this.filters = {
            player: true,      // Yellow - your vehicle
            squad: true,       // Green - squadmates  
            ally: true,        // Blue - allied team
            enemy: true,       // Red - enemy team
            capture_zone: true,
            respawn: true,
            other: true
        };
        
        // Blip (marker) size
        this.blipSize = 1.5;  // Default size, range 1-6
        
        // Timeline state (for replay mode)
        this.timelinePosition = 1.0;  // Current time position (0-1, 1 = show all)
        this.maxTimestamp = 0;        // Max timestamp in data (ms)
        
        // Initialize
        this._loadMap();
        this._loadPositions();
        this._setupInteractions();
        
        // Start polling if live
        if (this.isLive) {
            this._startPolling();
        }
        
        // Handle resize
        window.addEventListener('resize', () => this._resize());
        
        // Delay initial resize to ensure container is laid out
        requestAnimationFrame(() => {
            this._resize();
            this._render();
        });
    }
    
    _resize() {
        const container = this.canvas.parentElement;
        // Larger default size, max 1500px
        const size = Math.min(container.clientWidth, container.clientHeight, 1500);
        this.canvas.width = size;
        this.canvas.height = size;
        this._render();
    }
    
    _setupInteractions() {
        // Mouse wheel zoom
        this.canvas.addEventListener('wheel', (e) => {
            e.preventDefault();
            const rect = this.canvas.getBoundingClientRect();
            const mouseX = e.clientX - rect.left;
            const mouseY = e.clientY - rect.top;
            
            // Zoom towards mouse position
            const zoomFactor = e.deltaY > 0 ? 0.9 : 1.1;
            const newZoom = Math.max(this.minZoom, Math.min(this.maxZoom, this.zoom * zoomFactor));
            
            if (newZoom !== this.zoom) {
                // Adjust pan to zoom towards mouse
                const zoomRatio = newZoom / this.zoom;
                this.panX = mouseX - (mouseX - this.panX) * zoomRatio;
                this.panY = mouseY - (mouseY - this.panY) * zoomRatio;
                this.zoom = newZoom;
                this._clampPan();
                this._render();
                this._updateZoomDisplay();
            }
        });
        
        // Pan with mouse drag
        this.canvas.addEventListener('mousedown', (e) => {
            if (e.button === 0) { // Left click
                this.isPanning = true;
                this.lastMouseX = e.clientX;
                this.lastMouseY = e.clientY;
                this.canvas.style.cursor = 'grabbing';
            }
        });
        
        window.addEventListener('mousemove', (e) => {
            if (this.isPanning) {
                const dx = e.clientX - this.lastMouseX;
                const dy = e.clientY - this.lastMouseY;
                this.panX += dx;
                this.panY += dy;
                this.lastMouseX = e.clientX;
                this.lastMouseY = e.clientY;
                this._clampPan();
                this._render();
            }
        });
        
        window.addEventListener('mouseup', () => {
            if (this.isPanning) {
                this.isPanning = false;
                this.canvas.style.cursor = 'grab';
            }
        });
        
        // Set initial cursor
        this.canvas.style.cursor = 'grab';
        
        // Double-click to reset view
        this.canvas.addEventListener('dblclick', () => {
            this.resetView();
        });
    }
    
    _clampPan() {
        const w = this.canvas.width;
        const h = this.canvas.height;
        const scaledW = w * this.zoom;
        const scaledH = h * this.zoom;
        
        // Allow panning but keep at least some of the map visible
        const margin = 50;
        this.panX = Math.max(-(scaledW - margin), Math.min(w - margin, this.panX));
        this.panY = Math.max(-(scaledH - margin), Math.min(h - margin, this.panY));
    }
    
    _updateZoomDisplay() {
        const zoomEl = document.getElementById('zoom-level');
        if (zoomEl) {
            zoomEl.textContent = `${Math.round(this.zoom * 100)}%`;
        }
    }
    
    resetView() {
        this.zoom = 1.0;
        this.panX = 0;
        this.panY = 0;
        this._render();
        this._updateZoomDisplay();
    }
    
    zoomIn() {
        const newZoom = Math.min(this.maxZoom, this.zoom * 1.25);
        if (newZoom !== this.zoom) {
            // Zoom towards center
            const cx = this.canvas.width / 2;
            const cy = this.canvas.height / 2;
            const zoomRatio = newZoom / this.zoom;
            this.panX = cx - (cx - this.panX) * zoomRatio;
            this.panY = cy - (cy - this.panY) * zoomRatio;
            this.zoom = newZoom;
            this._clampPan();
            this._render();
            this._updateZoomDisplay();
        }
    }
    
    zoomOut() {
        const newZoom = Math.max(this.minZoom, this.zoom / 1.25);
        if (newZoom !== this.zoom) {
            const cx = this.canvas.width / 2;
            const cy = this.canvas.height / 2;
            const zoomRatio = newZoom / this.zoom;
            this.panX = cx - (cx - this.panX) * zoomRatio;
            this.panY = cy - (cy - this.panY) * zoomRatio;
            this.zoom = newZoom;
            this._clampPan();
            this._render();
            this._updateZoomDisplay();
        }
    }
    
    async _loadMap() {
        const img = new Image();
        img.onload = () => {
            this.mapImage = img;
            this._render();
        };
        img.onerror = () => {
            console.warn('Failed to load map image');
            this._render();
        };
        img.src = `/api/match/${this.matchId}/map.png`;
    }
    
    async _loadPositions() {
        try {
            const resp = await fetch(`/api/match/${this.matchId}/positions?since=${this.lastTimestamp}`);
            const positions = await resp.json();
            
            if (positions.length > 0) {
                // Process positions: use ground coordinates when available
                const processed = positions.map(pos => {
                    // Use ground coordinates when available (for air-view positions)
                    if (pos.x_ground !== null && pos.x_ground !== undefined &&
                        pos.y_ground !== null && pos.y_ground !== undefined) {
                        return {
                            ...pos,
                            x: pos.x_ground,
                            y: pos.y_ground,
                            x_original: pos.x,
                            y_original: pos.y
                        };
                    }
                    return pos;
                });

                // Separate POIs from regular positions (store all for stats, filter aircraft for display)
                for (const pos of processed) {
                    if (pos.is_poi) {
                        this.pois.push(pos);
                    } else {
                        this.positions.push(pos);
                    }
                }

                // Update last timestamp
                const maxTs = Math.max(...processed.map(p => p.timestamp));
                if (maxTs > this.lastTimestamp) {
                    this.lastTimestamp = maxTs + 1; // Small offset to avoid duplicates (ms)
                }

                // Update max timestamp for timeline
                if (maxTs > this.maxTimestamp) {
                    this.maxTimestamp = maxTs;
                    this._updateTimelineMax();
                }

                this._render();
            }
            this._updateStats();
        } catch (e) {
            console.error('Failed to load positions:', e);
            this._updateStats();
        }
    }
    
    _startPolling() {
        this.pollTimer = setInterval(() => {
            this._checkMatchStatus();
            this._loadPositions();
        }, this.pollInterval);
    }
    
    _stopPolling() {
        if (this.pollTimer) {
            clearInterval(this.pollTimer);
            this.pollTimer = null;
        }
    }
    
    async _checkMatchStatus() {
        try {
            const resp = await fetch(`/api/match/${this.matchId}`);
            const match = await resp.json();
            if (match.ended_at) {
                // Match ended - check if there's a new active match
                const activeResp = await fetch('/api/active');
                const active = await activeResp.json();
                if (active && active.id && active.id !== this.matchId) {
                    // New match started, redirect to live view
                    window.location.href = '/live';
                } else {
                    // No new match, show ended
                    this._stopPolling();
                    this._showMatchEnded();
                }
            }
            
            // Also fetch live status for army_type display
            const statusResp = await fetch('/api/status');
            const status = await statusResp.json();
            this.liveArmyType = status.army_type || 'tank';
            this.liveVehicleType = status.vehicle_type || '';
            this._updateStats();
        } catch (e) {
            console.error('Failed to check match status:', e);
        }
    }
    
    _showMatchEnded() {
        const badge = document.getElementById('live-badge');
        if (badge) {
            badge.textContent = 'ENDED';
            badge.classList.remove('live');
            badge.classList.add('ended');
        }
    }
    
    _updateStats() {
        const statsEl = document.getElementById('stats');
        if (statsEl) {
            const total = this.positions.length;
            const poiCount = new Set(this.pois.map(p => `${p.x.toFixed(3)},${p.y.toFixed(3)}`)).size;
            
            // Determine current army type and vehicle
            let armyType = 'tank';
            let vehicleType = '';
            
            console.debug(`Updating stats. isLive: ${this.isLive}, timelinePosition: ${this.timelinePosition}, positions count: ${this.positions.length}`);
            if (this.isLive) {
                // Live mode: use live status from API
                console.debug(`Live army type: ${this.liveArmyType}, vehicle type: ${this.liveVehicleType}`);
                armyType = this.liveArmyType || 'tank';
                vehicleType = this.liveVehicleType || '';
            } else if (this.positions.length > 0) {
                if (this.timelinePosition >= 1.0) {
                    // Showing all: use latest position
                    armyType = this.positions[this.positions.length - 1].army_type || 'tank';
                    vehicleType = this.positions[this.positions.length - 1].vehicle_type || '';
                } else {
                    // Timeline mode: find army_type and vehicle at current time
                    const cutoffTime = this.maxTimestamp * this.timelinePosition;
                    for (let i = this.positions.length - 1; i >= 0; i--) {
                        if (this.positions[i].timestamp <= cutoffTime) {
                            armyType = this.positions[i].army_type || 'tank';
                            vehicleType = this.positions[i].vehicle_type || '';
                            break;
                        }
                    }
                }
            }
            
            // Format vehicle name - extract from path like "tankModels/fr_leclerc_s1" -> "fr_leclerc_s1"
            let vehicleName = '';
            if (vehicleType) {
                const parts = vehicleType.split('/');
                vehicleName = parts[parts.length - 1].replace(/_/g, ' ');
            }
            
            let html = `${total} positions, ${poiCount} POIs<br>`;
            
            // Show status about air mode
            if (armyType === 'air') {
                html += `<span class="army-status air-info">✈️ Air View (mapped to ground)</span>`;
            } else {
                html += `<span class="army-status">🚗 Ground</span>`;
            }
            
            if (vehicleName) {
                html += `<br><span class="vehicle-name">${vehicleName}</span>`;
            }
            statsEl.innerHTML = html;
        }
    }
    
    _updateTimelineMax() {
        // Called when maxTimestamp changes - allows external UI to update
        // The match.html template hooks into this via _render override
    }
    
    _categorize(pos) {
        const type = pos.type.toLowerCase();
        const icon = (pos.icon || '').toLowerCase();
        const color = (pos.color || '#FFFFFF').toUpperCase();
        
        // POI types first
        if (type === 'capture_zone') return 'capture_zone';
        if (type.includes('respawn') || type.includes('airfield')) return 'respawn';
        
        // Parse color to RGB for better matching
        const rgb = this._parseColor(color);
        if (rgb) {
            const [r, g, b] = rgb;
            
            // Player (you) - yellow/gold (#FAC81E or similar)
            // High red, high green, low blue
            if (r > 200 && g > 150 && b < 100) {
                return 'player';
            }
            
            // Squad - green (#67D756 or similar)
            // Medium-high green, lower red and blue
            if (g > 180 && r < 150 && b < 150) {
                return 'squad';
            }
            
            // Enemy - red (#FA0C00 or similar)
            // High red, low green, low blue
            if (r > 200 && g < 100 && b < 100) {
                return 'enemy';
            }
            
            // Ally - blue (#174DFF or similar)
            // High blue, lower red and green
            if (b > 200 && r < 100) {
                return 'ally';
            }
        }
        
        // Fallback: check icon for player marker
        if (icon === 'player') {
            return 'player';
        }
        
        return 'other';
    }
    
    _parseColor(hex) {
        // Parse hex color to RGB array
        if (!hex) return null;
        hex = hex.replace('#', '');
        if (hex.length === 3) {
            hex = hex.split('').map(c => c + c).join('');
        }
        if (hex.length !== 6) return null;
        
        const r = parseInt(hex.slice(0, 2), 16);
        const g = parseInt(hex.slice(2, 4), 16);
        const b = parseInt(hex.slice(4, 6), 16);
        
        if (isNaN(r) || isNaN(g) || isNaN(b)) return null;
        return [r, g, b];
    }
    
    _shouldShow(pos) {
        // Don't display aircraft type positions on the map
        const isAirType = (pos.type || '').toLowerCase() === 'aircraft';
        if (isAirType) return false;
        
        // Don't display air-view positions without ground coordinates
        const isAirView = pos.is_player_air_view || pos.is_player_air;
        if (isAirView && (pos.x_ground === null || pos.x_ground === undefined)) {
            return false;
        }
        
        const cat = this._categorize(pos);
        if (this.filters[cat] === false) return false;
        
        // Timeline filter (only for non-live, non-POI)
        if (!this.isLive && !pos.is_poi && this.timelinePosition < 1.0) {
            const cutoffTime = this.maxTimestamp * this.timelinePosition;
            if (pos.timestamp > cutoffTime) return false;
        }
        
        return true;
    }
    
    _getCurrentPois() {
        if (this.isLive || this.timelinePosition >= 1.0) {
            // For live or showing all, group by position and take latest
            const poiMap = new Map();
            for (const pos of this.pois) {
                const key = `${pos.x.toFixed(3)},${pos.y.toFixed(3)}`;
                if (!poiMap.has(key) || pos.timestamp > poiMap.get(key).timestamp) {
                    poiMap.set(key, pos);
                }
            }
            return Array.from(poiMap.values());
        } else {
            // Timeline mode: find POIs at or before cutoff time
            const cutoffTime = this.maxTimestamp * this.timelinePosition;
            const poiMap = new Map();
            for (const pos of this.pois) {
                if (pos.timestamp <= cutoffTime) {
                    const key = `${pos.x.toFixed(3)},${pos.y.toFixed(3)}`;
                    if (!poiMap.has(key) || pos.timestamp > poiMap.get(key).timestamp) {
                        poiMap.set(key, pos);
                    }
                }
            }
            return Array.from(poiMap.values());
        }
    }
    
    _render() {
        const ctx = this.ctx;
        const w = this.canvas.width;
        const h = this.canvas.height;
        
        // Clear
        ctx.fillStyle = '#1a1a1a';
        ctx.fillRect(0, 0, w, h);
        
        // Save context and apply zoom/pan transform
        ctx.save();
        ctx.translate(this.panX, this.panY);
        ctx.scale(this.zoom, this.zoom);
        
        // Draw map
        if (this.mapImage) {
            ctx.drawImage(this.mapImage, 0, 0, w, h);
        } else {
            // Grid fallback
            ctx.strokeStyle = '#333';
            ctx.lineWidth = 1 / this.zoom; // Keep line width consistent
            for (let i = 0; i <= 10; i++) {
                const p = (i / 10) * w;
                ctx.beginPath();
                ctx.moveTo(p, 0);
                ctx.lineTo(p, h);
                ctx.stroke();
                ctx.beginPath();
                ctx.moveTo(0, p);
                ctx.lineTo(w, p);
                ctx.stroke();
            }
        }
        
        // Draw POIs first (capture zones, respawns)
        const currentPois = this._getCurrentPois();
        for (const pos of currentPois) {
            if (this._shouldShow(pos)) {
                this._drawPOI(pos, w, h);
            }
        }
        
        // Draw positions
        for (const pos of this.positions) {
            if (this._shouldShow(pos)) {
                this._drawPosition(pos, w, h);
            }
        }
        
        // Restore context
        ctx.restore();
    }
    
    _drawPOI(pos, w, h) {
        const ctx = this.ctx;
        const x = pos.x * w;
        const y = pos.y * h;
        const type = pos.type.toLowerCase();
        
        if (type === 'capture_zone') {
            // Large semi-transparent circle
            ctx.beginPath();
            ctx.arc(x, y, 20, 0, Math.PI * 2);
            ctx.fillStyle = this._hexToRgba(pos.color, 0.3);
            ctx.fill();
            ctx.strokeStyle = pos.color;
            ctx.lineWidth = 2;
            ctx.stroke();
        } else {
            // Respawn - triangle
            ctx.beginPath();
            ctx.moveTo(x, y - 3);
            ctx.lineTo(x - 2, y + 1);
            ctx.lineTo(x + 2, y + 1);
            ctx.closePath();
            ctx.fillStyle = this._hexToRgba(pos.color, 0.3);
            ctx.fill();
            ctx.strokeStyle = pos.color;
            ctx.lineWidth = 1;
            ctx.stroke();
        }
    }
    
    _drawPosition(pos, w, h) {
        const ctx = this.ctx;
        const x = pos.x * w;
        const y = pos.y * h;
        
        // Size from blipSize setting
        let size = this.blipSize;
        let alpha = 1.0;
        
        // Draw dot
        ctx.beginPath();
        ctx.arc(x, y, size, 0, Math.PI * 2);
        ctx.fillStyle = this._hexToRgba(pos.color, alpha);
        ctx.fill();
    }
    
    _hexToRgba(hex, alpha) {
        // Handle various color formats
        if (!hex || hex === '#FFFFFF' || hex === '#ffffff') {
            return `rgba(255, 255, 255, ${alpha})`;
        }
        
        // Named colors
        const colors = {
            'blue': '#4444ff',
            'red': '#ff4444',
            'green': '#44ff44',
            'yellow': '#ffff44',
            'white': '#ffffff',
            'gray': '#888888'
        };
        if (colors[hex.toLowerCase()]) {
            hex = colors[hex.toLowerCase()];
        }
        
        // Parse hex
        if (hex.startsWith('#')) {
            hex = hex.slice(1);
        }
        if (hex.length === 3) {
            hex = hex.split('').map(c => c + c).join('');
        }
        
        const r = parseInt(hex.slice(0, 2), 16);
        const g = parseInt(hex.slice(2, 4), 16);
        const b = parseInt(hex.slice(4, 6), 16);
        
        // Handle NaN (invalid hex) - default to white
        return `rgba(${isNaN(r) ? 255 : r}, ${isNaN(g) ? 255 : g}, ${isNaN(b) ? 255 : b}, ${alpha})`;
    }
    
    setFilter(category, enabled) {
        this.filters[category] = enabled;
        this._render();
    }
    
    setBlipSize(size) {
        // size is expected to be between 0.5 and 3
        this.blipSize = Math.max(0.5, Math.min(3, size));
        this._render();
    }
    
    setTimeline(position) {
        // position is 0-1 where 1 = show all
        this.timelinePosition = Math.max(0, Math.min(1, position));
        this._render();
        this._updateStats();
    }
    
    getTimelineMax() {
        return this.maxTimestamp;
    }
    
    formatTime(seconds) {
        const totalSeconds = Math.floor(seconds / 1000);
        const mins = Math.floor(totalSeconds / 60);
        const secs = Math.floor(totalSeconds % 60);
        return `${mins}:${secs.toString().padStart(2, '0')}`;
    }
    
    destroy() {
        this._stopPolling();
    }
}

// Export for use
window.MatchViewer = MatchViewer;
