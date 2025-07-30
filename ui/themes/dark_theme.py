class DarkTheme:
    def __init__(self):
        self.name = "dark"
        self.colors = {
            "background": "#1a1a1a",
            "surface": "#2d2d2d",
            "primary": "#4a9eff",
            "secondary": "#6c757d",
            "success": "#28a745",
            "warning": "#ffc107",
            "error": "#dc3545",
            "info": "#17a2b8",
            "text": "#ffffff",
            "text-secondary": "#b0b0b0",
            "border": "#404040",
            "shadow": "rgba(0, 0, 0, 0.3)",
            "hover": "#404040",
            "active": "#4a9eff",
            "disabled": "#666666"
        }
    
    def get_css(self):
        """Get the CSS content for the dark theme."""
        return f"""
        /* Dark Theme Styles */
        
        /* Global Styles */
        window {{
            background-color: {self.colors['background']};
            color: {self.colors['text']};
        }}
        
        /* Resource Cards */
        .resource-card {{
            background-color: {self.colors['surface']};
            border: 1px solid {self.colors['border']};
            border-radius: 8px;
            box-shadow: 0 2px 4px {self.colors['shadow']};
            transition: all 0.2s ease;
        }}
        
        .resource-card:hover {{
            box-shadow: 0 4px 8px {self.colors['shadow']};
            transform: translateY(-1px);
            background-color: {self.colors['hover']};
        }}
        
        .resource-card.selected {{
            border-color: {self.colors['primary']};
            box-shadow: 0 0 0 2px {self.colors['primary']}40;
        }}
        
        .card-title {{
            font-weight: 600;
            color: {self.colors['text']};
            font-size: 14px;
        }}
        
        .card-content {{
            color: {self.colors['text-secondary']};
            font-size: 12px;
        }}
        
        .card-detail {{
            color: {self.colors['text-secondary']};
            font-size: 11px;
        }}
        
        .card-footer {{
            border-top: 1px solid {self.colors['border']};
            padding-top: 8px;
        }}
        
        /* Status Cards */
        .status-card {{
            background-color: {self.colors['surface']};
            border: 1px solid {self.colors['border']};
            border-radius: 8px;
            padding: 16px;
            box-shadow: 0 2px 4px {self.colors['shadow']};
        }}
        
        .status-card-title {{
            font-weight: 600;
            color: {self.colors['text']};
            font-size: 14px;
        }}
        
        .status-card-value {{
            font-size: 24px;
            font-weight: 700;
            color: {self.colors['primary']};
        }}
        
        /* Status Indicators */
        .status-running {{
            color: {self.colors['success']};
            font-weight: 600;
            font-size: 11px;
            background-color: {self.colors['success']}20;
            padding: 2px 6px;
            border-radius: 4px;
        }}
        
        .status-stopped {{
            color: {self.colors['warning']};
            font-weight: 600;
            font-size: 11px;
            background-color: {self.colors['warning']}20;
            padding: 2px 6px;
            border-radius: 4px;
        }}
        
        .status-exited {{
            color: {self.colors['error']};
            font-weight: 600;
            font-size: 11px;
            background-color: {self.colors['error']}20;
            padding: 2px 6px;
            border-radius: 4px;
        }}
        
        .status-unknown {{
            color: {self.colors['secondary']};
            font-weight: 600;
            font-size: 11px;
            background-color: {self.colors['secondary']}20;
            padding: 2px 6px;
            border-radius: 4px;
        }}
        
        /* Status Bar */
        .status-bar {{
            background-color: {self.colors['surface']};
            border-top: 1px solid {self.colors['border']};
            padding: 8px 16px;
        }}
        
        .status-indicator {{
            padding: 4px 8px;
            border-radius: 4px;
            background-color: {self.colors['surface']};
        }}
        
        .status-indicator.connected {{
            background-color: {self.colors['success']}20;
            color: {self.colors['success']};
        }}
        
        .status-indicator.disconnected {{
            background-color: {self.colors['error']}20;
            color: {self.colors['error']};
        }}
        
        .status-text {{
            font-size: 12px;
            font-weight: 500;
        }}
        
        .status-message {{
            font-size: 12px;
            color: {self.colors['text-secondary']};
        }}
        
        .status-progress {{
            min-width: 200px;
        }}
        
        /* Search Bar */
        .search-bar {{
            background-color: {self.colors['surface']};
            border: 1px solid {self.colors['border']};
            border-radius: 6px;
            padding: 8px 12px;
        }}
        
        .search-entry {{
            border: none;
            background: transparent;
            font-size: 14px;
            color: {self.colors['text']};
        }}
        
        .search-clear {{
            background: transparent;
            border: none;
            color: {self.colors['text-secondary']};
        }}
        
        .search-clear:hover {{
            color: {self.colors['text']};
        }}
        
        /* Filter Bar */
        .filter-bar {{
            background-color: {self.colors['surface']};
            border-bottom: 1px solid {self.colors['border']};
            padding: 8px 16px;
        }}
        
        .filter-label {{
            font-weight: 600;
            color: {self.colors['text']};
            font-size: 12px;
        }}
        
        .filter-chip {{
            background-color: {self.colors['primary']}20;
            border: 1px solid {self.colors['primary']}40;
            border-radius: 16px;
            padding: 4px 8px;
        }}
        
        .filter-chip-label {{
            font-size: 11px;
            color: {self.colors['primary']};
            font-weight: 500;
        }}
        
        .filter-chip-remove {{
            background: transparent;
            border: none;
            color: {self.colors['primary']};
            padding: 0;
            min-width: 16px;
            min-height: 16px;
        }}
        
        .filter-clear {{
            background: transparent;
            border: 1px solid {self.colors['border']};
            border-radius: 4px;
            padding: 4px 8px;
            font-size: 11px;
            color: {self.colors['text-secondary']};
        }}
        
        .filter-clear:hover {{
            background-color: {self.colors['hover']};
        }}
        
        /* Dashboard */
        .dashboard {{
            background-color: {self.colors['background']};
        }}
        
        .dashboard-header {{
            border-bottom: 1px solid {self.colors['border']};
            padding-bottom: 16px;
        }}
        
        .dashboard-title {{
            font-size: 24px;
            font-weight: 700;
            color: {self.colors['text']};
        }}
        
        .dashboard-refresh {{
            background: transparent;
            border: 1px solid {self.colors['border']};
            border-radius: 6px;
            padding: 8px;
        }}
        
        .dashboard-refresh:hover {{
            background-color: {self.colors['hover']};
        }}
        
        .dashboard-stats {{
            margin: 16px 0;
        }}
        
        .dashboard-actions {{
            border-top: 1px solid {self.colors['border']};
            padding-top: 16px;
        }}
        
        .section-title {{
            font-size: 16px;
            font-weight: 600;
            color: {self.colors['text']};
        }}
        
        .action-button {{
            border: 1px solid {self.colors['border']};
            border-radius: 6px;
            padding: 8px 12px;
            font-size: 12px;
            font-weight: 500;
            transition: all 0.2s ease;
            background-color: {self.colors['surface']};
            color: {self.colors['text']};
        }}
        
        .action-button:hover {{
            transform: translateY(-1px);
            box-shadow: 0 2px 4px {self.colors['shadow']};
            background-color: {self.colors['hover']};
        }}
        
        .action-button.success-action {{
            background-color: {self.colors['success']}20;
            border-color: {self.colors['success']}40;
            color: {self.colors['success']};
        }}
        
        .action-button.warning-action {{
            background-color: {self.colors['warning']}20;
            border-color: {self.colors['warning']}40;
            color: {self.colors['warning']};
        }}
        
        .action-button.destructive-action {{
            background-color: {self.colors['error']}20;
            border-color: {self.colors['error']}40;
            color: {self.colors['error']};
        }}
        
        /* Notifications */
        .notification-area {{
            /* pointer-events не поддерживается в GTK4 */
        }}
        
        .notification-toast {{
            background-color: {self.colors['surface']};
            border: 1px solid {self.colors['border']};
            border-radius: 8px;
            box-shadow: 0 4px 12px {self.colors['shadow']};
            margin-bottom: 8px;
        }}
        
        .notification-info {{
            border-left: 4px solid {self.colors['info']};
        }}
        
        .notification-success {{
            border-left: 4px solid {self.colors['success']};
        }}
        
        .notification-warning {{
            border-left: 4px solid {self.colors['warning']};
        }}
        
        .notification-error {{
            border-left: 4px solid {self.colors['error']};
        }}
        
        .toast-content {{
            padding: 12px 16px;
        }}
        
        .toast-icon {{
            color: {self.colors['text-secondary']};
        }}
        
        .toast-message {{
            color: {self.colors['text']};
            font-size: 14px;
        }}
        
        .toast-close {{
            background: transparent;
            border: none;
            color: {self.colors['text-secondary']};
            padding: 4px;
        }}
        
        .toast-close:hover {{
            color: {self.colors['text']};
        }}
        
        /* Buttons */
        button {{
            border-radius: 6px;
            font-weight: 500;
            transition: all 0.2s ease;
            background-color: {self.colors['surface']};
            color: {self.colors['text']};
            border: 1px solid {self.colors['border']};
        }}
        
        button:hover {{
            transform: translateY(-1px);
            background-color: {self.colors['hover']};
        }}
        
        button:active {{
            transform: translateY(0);
        }}
        
        /* Scrollbars */
        scrollbar {{
            background-color: {self.colors['surface']};
        }}
        
        scrollbar slider {{
            background-color: {self.colors['border']};
            border-radius: 4px;
            min-width: 8px;
            min-height: 8px;
        }}
        
        scrollbar slider:hover {{
            background-color: {self.colors['text-secondary']};
        }}
        
        /* Notebook tabs */
        notebook tab {{
            background-color: {self.colors['surface']};
            border: 1px solid {self.colors['border']};
            border-bottom: none;
            border-radius: 6px 6px 0 0;
            padding: 8px 16px;
            margin-right: 2px;
            color: {self.colors['text']};
        }}
        
        notebook tab:checked {{
            background-color: {self.colors['background']};
            border-bottom: 2px solid {self.colors['primary']};
        }}
        
        notebook tab:hover {{
            background-color: {self.colors['hover']};
        }}
        
        /* TreeView */
        treeview {{
            background-color: {self.colors['background']};
            color: {self.colors['text']};
        }}
        
        treeview:selected {{
            background-color: {self.colors['primary']}20;
            color: {self.colors['primary']};
        }}
        
        /* Entry */
        entry {{
            border: 1px solid {self.colors['border']};
            border-radius: 6px;
            padding: 8px 12px;
            background-color: {self.colors['surface']};
            color: {self.colors['text']};
        }}
        
        entry:focus {{
            border-color: {self.colors['primary']};
            box-shadow: 0 0 0 2px {self.colors['primary']}20;
        }}
        
        /* Progress bar */
        progressbar {{
            background-color: {self.colors['surface']};
            border: 1px solid {self.colors['border']};
            border-radius: 4px;
        }}
        
        progressbar progress {{
            background-color: {self.colors['primary']};
            border-radius: 3px;
        }}
        
        /* Separator */
        separator {{
            background-color: {self.colors['border']};
        }}
        
        /* Label */
        label {{
            color: {self.colors['text']};
        }}
        
        /* Box */
        box {{
            background-color: transparent;
        }}
        
        /* Grid */
        grid {{
            background-color: transparent;
        }}
        """
    
    def get_colors(self):
        """Get the color palette for this theme."""
        return self.colors.copy()
