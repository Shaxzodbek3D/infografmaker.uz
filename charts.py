"""
Chartlar Va Infografika Yaratish Moduli
"""

import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib import rcParams
import io
import base64
from datetime import datetime

# O'zbek shrift o'rnatish
rcParams['font.sans-serif'] = ['DejaVu Sans']

class ChartGenerator:
    def __init__(self):
        self.colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A', '#98D8C8', '#F7DC6F', '#BB8FCE', '#85C1E2']
    
    def generate_bar_chart(self, labels, data, title, xlabel='', ylabel=''):
        """Bar chart yaratish"""
        fig, ax = plt.subplots(figsize=(12, 6))
        
        ax.bar(range(len(labels)), data, color=self.colors[:len(labels)])
        ax.set_xticks(range(len(labels)))
        ax.set_xticklabels(labels, rotation=45, ha='right')
        ax.set_title(title, fontsize=16, fontweight='bold', pad=20)
        ax.set_ylabel(ylabel, fontsize=12)
        ax.set_xlabel(xlabel, fontsize=12)
        ax.grid(axis='y', alpha=0.3)
        
        plt.tight_layout()
        
        # Base64 ga konvertish
        img_base64 = self.fig_to_base64(fig)
        plt.close(fig)
        return img_base64
    
    def generate_pie_chart(self, labels, data, title):
        """Pie chart yaratish"""
        fig, ax = plt.subplots(figsize=(10, 8))
        
        ax.pie(data, labels=labels, autopct='%1.1f%%', colors=self.colors[:len(labels)], startangle=90)
        ax.set_title(title, fontsize=16, fontweight='bold', pad=20)
        
        plt.tight_layout()
        
        img_base64 = self.fig_to_base64(fig)
        plt.close(fig)
        return img_base64
    
    def generate_line_chart(self, labels, data, title):
        """Line chart yaratish"""
        fig, ax = plt.subplots(figsize=(14, 6))
        
        ax.plot(range(len(labels)), data, marker='o', linewidth=2, markersize=6, color='#4ECDC4')
        ax.fill_between(range(len(labels)), data, alpha=0.3, color='#4ECDC4')
        ax.set_xticks(range(0, len(labels), max(1, len(labels)//10)))
        ax.set_xticklabels([labels[i] for i in range(0, len(labels), max(1, len(labels)//10))], rotation=45, ha='right')
        ax.set_title(title, fontsize=16, fontweight='bold', pad=20)
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        img_base64 = self.fig_to_base64(fig)
        plt.close(fig)
        return img_base64
    
    def fig_to_base64(self, fig):
        """Matplotlib figure'ni base64 ga konvertish"""
        img = io.BytesIO()
        fig.savefig(img, format='png', bbox_inches='tight', dpi=100)
        img.seek(0)
        return 'data:image/png;base64,' + base64.b64encode(img.getvalue()).decode()
    
    def generate_stats_card(self, value, label, icon=''):
        """Statistika kartasi HTML"""
        return f"""
        <div class="stat-card">
            <div class="stat-icon">{icon}</div>
            <div class="stat-content">
                <div class="stat-value">{value}</div>
                <div class="stat-label">{label}</div>
            </div>
        </div>
        """
