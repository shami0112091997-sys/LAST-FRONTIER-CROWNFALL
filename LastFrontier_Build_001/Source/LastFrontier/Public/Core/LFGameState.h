#pragma once
#include "CoreMinimal.h"
#include "GameFramework/GameStateBase.h"
#include "LFGameState.generated.h"

UCLASS()
class LASTFRONTIER_API ALFGameState : public AGameStateBase
{
    GENERATED_BODY()

public:
    UPROPERTY(Replicated, BlueprintReadOnly, Category="Crownfall|Match")
    int32 AlivePlayers = 0;

    virtual void GetLifetimeReplicatedProps(TArray<FLifetimeProperty>& OutLifetimeProps) const override;
};
