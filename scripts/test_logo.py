#!/usr/bin/env python3
"""
Test script to verify logo loading from different paths
"""

import os
import streamlit as st

def test_logo_paths():
    """Test different logo paths to see which one works"""
    
    # Get current working directory
    cwd = os.getcwd()
    print(f"Current working directory: {cwd}")
    
    # Define possible logo paths
    logo_paths = [
        "design/triangle_tweener_logo.png",
        "../design/triangle_tweener_logo.png", 
        "dashboard/design/triangle_tweener_logo.png",
        os.path.join(cwd, "dashboard/design/triangle_tweener_logo.png")
    ]
    
    print("\nTesting logo paths:")
    for i, path in enumerate(logo_paths, 1):
        exists = os.path.exists(path)
        print(f"{i}. {path}: {'✅ EXISTS' if exists else '❌ NOT FOUND'}")
        
        if exists:
            try:
                # Try to load with streamlit
                st.image(path, width=100)
                print(f"   ✅ Streamlit can load: {path}")
                return path
            except Exception as e:
                print(f"   ❌ Streamlit error: {e}")
    
    print("\n❌ No working logo path found")
    return None

if __name__ == "__main__":
    working_path = test_logo_paths()
    if working_path:
        print(f"\n✅ Recommended logo path: {working_path}")
    else:
        print("\n❌ Logo loading failed - check file permissions and paths") 