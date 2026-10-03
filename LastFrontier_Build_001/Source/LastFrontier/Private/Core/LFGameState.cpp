#include "Core/LFGameState.h"
#include "Net/UnrealNetwork.h"

void ALFGameState::GetLifetimeReplicatedProps(TArray<FLifetimeProperty>& OutLifetimeProps) const
{
    Super::GetLifetimeReplicatedProps(OutLifetimeProps);
    DOREPLIFETIME(ALFGameState, AlivePlayers);
}
