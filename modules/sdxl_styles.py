import os
import re
import json
import math
from modules.extra_utils import get_files_from_folder

# Cannot use modules.config - validators causing circular imports
styles_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../sdxl_styles/'))

def normalize_key(k):
    k = k.replace('-', ' ')  # Replace hyphens with spaces
    words = k.split(' ')
    words = [w[:1].upper() + w[1:].lower() for w in words]  # Capitalize each word
    k = ' '.join(words)
    k = k.replace('3d', '3D')  # Fix "3d" → "3D"
    k = k.replace('Sai', 'SAI')  # Fix "Sai" → "SAI"
    k = k.replace('Mre', 'MRE')  # Fix "Mre" → "MRE"
    k = k.replace('(s', '(S')  # Ensure consistency
    return k

styles = {}

# Automatically load all JSON files in the styles folder
styles_files = get_files_from_folder(styles_path, ['.json'])

# Load styles from each JSON file
for styles_file in styles_files:
    try:
        with open(os.path.join(styles_path, styles_file), encoding='utf-8') as f:
            for entry in json.load(f):
                name = normalize_key(entry['name'])
                prompt = entry['prompt'] if 'prompt' in entry else ''
                negative_prompt = entry['negative_prompt'] if 'negative_prompt' in entry else ''
                styles[name] = (prompt, negative_prompt)
    except Exception as e:
        print(str(e))
        print(f'Failed to load style file {styles_file}')

def apply_style(style, positive):
    p, n = styles[style]
    result = positive
    placeholder = f"{{{style}}}"
    if placeholder in result:
        result = result.replace(placeholder, p)
        print(f"[Style Applied] Replaced '{placeholder}' with: {p}")
    return result.splitlines(), n.splitlines(), '{prompt}' in p

def get_words(arrays, total_mult, index):
    if len(arrays) == 1:
        return [arrays[0].split(',')[index]]
    else:
        words = arrays[0].split(',')
        word = words[index % len(words)]
        index -= index % len(words)
        index /= len(words)
        index = math.floor(index)
        return [word] + get_words(arrays[1:], math.floor(total_mult / len(words)), index)

def apply_arrays(text, index):
    arrays = re.findall(r'\[\[(.*?)\]\]', text)
    if len(arrays) == 0:
        return text
    
    print(f'[Arrays] processing: {text}')
    mult = 1
    for arr in arrays:
        words = arr.split(',')
        mult *= len(words)
    
    index %= mult
    chosen_words = get_words(arrays, mult, index)
    
    i = 0
    for arr in arrays:
        text = text.replace(f'[[{arr}]]', chosen_words[i], 1)   
        i = i + 1
    
    return text
