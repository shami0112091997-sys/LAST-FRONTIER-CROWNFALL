#pragma once

#include "CoreMinimal.h"
#include "GameFramework/HUD.h"
#include "LFHUD.generated.h"

UCLASS()
class LASTFRONTIER_API ALFHUD : public AHUD
{
    GENERATED_BODY()

public:
    virtual void DrawHUD() override;

private:
    // Avoid a world-wide actor lookup on every rendered frame.
    float LastEnemyCountRefreshSeconds = -1.0f;
    int32 CachedEnemyCount = 0;
    // Avoid showing victory before deferred enemy spawning has happened.
    bool bHasSeenEnemies = false;
};
