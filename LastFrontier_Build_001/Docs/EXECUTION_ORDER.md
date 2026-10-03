# Recovery execution order

## Linux
```bash
python3 Scripts/M44_Recovery_Static_Audit.py
export UE_ROOT=/path/to/UnrealEngine-5.8
Scripts/Run_M44_Compile_UE58.sh
# Create Content/Maps/TestMap.umap in UE 5.8 after compile succeeds.
Scripts/Run_M44_BuildCookPackage_UE58.sh
```

## Windows
```bat
py Scripts\M44_Recovery_Static_Audit.py
set UE_ROOT=C:\Path\To\UE_5.8
Scripts\Run_M44_Compile_UE58.bat
REM Create Content\Maps\TestMap.umap in UE 5.8 after compile succeeds.
Scripts\Run_M44_BuildCookPackage_UE58.bat
```

Do not mark a stage PASS without its real UE log and artifacts.
