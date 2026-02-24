"""
Test script for Architecture System
Tests deterministic layout engine and AI blueprint generator
"""

import sys
sys.path.append('backend')

from services.deterministic_layout_engine import DeterministicLayoutEngine
from services.ai_blueprint_generator import AIBlueprintGenerator

def test_layout_engine():
    """Test deterministic layout engine"""
    print("=" * 60)
    print("Testing Deterministic Layout Engine")
    print("=" * 60)
    
    engine = DeterministicLayoutEngine()
    
    # Test cases
    test_prompts = [
        "30x40 ft plot, G+1, 2BHK",
        "40x50 ft plot, G+2, 3BHK, duplex",
        "25x30 ft plot, 1BHK",
        "10x12 m plot, G+1, 2BHK, internal staircase"
    ]
    
    for prompt in test_prompts:
        print(f"\nTest: {prompt}")
        print("-" * 60)
        
        # Parse input
        params = engine.parse_input(prompt)
        if 'error' in params:
            print(f"❌ Error: {params['error']}")
            continue
        
        print(f"✓ Parsed parameters:")
        print(f"  Plot: {params['plot_width']:.2f}m × {params['plot_length']:.2f}m")
        print(f"  Floors: {params['floors']}")
        print(f"  Configuration: {params['configuration']}")
        
        # Generate layout
        layout = engine.generate_layout(params)
        if 'error' in layout:
            print(f"❌ Error: {layout['error']}")
            continue
        
        print(f"✓ Generated layout:")
        print(f"  Total Built-up: {layout['total_built_up_area']} m²")
        print(f"  Efficiency: {layout['efficiency_ratio']*100:.0f}%")
        print(f"  Floors: {len(layout['floors'])}")
        
        for floor in layout['floors']:
            print(f"  Floor {floor['floor_number']}: {len(floor['rooms'])} rooms, {floor['built_up_area']} m²")

def test_blueprint_generator():
    """Test AI blueprint generator (without Ollama)"""
    print("\n" + "=" * 60)
    print("Testing AI Blueprint Generator")
    print("=" * 60)
    
    generator = AIBlueprintGenerator()
    
    prompt = "30x40 ft plot, G+1, 2BHK"
    print(f"\nTest: {prompt}")
    print("-" * 60)
    
    result = generator.generate_blueprint(prompt)
    
    if 'error' in result:
        print(f"❌ Error: {result['error']}")
        return
    
    print(f"✓ Blueprint generated successfully!")
    print(f"  Configuration: {result['layout']['configuration']}")
    print(f"  Total Built-up: {result['layout']['total_built_up_area']} m²")
    print(f"  Image size: {len(result['blueprint_image'])} bytes")
    print(f"  Metadata: {result['metadata']}")

if __name__ == "__main__":
    print("\n🏗️  BuildWise Architecture System Test\n")
    
    try:
        test_layout_engine()
        test_blueprint_generator()
        
        print("\n" + "=" * 60)
        print("✅ All tests completed!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
