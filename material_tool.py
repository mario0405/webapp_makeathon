import json
import os

# --- Global cache for our Knowledge Base ---
# We load the tree once to make searches fast
MATERIAL_TREE = None

def load_material_tree():
    """Loads the JSON tree from disk into memory."""
    global MATERIAL_TREE
    if MATERIAL_TREE is None:
        json_filename = 'material_tree.json'
        if not os.path.exists(json_filename):
            print(f"FATAL ERROR: '{json_filename}' not found.")
            return None
        
        with open(json_filename, 'r', encoding='utf-8') as f:
            MATERIAL_TREE = json.load(f)
        print("--- Material Knowledge Base loaded successfully. ---")
    return MATERIAL_TREE

def search_material_knowledgebase(material_name: str) -> str:
    """
    This is the TOOL our AI Agent will call.
    It searches the loaded material tree for a specific material name
    and returns its direct sub-categories (children).
    
    Args:
        material_name: The exact name of the material to search for.
        
    Returns:
        A JSON string describing the findings.
    """
    
    # Ensure the KB is loaded
    tree = load_material_tree()
    if tree is None:
        return json.dumps({"error": "Knowledge Base (material_tree.json) is not loaded."})

    # We will use a recursive helper function to find the node
    def find_node(nodes_list, name):
        for node in nodes_list:
            # Case-insensitive and strip whitespace for a better match
            if node['name'].strip().lower() == name.strip().lower():
                return node  # Found it!
            
            # If not found, search in its children
            if node['children']:
                found = find_node(node['children'], name)
                if found:
                    return found
        return None # Not found at this level

    # Start the search from the top-level categories
    found_node = find_node(tree, material_name)

    # --- Prepare the response for the AI ---
    if found_node:
        if found_node['children']:
            # Get the names of all children
            child_names = [child['name'] for child in found_node['children']]
            response = {
                "status": "found",
                "material": material_name,
                "subcategories": child_names
            }
        else:
            # The material was found but has no sub-categories
            response = {
                "status": "found",
                "material": material_name,
                "subcategories": []
            }
    else:
        # The material was not found anywhere in the tree
        response = {
            "status": "not_found",
            "material": material_name
        }
            
    # Return the result as a JSON string, as this is
    # what the AI agent will receive and parse.
    return json.dumps(response, ensure_ascii=False)

# --- You can run this file directly to test the tool ---
if __name__ == "__main__":
    print("--- Testing material_tool.py ---")
    
    # Test 1: A top-level category
    print("\nTest 1: 'Beläge'")
    print(search_material_knowledgebase("Beläge"))
    
    # Test 2: A nested category
    print("\nTest 2: 'Walzasphalt'")
    print(search_material_knowledgebase("Walzasphalt"))
    
    # Test 3: A material with no children
    print("\nTest 3: 'gestrahlt'")
    print(search_material_knowledgebase("gestrahlt"))

    # Test 4: A material that doesn't exist
    print("\nTest 4: 'Stahlbeton'")
    print(search_material_knowledgebase("Stahlbeton"))