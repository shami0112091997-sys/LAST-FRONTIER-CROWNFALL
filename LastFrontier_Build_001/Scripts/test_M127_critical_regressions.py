#!/usr/bin/env python3
"""Tests M127 false-negative regressions against synthetic DEX and mock AAB only."""
import tempfile
from pathlib import Path
import M126_GooglePAD_Dex_Method_Audit_ReadOnly as audit
from test_M126_synthetic_dex import dex, bundle, METHOD

checks = 0
with tempfile.TemporaryDirectory() as t:
    target = Path(t) / 'fake.aab'
    tests = (
        ('wrong_owner_class', {'class_name': 'Lcom/example/OtherClass;'}, 3,
         'REVIEW_METHOD_OWNER_OR_INHERITANCE'),
        ('wrong_noargs_boolean_signature', {'bool_return': False}, 3,
         'REVIEW_AVAILABLE_JNI_SIGNATURE'),
        ('correct_owner_and_signature', {}, 0,
         'STATIC_ACTIVITY_METHODS_FOUND_OTHER_SIGNATURES_UNVERIFIED'),
        ('not_defined_in_class_data', {'has_class_data': False}, 3,
         'REVIEW_POTENTIAL_JNI_METHOD_MISMATCH'),
        ('unrelated_method_id', {'defined_name': 'AndroidThunkJava_GooglePAD_Unrelated'}, 3,
         'REVIEW_POTENTIAL_JNI_METHOD_MISMATCH'),
    )
    for _, options, expected_status, expected_assessment in tests:
        bundle(target, dex(**options), METHOD.encode() + b'\0')
        code, result = audit.audit(target)
        assert code == expected_status, (options, code)
        assert result['M126_ASSESSMENT'] == expected_assessment, (options, result)
        checks += 1
    bundle(target, dex(class_name='Lcom/example/OtherClass;'), b'no googlepad symbols')
    code, result = audit.audit(target)
    assert code == 0 and result['M126_ASSESSMENT'] == 'NO_NATIVE_GOOGLEPAD_JNI_NAMES_FOUND'
    checks += 1
print(f'M127_REGRESSION_CHECKS=PASS ({checks} synthetic cases; NO real AAB/device tested)')
