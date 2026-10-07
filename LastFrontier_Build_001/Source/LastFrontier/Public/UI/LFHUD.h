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
};
