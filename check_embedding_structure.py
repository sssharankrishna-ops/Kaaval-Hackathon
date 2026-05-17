import json
from pathlib import Path

# Check embedding structure
emb_file = Path('backend/embeddings_output/darshina_embeddings.json')
with open(emb_file) as f:
    data = json.load(f)

print('Embedding File Structure:')
print(f'  Person: {data.get("person_name")}')
print(f'  Total images: {data.get("total_images")}')
print(f'  Successful extractions: {data.get("successful_extractions")}')
print(f'  Keys in file: {list(data.keys())}')

if 'embeddings' in data:
    print(f'  Embeddings array length: {len(data["embeddings"])}')
    if data['embeddings']:
        first_emb = data['embeddings'][0]
        print(f'    First embedding keys: {list(first_emb.keys())}')
        if 'embedding' in first_emb:
            print(f'    Embedding dimensions: {len(first_emb["embedding"])}')
else:
    print('  WARNING: No embeddings array found!')
