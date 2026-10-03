# M47 Current Execution Evidence

A real compile runner invocation was attempted in the current execution container.

Result:
- `M47_COMPILE_STATUS=BLOCKED_OR_FAILED`
- Exit code: `2`
- Reason: Unreal Engine 5.8 root was not found in this container.
- Evidence audit result: `M47_EVIDENCE_STATUS=COMPILE_NOT_PROVEN`

This is a valid negative execution result: the gate executed and failed closed before UnrealBuildTool because the required engine was absent. No Compile PASS, Build PASS, Cook PASS, Package PASS, Runtime PASS, or Automation PASS is claimed.
