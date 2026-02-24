"""
Test fallback parameter extraction (regex-based)
"""

from services.ai_estimator import AIEstimator

ai_estimator = AIEstimator()

# Test prompt with steel and cement types
test_prompt = "Build G+2 residential building of 1500 sqft using Fe500 steel and OPC 53 cement with wage 500 in Mumbai"

print("=" * 60)
print("FALLBACK PARAMETER EXTRACTION TEST")
print("=" * 60)
print(f"Prompt: {test_prompt}")
print()

# Test fallback extraction directly
extracted = ai_estimator._fallback_extraction(test_prompt)

print("Extracted Parameters (Regex Fallback):")
print(f"  Area: {extracted['area']} sqft")
print(f"  Floors: {extracted['floors']} (G+2 = 3 floors)")
print(f"  Steel Type: {extracted['steel_type']}")
print(f"  Cement Type: {extracted['cement_type']}")
print(f"  Wage: ₹{extracted['wage']}/day")
print(f"  Location: {extracted['location']}")
print()

# Verify correctness
expected = {
    'area': 1500,
    'floors': 3,  # G+2 = 3 floors
    'steel_type': 'Fe500',
    'cement_type': 'OPC 53',
    'wage': 500,
    'location': 'Mumbai'
}

all_correct = all(extracted[k] == v for k, v in expected.items())
print(f"Result: {'✓ ALL CORRECT' if all_correct else '✗ SOME INCORRECT'}")
print("=" * 60)
