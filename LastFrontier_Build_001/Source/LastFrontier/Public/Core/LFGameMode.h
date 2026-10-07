#pragma once

#include "CoreMinimal.h"
#include "GameFramework/GameModeBase.h"
#include "LFGameMode.generated.h"

UCLASS()
class LASTFRONTIER_API ALFGameMode : public AGameModeBase
{
    GENERATED_BODY()

public:
    ALFGameMode();

protected:
    virtual void BeginPlay() override;

private:
    void EnsurePlayablePawn();
};
