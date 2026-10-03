#include "Core/LFGameMode.h"
#include "Core/LFGameState.h"
#include "Character/LFCharacter.h"

ALFGameMode::ALFGameMode()
{
    GameStateClass = ALFGameState::StaticClass();
    DefaultPawnClass = ALFCharacter::StaticClass();
}
