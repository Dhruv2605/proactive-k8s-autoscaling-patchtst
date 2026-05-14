import matplotlib.pyplot as plt
import matplotlib.patches as patches

def draw_architecture():
    fig, ax = plt.subplots(figsize=(10, 7), dpi=300)
    ax.set_xlim(-1.5, 3.5)
    ax.set_ylim(-1, 3)
    ax.axis('off')
    
    # Node definitions: (x, y, label, color)
    nodes = {
        'Locust': (0, 1, "Locust\n(Traffic Gen)", "#ffebee"),       # Red
        'GKE': (2, 1, "GKE Cluster\n(Microservices)", "#e8f5e9"),  # Green
        'Prometheus': (2, 0, "Prometheus\n(Metric Scraper)", "#e3f2fd"), # Blue
        'PatchTST': (0, 0, "PatchTST\n(Predictive AI)", "#fff3e0"), # Orange
        'K8s': (1, 2, "Kubernetes API\n(Autoscaler)", "#f3e5f5")   # Purple
    }
    
    box_width = 1.0
    box_height = 0.6
    
    # Draw nodes
    for key, (x, y, text, color) in nodes.items():
        # Draw box
        box = patches.FancyBboxPatch(
            (x - box_width/2, y - box_height/2), box_width, box_height,
            boxstyle="round,pad=0.1,rounding_size=0.1",
            ec="gray", fc=color, lw=1.5, zorder=3
        )
        ax.add_patch(box)
        # Add text
        ax.text(x, y, text, ha='center', va='center', fontsize=10, 
                fontweight='bold', color='#333333', zorder=4, family='sans-serif')
                
    # Define arrows: (start_node, end_node, label, connection_style, text_offset_x, text_offset_y)
    edges = [
        ('Locust', 'GKE', "Load", "arc3,rad=0", 0, 0.1),
        ('GKE', 'Prometheus', "Metrics (2s)", "arc3,rad=0", 0.3, 0),
        ('Prometheus', 'PatchTST', "Query API", "arc3,rad=0", 0, -0.1),
        ('PatchTST', 'K8s', "Scale Cmd", "arc3,rad=0.2", -0.3, 0.1),
        ('K8s', 'GKE', "Provision Pods", "arc3,rad=0.2", 0.4, 0.1)
    ]
    
    # Draw arrows
    for start, end, label, style, tx, ty in edges:
        x1, y1, _, _ = nodes[start]
        x2, y2, _, _ = nodes[end]
        
        arrow = patches.FancyArrowPatch(
            (x1, y1), (x2, y2),
            connectionstyle=style,
            arrowstyle='-|>',
            mutation_scale=15,
            color='#666666',
            lw=2,
            zorder=2,
            shrinkA=35,
            shrinkB=35
        )
        ax.add_patch(arrow)
        
        # Determine text position
        if style == "arc3,rad=0": # Straight line
            cx, cy = (x1 + x2)/2, (y1 + y2)/2
        else:
            # Approximate arc center
            cx, cy = (x1 + x2)/2, (y1 + y2)/2
            # Add some curve offset based on style
            if start == 'PatchTST' and end == 'K8s':
                cx -= 0.15
            elif start == 'K8s' and end == 'GKE':
                cx += 0.15
                
        # Draw label
        ax.text(cx + tx, cy + ty, label, ha='center', va='center', 
                fontsize=9, color='#444444', 
                bbox=dict(facecolor='white', edgecolor='none', alpha=0.8, pad=1),
                zorder=5, family='sans-serif')
                
    plt.tight_layout()
    plt.savefig('paper/architecture.png', format='png', bbox_inches='tight', dpi=300)
    plt.close()

if __name__ == '__main__':
    draw_architecture()
    print("Architecture diagram generated at paper/architecture.png")
