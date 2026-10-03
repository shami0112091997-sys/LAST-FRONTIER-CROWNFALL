# M47 Changeset

Baseline: recovered `LastFrontier_Build_001_M44_Validated.zip`.

This package does not rewrite the game design or pretend to replace missing Unreal assets. It hardens the Compile gate while preserving the recovered M44 C++ scaffold.

- Preserves UE association 5.8.
- Preserves LastFrontier runtime module and the recovered LFCharacter, LFGameMode, LFGameState, LFGameInstance classes.
- Preserves `AlivePlayers` replication setup.
- Adds `Run_M47_Compile_UE58.sh/.bat`.
- Adds `M47_PreCompile_Audit.py` and `M47_Compile_Evidence_Audit.py`.
- Keeps `TestMap.umap` as an unresolved genuine Unreal asset rather than generating a fake text file.

Promotion path:
`M44 Static PASS -> M47 Static Pre-Compile PASS -> REAL UBT COMPILE -> binary evidence audit -> Compile PASS -> TestMap asset -> Cook/Package -> Boot -> Automation/Gauntlet -> performance`.
