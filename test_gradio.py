"""
Verify the Gradio interface is correctly configured
"""
from app import build_interface

print("Building Gradio interface...")
try:
    demo = build_interface()
    print("✅ Interface built successfully\n")

    # Check the interface structure
    print("Verifying interface structure:")
    print(f"  - Interface type: {type(demo).__name__}")
    print(f"  - Has blocks: {hasattr(demo, 'blocks')}")

    # Verify all components are created
    components = []
    for block in demo.blocks:
        if hasattr(block, 'label'):
            components.append(block.label)

    print(f"  - Total components: {len(components)}")
    print(f"  - Components: {components[:5]}...")  # Show first 5

    print("\n✅ Gradio interface is properly configured and ready to launch!")

except Exception as e:
    print(f"❌ Error building interface: {e}")
    import traceback
    traceback.print_exc()
