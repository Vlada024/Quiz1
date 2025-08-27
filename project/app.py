import streamlit as st
import json
import plotly.graph_objs as go
import os

# Load data
with open('project/build/points.json') as f:
    data = json.load(f)

states = data['states']
centroids = data['centroids']
k = data['meta']['k']

# Cluster colors
CLUSTER_COLORS = ['#e41a1c', '#377eb8', '#4daf4a', '#ff7f00']

# Prepare plot data
points = [s['rgb'] for s in states]
labels = [s['cluster'] for s in states]
state_names = [s['state'] for s in states]

# 3D scatter points
scatter = go.Scatter3d(
    x=[p[0] for p in points],
    y=[p[1] for p in points],
    z=[p[2] for p in points],
    mode='markers',
    marker=dict(
        size=6,
        color=[CLUSTER_COLORS[l] for l in labels],
        line=dict(width=1, color='black')
    ),
    text=[f"{state_names[i]}<br>RGB: {points[i]}<br>Cluster: {labels[i]}" for i in range(len(points))],
    hoverinfo='text',
    name='States'
)

# Centroids
centroid_scatter = go.Scatter3d(
    x=[c[0] for c in centroids],
    y=[c[1] for c in centroids],
    z=[c[2] for c in centroids],
    mode='markers',
    marker=dict(
        size=14,
        color=CLUSTER_COLORS,
        line=dict(width=3, color='black')
    ),
    text=[f"Centroid {i}: {centroids[i]}" for i in range(k)],
    hoverinfo='text',
    name='Centroids'
)

# Lines from points to centroids
lines = []
for i, p in enumerate(points):
    c = centroids[labels[i]]
    lines.append(go.Scatter3d(
        x=[p[0], c[0]],
        y=[p[1], c[1]],
        z=[p[2], c[2]],
        mode='lines',
        line=dict(color=CLUSTER_COLORS[labels[i]], width=2),
        showlegend=False
    ))

# Layout
layout = go.Layout(
    scene=dict(
    xaxis=dict(title='R', range=[0,1], backgroundcolor='rgb(240,240,240)', showspikes=False, showbackground=True, showticklabels=True, ticks='outside', tickmode='array', tickvals=[0,0.2,0.4,0.6,0.8,1], ticktext=['0','0.2','0.4','0.6','0.8','1']),
    yaxis=dict(title='G', range=[0,1], backgroundcolor='rgb(240,240,240)', showspikes=False, showbackground=True, showticklabels=True, ticks='outside', tickmode='array', tickvals=[0,0.2,0.4,0.6,0.8,1], ticktext=['0','0.2','0.4','0.6','0.8','1']),
    zaxis=dict(title='B', range=[0,1], backgroundcolor='rgb(240,240,240)', showspikes=False, showbackground=True, showticklabels=True, ticks='outside', tickmode='array', tickvals=[0,0.2,0.4,0.6,0.8,1], ticktext=['0','0.2','0.4','0.6','0.8','1']),
        dragmode='turntable',
        aspectmode='cube',
        bgcolor='rgb(240,240,240)',
    ),
    margin=dict(l=0, r=0, b=0, t=40),
    legend=dict(x=0, y=1),
)
fig = go.Figure(data=[scatter, centroid_scatter] + lines, layout=layout)
fig.update_layout(scene_camera=dict(eye=dict(x=1.5, y=1.5, z=1.5)), scene_dragmode='turntable')

fig = go.Figure(data=[scatter, centroid_scatter] + lines, layout=layout)

# Streamlit UI
st.title('US State Flags: RGB Clustering')
st.write('Each flag is represented as a single RGB point (mean color), clustered into 4 groups using k-means. Explore the clusters and flag thumbnails below!')
st.plotly_chart(fig, use_container_width=True)

# Cluster panels
for cluster_id in range(k):
    st.subheader(f'Cluster {cluster_id}')
    cluster_states = [s for s in states if s['cluster'] == cluster_id]
    cols = st.columns(4)
    for i, state in enumerate(cluster_states):
        with cols[i % 4]:
            thumb_path = os.path.join('project', state['thumb'])
            st.image(thumb_path, width=80)
            st.caption(state['state'])
