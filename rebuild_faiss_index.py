"""Rebuild FAISS index from embedding JSON files"""
import json
import numpy as np
import faiss
import pickle
from pathlib import Path
import os

print("\n" + "="*70)
print("REBUILDING FAISS INDEX FROM EMBEDDINGS")
print("="*70 + "\n")

# Paths
embeddings_dir = Path("backend/embeddings_output")
faiss_dir = Path("backend/models/faiss")
faiss_dir.mkdir(parents=True, exist_ok=True)

index_path = faiss_dir / "embeddings.index"
metadata_path = faiss_dir / "metadata.pkl"

# Load all embeddings
embeddings_list = []
metadata = {'person_ids': [], 'person_names': [], 'dimension': 512, 'n_embeddings': 0}

print("[1/4] Loading embeddings from JSON files...")
embedding_files = sorted(list(embeddings_dir.glob("*_embeddings.json")))
print(f"Found {len(embedding_files)} embedding files")

person_id = 0
total_vectors = 0

for emb_file in embedding_files:
    try:
        with open(emb_file) as f:
            data = json.load(f)
        
        person_name = data.get('person_name', emb_file.stem.replace('_embeddings', ''))
        embeddings = data.get('embeddings', [])
        
        if embeddings:
            print(f"  {person_name}: {len(embeddings)} embeddings")
            
            for emb_data in embeddings:
                if 'embedding_vector' in emb_data:
                    vector = emb_data['embedding_vector']
                    embeddings_list.append(vector)
                    metadata['person_ids'].append(person_id)
                    metadata['person_names'].append(person_name)
                    total_vectors += 1
            
            person_id += 1
    except Exception as e:
        print(f"  ✗ Error loading {emb_file.name}: {e}")

print(f"\n✓ Loaded {total_vectors} vectors from {len(embedding_files)} persons")

if total_vectors == 0:
    print("\n✗ No embeddings found! Cannot build FAISS index.")
    exit(1)

# Create FAISS index
print("\n[2/4] Creating FAISS index...")
vectors = np.array(embeddings_list, dtype=np.float32)
print(f"Vector shape: {vectors.shape}")

# Normalize vectors for cosine distance
faiss.normalize_L2(vectors)

# Create index
dimension = vectors.shape[1]
index = faiss.IndexFlatL2(dimension)
index.add(vectors)

metadata['dimension'] = dimension
metadata['n_embeddings'] = total_vectors

print(f"✓ Created index with {index.ntotal} embeddings")

# Save FAISS index
print(f"\n[3/4] Saving FAISS index to {index_path}...")
faiss.write_index(index, str(index_path))
print(f"✓ FAISS index saved ({index_path.stat().st_size / 1024:.1f} KB)")

# Save metadata
print(f"\n[4/4] Saving metadata to {metadata_path}...")
with open(metadata_path, 'wb') as f:
    pickle.dump(metadata, f)
print(f"✓ Metadata saved")

print("\n" + "="*70)
print(f"FAISS INDEX REBUILT SUCCESSFULLY")
print(f"  Total embeddings: {total_vectors}")
print(f"  Total persons: {len(set(metadata['person_names']))}")
print(f"  Dimension: {dimension}")
print("="*70 + "\n")

print("Restart the backend server for changes to take effect:")
print("  Stop-Job -Name Backend; Start-Job -Name Backend ...")
