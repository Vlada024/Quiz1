import os
import json
import numpy as np
from PIL import Image
from sklearn.cluster import KMeans
from datetime import datetime

# Constants
DATA_DIR = 'state_flags_png'
THUMBS_DIR = 'project/build/thumbs'
POINTS_PATH = 'project/build/points.json'
THUMB_WIDTH = 120
K = 4
SEED = 42

# Helper: map filename to state name
def filename_to_state(filename):
    name = os.path.splitext(filename)[0]
    name = name.replace('_', ' ').replace('-', ' ')
    return name.title()

# Gather image files
def get_image_files():
    return [f for f in os.listdir(DATA_DIR) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]

# Process images
def process_images(files):
    states = []
    rgbs = []
    for fname in files:
        path = os.path.join(DATA_DIR, fname)
        try:
            img = Image.open(path).convert('RGB')
        except Exception as e:
            print(f"Error loading {fname}: {e}")
            continue
        arr = np.asarray(img) / 255.0
        mean_rgb = arr.mean(axis=(0,1)).tolist()
        rgbs.append(mean_rgb)
        # Save thumbnail
        thumb_path = os.path.join(THUMBS_DIR, os.path.splitext(fname)[0] + '.jpg')
        img.thumbnail((THUMB_WIDTH, THUMB_WIDTH*10))
        img.save(thumb_path, 'JPEG')
        states.append({
            'state': filename_to_state(fname),
            'file': fname,
            'thumb': thumb_path,
            'rgb': mean_rgb
        })
    return states, np.array(rgbs)

# Main
if __name__ == '__main__':
    os.makedirs(THUMBS_DIR, exist_ok=True)
    files = get_image_files()
    if len(files) != 50:
        print(f"Error: Found {len(files)} images, expected 50.")
        missing = set([filename_to_state(f) for f in files])
        print(f"States found: {sorted(missing)}")
        exit(1)
    states, rgbs = process_images(files)
    kmeans = KMeans(n_clusters=K, random_state=SEED, n_init='auto').fit(rgbs)
    labels = kmeans.labels_.tolist()
    centroids = kmeans.cluster_centers_.tolist()
    # Assign clusters
    for i, state in enumerate(states):
        state['cluster'] = labels[i]
        state['thumb'] = os.path.relpath(state['thumb'], start='project')
    # Save points.json
    out = {
        'meta': {
            'k': K,
            'created_at': datetime.now().isoformat(),
            'n': 50
        },
        'centroids': centroids,
        'states': states
    }
    with open(POINTS_PATH, 'w') as f:
        json.dump(out, f, indent=2)
    # Print summary
    print(f"Cluster sizes: {np.bincount(labels)}")
    print(f"Centroid RGBs:")
    for i, c in enumerate(centroids):
        print(f"  Cluster {i}: {c}")
    print(f"Done. points.json written to {POINTS_PATH}")
