#pragma once
#include "CoreMinimal.h"
#include "Engine/GameInstance.h"
#include "LFGameInstance.generated.h"

UCLASS()
class LASTFRONTIER_API ULFGameInstance : public UGameInstance
{
    GENERATED_BODY()

public:
    // Future controlled builds can identify whether Unreal reached GameInstance.
    virtual void Init() override;
};
