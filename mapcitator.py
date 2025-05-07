from citation_map import generate_citation_map
import pandas as pd
import folium
import sys
import os

# Generate initial map and CSV
scholar_id = sys.argv[1]
csv_output_path = 'citations.csv'

if not os.path.exists(csv_output_path):
    print("Generating citations.csv...")
    generate_citation_map(scholar_id, csv_output_path=csv_output_path)
else:
    print(f"{csv_output_path} already exists. Skipping citation extraction.")

# Read and aggregate citation data
df = pd.read_csv(csv_output_path)
agg_counts = df.groupby(['latitude', 'longitude']).size().reset_index(name='counts')

# Define thresholds and pink colors (light to dark)
thresholds = [1, 3, 5, 30]
colors = ['#ffdde6', '#ff99bb', '#ff4d88', '#cc0066', '#800040']  # Light pink to dark pink

def get_color(count):
    for i, t in enumerate(thresholds):
        if count <= t:
            return colors[i]
    return colors[-1]

# Create the map
m = folium.Map(tiles='cartodbpositron')

for _, row in agg_counts.iterrows():
    color = get_color(row['counts'])
    folium.CircleMarker(
        location=[row['latitude'], row['longitude']],
        radius=16,
        color='black',
        weight=2,
        fill=True,
        fill_color=color,
        fill_opacity=0.85,
        popup=folium.Popup(f"Citations: {row['counts']}", parse_html=True),
        tooltip=f"Citations: {row['counts']}"
    ).add_to(m)
    # Add the number as a label
    #folium.map.Marker(
    #    [row['latitude'], row['longitude']],
    #    icon=folium.DivIcon(
    #        html=f"""<div style="font-size: 16px; font-weight: bold; color: white; text-align: center; width: 32px;">{row['counts']}</div>"""
    #    )
    #).add_to(m)

# Add a custom discrete legend
def add_discrete_legend(m, thresholds, colors):
    legend_html = '''
    <div id="draggable-legend" style="
        position: fixed;
        top: 40px; right: 10px; z-index:9999;
        background: white;
        padding: 24px 32px 24px 24px;
        border-radius: 12px;
        border: 2px solid grey;
        font-size: 22px;
        box-shadow: 2px 2px 8px rgba(0,0,0,0.2);
        cursor: move;
        ">
        <b style="font-size: 24px;">Citation Count</b><br>
    '''
    prev = 0
    for i, t in enumerate(thresholds):
        if i == 0:
            label = f"{prev+1}"
        else:
            label = f"{prev+1}-{t}"
        legend_html += (
            f'<i style="background:{colors[i]};'
            'width:32px;height:32px;'
            'float:left;margin-right:16px;'
            'opacity:0.85;display:inline-block;'
            'border-radius: 50%;'
            'border: 1px solid #333;"></i>'
            f'<span style="line-height:32px;">{label}</span><br>'
        )
        prev = t
    legend_html += (
        f'<i style="background:{colors[-1]};'
        'width:32px;height:32px;'
        'float:left;margin-right:16px;'
        'opacity:0.85;display:inline-block;'
        'border-radius: 50%;'
        'border: 1px solid #333;"></i>'
        f'<span style="line-height:32px;">>{thresholds[-1]}</span><br>'
    )
    legend_html += '</div>'
    m.get_root().html.add_child(folium.Element(legend_html))

add_discrete_legend(m, thresholds, colors)

# Add draggable JavaScript
draggable_js = """
<script>
function makeLegendDraggable() {
    var legend = document.getElementById('draggable-legend');
    var pos1 = 0, pos2 = 0, pos3 = 0, pos4 = 0;
    legend.onmousedown = dragMouseDown;

    function dragMouseDown(e) {
        e = e || window.event;
        e.preventDefault();
        // get the mouse cursor position at startup:
        pos3 = e.clientX;
        pos4 = e.clientY;
        document.onmouseup = closeDragElement;
        document.onmousemove = elementDrag;
    }

    function elementDrag(e) {
        e = e || window.event;
        e.preventDefault();
        // calculate the new cursor position:
        pos1 = pos3 - e.clientX;
        pos2 = pos4 - e.clientY;
        pos3 = e.clientX;
        pos4 = e.clientY;
        // set the element's new position:
        legend.style.top = (legend.offsetTop - pos2) + "px";
        legend.style.left = (legend.offsetLeft - pos1) + "px";
        legend.style.right = "auto";
    }

    function closeDragElement() {
        document.onmouseup = null;
        document.onmousemove = null;
    }
}
makeLegendDraggable();
</script>
"""
m.get_root().html.add_child(folium.Element(draggable_js))


m.save('custom_label_map.html')
print("Map saved as custom_label_map.html")
