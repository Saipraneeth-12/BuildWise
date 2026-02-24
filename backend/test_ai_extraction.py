"""
Test AI parameter extraction with steel and cement types
"""

from services.ai_estimator import AIEstimator

ai_estimator = AIEstimator()

# Test prompt with steel and cement types
test_prompt = "Build G+2 residential building of 1500 sqft using Fe500 steel and OPC 53 cement with wage 500 in Mumbai"

print("=" * 60)
print("AI PARAMETER EXTRACTION TEST")
print("=" * 60)
print(f"Prompt: {test_prompt}")
print()

extracted = ai_estimator.extract_parameters(test_prompt)

print("Extracted Parameters:")
print(f"  Area: {extracted['area']} sqft")
print(f"  Floors: {extracted['floors']}")
print(f"  Steel Type: {extracted['steel_type']}")
print(f"  Cement Type: {extracted['cement_type']}")
print(f"  Wage: ₹{extracted['wage']}/day")
print(f"  Location: {extracted['location']}")
print()
print("✓ Extraction successful!")
print("=" * 60)
