#!/usr/bin/env python3
"""
Create NPC-to-hexagram kit mappings linking RSC NPC models to King Wen hexagrams.

Each NPC model (file ID 3,5,6,7,8,9,10,11,12) is mapped to a specific hexagram
based on vertex count patterns and emotional vector compatibility.
"""
import json
import os

NPC_MODEL_IDS = [3, 5, 6, 7, 8, 9, 10, 11, 12]
DATASETS_DIR = 'C:/Users/krist/Desktop/KING-WEN-I-CHING-IMMUTABLE-TABLES/DATASETS/kingwen_model_sets'
NPC_MESH_DIR = 'C:/Users/krist/Desktop/KING-WEN-I-CHING-IMMUTABLE-TABLES/DATASETS/kingwen_avatar_meshes_rsc'

def load_kit(hex_id):
    """Load hexagram kit file."""
    path = os.path.join(DATASETS_DIR, f'kit_{hex_id}.json')
    with open(path) as f:
        kit = json.load(f)
    vec = {}
    name = ''
    unicode = ''
    binary = ''
    category = ''
    action = ''
    for extra in kit.get('extra', []):
        key = extra.get('key')
        if key in ['voiceWeight', 'coherence', 'chaos', 'whimsy', 'darkTone', 'porosity']:
            vec[key] = extra.get('intvalue', 0) / 10000.0
        elif key == 'name':
            name = extra.get('stringvalue', '')
        elif key == 'unicode':
            unicode = extra.get('stringvalue', '')
        elif key == 'binary':
            binary = extra.get('stringvalue', '')
    
    # Also get category/action from baseModel/positions
    return {
        'hex_id': hex_id,
        'name': name,
        'unicode': unicode,
        'binary': binary,
        'vector': vec,
        'baseModel': kit.get('baseModel', hex_id),
        'positions': kit.get('positions', []),
    }

def load_npc_ply_metadata(model_id):
    """Read PLY file header to get vertex/face counts."""
    path = os.path.join(NPC_MESH_DIR, f'rsc_npc_{model_id}.ply')
    try:
        with open(path, 'rb') as f:
            data = f.read()
        
        header_end = data.find(b'end_header\n')
        if header_end == -1:
            header_end = data.find(b'end_header\r\n')
        header = data[:header_end].decode('ascii')
        
        vc = fc = 0
        for line in header.split('\n'):
            if 'element vertex' in line:
                vc = int(line.split()[2])
            elif 'element face' in line:
                fc = int(line.split()[2])
        
        return {'model_id': model_id, 'vertex_count': vc, 'face_count': fc, 'ply_path': path}
    except Exception as e:
        return {'model_id': model_id, 'vertex_count': 0, 'face_count': 0, 'error': str(e)}

def compute_similarity(npc, kit):
    """
    Compute similarity between NLP and hexagram kit.
    NPC models are mapped based on:
    1. Vertex count compatibility (small models → small hexagrams, large → large)
    2. Emotional vector distance
    """
    npc_vc = npc['vertex_count']
    
    # Scale NPC vertex count to hexagram vector magnitude
    # NPC models range from 16 to 206 vertices
    # King Wen vectors range ~0.1-0.6
    npc_scale = min(1.0, npc_vc / 200.0)
    
    kit_vec = kit['vector']
    avg_vec = sum(kit_vec.values()) / len(kit_vec) if kit_vec else 0.5
    
    # Distance between npc_scale and avg_vec
    vec_distance = abs(npc_scale - avg_vec)
    
    return vec_distance

def main():
    # Load all NPC models
    npcs = [load_npc_ply_metadata(mid) for mid in NPC_MODEL_IDS]
    
    # Load all hexagram kits
    kits = {hex_id: load_kit(hex_id) for hex_id in range(1, 65)}
    
    print("NPC Models loaded:")
    for npc in npcs:
        print(f"  Model {npc['model_id']}: {npc['vertex_count']} verts, {npc['face_count']} faces")
    
    # Map NPC models to hexagrams
    # Strategy: assign each NPC to the hexagram whose vector best matches
    # the NPC's relative size and complexity
    
    # Sort NPCs by vertex count for systematic assignment
    npcs_sorted = sorted(npcs, key=lambda n: n['vertex_count'])
    
    # Sort hexagrams by vector strength (voiceWeight + coherence)
    hex_by_strength = sorted(range(1, 65), 
                            key=lambda h: kits[h]['vector'].get('voiceWeight', 0) + kits[h]['vector'].get('coherence', 0))
    
    # Assign smallest NPCs to least "active" hexagrams (low voiceWeight),
    # largest NPCs to most "active" hexagrams (high voiceWeight)
    mappings = []
    for i, npc in enumerate(npcs_sorted):
        # Map i-th smallest NPC to i-th percentile of hexagrams by strength
        # This gives 9 hexagrams spread across the strength range
        hex_idx = int((i / (len(npcs_sorted) - 1)) * (len(hex_by_strength) - 1))
        hex_id = hex_by_strength[hex_idx]
        kit = kits[hex_id]
        
        mappings.append({
            'npc_model_id': npc['model_id'],
            'npc_vertex_count': npc['vertex_count'],
            'npc_face_count': npc['face_count'],
            'hexagram_id': hex_id,
            'hexagram_name': kit['name'],
            'hexagram_unicode': kit['unicode'],
            'hexagram_binary': kit['binary'],
            'kit_base_model': kit['baseModel'],
            'emotional_vector': kit['vector'],
            'ply_file': f'DATASETS/kingwen_avatar_meshes_rsc/rsc_npc_{npc["model_id"]}.ply',
        })
    
    # Write mapping file
    output_path = os.path.join(DATASETS_DIR, 'npc_kit_mappings.json')
    with open(output_path, 'w') as f:
        json.dump(mappings, f, indent=2)
    
    print(f"\nWrote {len(mappings)} NPC→hexagram mappings to {output_path}")
    print("\nMappings:")
    for m in mappings:
        v = m['emotional_vector']
        print(f"  NPC {m['npc_model_id']} ({m['npc_vertex_count']}v/{m['npc_face_count']}f) → "
              f"Hex {m['hexagram_id']:2d} ({m['hexagram_name']}) "
              f"VW={v.get('voiceWeight',0):.3f} COH={v.get('coherence',0):.3f}")

if __name__ == '__main__':
    main()
