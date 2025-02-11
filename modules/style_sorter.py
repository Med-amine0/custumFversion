import os
import gradio as gr
import modules.localization as localization
import json

all_styles = []
original_order = []  # Store the original order of styles

def try_load_sorted_styles(style_names, default_selected):
    global all_styles, original_order
    all_styles = style_names
    original_order = style_names.copy()  # Save the original order
    
    try:
        if os.path.exists('sorted_styles.json'):
            with open('sorted_styles.json', 'rt', encoding='utf-8') as fp:
                sorted_styles = []
                for x in json.load(fp):
                    if x in all_styles:
                        sorted_styles.append(x)
                for x in all_styles:
                    if x not in sorted_styles:
                        sorted_styles.append(x)
                all_styles = sorted_styles
    except Exception as e:
        print('Load style sorting failed.')
        print(e)
    
    # Handle default selected items
    unselected = [y for y in all_styles if y not in default_selected]
    all_styles = default_selected + unselected
    return

def sort_styles(selected):
    global all_styles
    
    # Create a new list based on original order
    new_order = []
    
    # First add selected items
    for style in original_order:
        if style in selected:
            new_order.append(style)
    
    # Then add unselected items in their original order
    for style in original_order:
        if style not in selected:
            new_order.append(style)
    
    try:
        with open('sorted_styles.json', 'wt', encoding='utf-8') as fp:
            json.dump(new_order, fp, indent=4)
    except Exception as e:
        print('Write style sorting failed.')
        print(e)
    
    all_styles = new_order
    return gr.CheckboxGroup.update(choices=new_order)

def localization_key(x):
    return x + localization.current_translation.get(x, '')

def search_styles(selected, query):
    if len(query.replace(' ', '')) == 0:
        return sort_styles(selected)
    
    # Filter based on search while maintaining original relative ordering
    matched = []
    unmatched = []
    
    for style in original_order:
        if query.lower() in localization_key(style).lower():
            if style in selected:
                matched.insert(0, style)  # Selected matches go first
            else:
                matched.append(style)     # Unselected matches go after
        else:
            if style in selected:
                unmatched.insert(0, style)  # Selected non-matches go after matches
            else:
                unmatched.append(style)     # Unselected non-matches go last
    
    sorted_styles = matched + unmatched
    return gr.CheckboxGroup.update(choices=sorted_styles)
