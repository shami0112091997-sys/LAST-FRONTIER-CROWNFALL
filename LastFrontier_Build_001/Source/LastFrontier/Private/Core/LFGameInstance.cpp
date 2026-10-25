#include "Core/LFGameInstance.h"

void ULFGameInstance::Init()
{
    Super::Init();
    // Release builds may suppress log output; useful when logs are available
    // from a controlled independent Android test environment.
    UE_LOG(LogTemp, Display, TEXT("CROWNFALL_BOOT_GAMEINSTANCE_INIT=M131"));
}
