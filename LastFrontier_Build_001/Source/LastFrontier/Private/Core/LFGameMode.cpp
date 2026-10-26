#include "Core/LFGameMode.h"

#include "Character/LFCharacter.h"
#include "Core/LFGameState.h"
#include "UI/LFHUD.h"
#include "World/LFWorldDirector.h"
#include "Engine/World.h"
#include "GameFramework/PlayerController.h"
#include "Kismet/GameplayStatics.h"

ALFGameMode::ALFGameMode()
{
    GameStateClass = ALFGameState::StaticClass();
    DefaultPawnClass = ALFCharacter::StaticClass();
    HUDClass = ALFHUD::StaticClass();
}

void ALFGameMode::BeginPlay()
{
    Super::BeginPlay();
    UE_LOG(LogTemp, Display, TEXT("CROWNFALL_BOOT_GAMEMODE_BEGINPLAY=M131"));

    if (UWorld* World = GetWorld())
    {
        ALFWorldDirector* Director = World->SpawnActor<ALFWorldDirector>(
            ALFWorldDirector::StaticClass(), FVector::ZeroVector, FRotator::ZeroRotator);
        if (!Director)
        {
            UE_LOG(LogTemp, Error, TEXT("CROWNFALL_WORLD_DIRECTOR_SPAWN_FAILED"));
        }
    }

    EnsurePlayablePawn();
}

void ALFGameMode::EnsurePlayablePawn()
{
    APlayerController* PC = UGameplayStatics::GetPlayerController(this, 0);
    if (!PC || PC->GetPawn() || !GetWorld())
    {
        return;
    }

    const FVector SpawnLocation(0.0f, -3200.0f, 180.0f);
    const FRotator SpawnRotation(0.0f, 0.0f, 0.0f);

    FActorSpawnParameters Params;
    Params.SpawnCollisionHandlingOverride = ESpawnActorCollisionHandlingMethod::AdjustIfPossibleButAlwaysSpawn;

    ALFCharacter* Pawn = GetWorld()->SpawnActor<ALFCharacter>(ALFCharacter::StaticClass(), SpawnLocation, SpawnRotation, Params);
    if (Pawn)
    {
        PC->Possess(Pawn);
        UE_LOG(LogTemp, Display, TEXT("CROWNFALL_M60_PLAYER=READY"));
    }
    else
    {
        UE_LOG(LogTemp, Error, TEXT("CROWNFALL_BOOT_PLAYER_SPAWN_FAILED"));
    }
}
