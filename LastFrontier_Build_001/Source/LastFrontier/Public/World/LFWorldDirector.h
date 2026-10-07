#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "LFWorldDirector.generated.h"

class UStaticMesh;
class AStaticMeshActor;

UCLASS()
class LASTFRONTIER_API ALFWorldDirector : public AActor
{
    GENERATED_BODY()

public:
    ALFWorldDirector();

protected:
    virtual void BeginPlay() override;

private:
    UPROPERTY()
    TObjectPtr<UStaticMesh> CubeMesh;

    UPROPERTY()
    TObjectPtr<UStaticMesh> CylinderMesh;

    UPROPERTY()
    TObjectPtr<UStaticMesh> ConeMesh;

    UPROPERTY()
    TObjectPtr<UStaticMesh> SphereMesh;

    AStaticMeshActor* SpawnShape(
        UStaticMesh* Mesh,
        const FVector& Location,
        const FVector& Scale,
        const FRotator& Rotation = FRotator::ZeroRotator,
        const TCHAR* Label = TEXT("CrownfallShape"));

    void BuildGroundAndRoads();
    void BuildVictorianStronghold();
    void BuildIndustrialDistrict();
    void BuildLighting();
    void SpawnEnemies();
};
