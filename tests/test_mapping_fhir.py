import json

# TODO: Incorporate actual examples. Simple unit examples are fine for now
EXAMPLES = dict()
with open('tests/data/patient_example.json', 'r') as f:
    FHIR_PATIENT_EX = json.load(f)
    EXAMPLES['Patient'] = FHIR_PATIENT_EX

"""
{
    'Patient': { ... },

}
"""