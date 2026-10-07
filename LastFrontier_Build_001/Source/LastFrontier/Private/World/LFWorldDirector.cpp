#include "World/LFWorldDirector.h"

#include "Enemy/LFEnemy.h"
#include "Engine/DirectionalLight.h"
#include "Engine/ExponentialHeightFog.h"
#include "Engine/PointLight.h"
#include "Engine/SkyLight.h"
#include "Engine/StaticMeshActor.h"
#include "Components/LightComponent.h"
#include "Components/StaticMeshComponent.h"
#include "UObject/ConstructorHelpers.h"

ALFWorldDirector::ALFWorldDirector()
{
    PrimaryActorTick.bCanEverTick = false;

    static ConstructorHelpers::FObjectFinder<UStaticMesh> CubeAsset(TEXT("/Engine/BasicShapes/Cube.Cube"));
    static ConstructorHelpers::FObjectFinder<UStaticMesh> CylinderAsset(TEXT("/Engine/BasicShapes/Cylinder.Cylinder"));
    static ConstructorHelpers::FObjectFinder<UStaticMesh> ConeAsset(TEXT("/Engine/BasicShapes/Cone.Cone"));
    static ConstructorHelpers::FObjectFinder<UStaticMesh> SphereAsset(TEXT("/Engine/BasicShapes/Sphere.Sphere"));

    CubeMesh = CubeAsset.Object;
    CylinderMesh = CylinderAsset.Object;
    ConeMesh = ConeAsset.Object;
    SphereMesh = SphereAsset.Object;
}

void ALFWorldDirector::BeginPlay()
{
    Super::BeginPlay();

    BuildGroundAndRoads();
    BuildVictorianStronghold();
    BuildIndustrialDistrict();
    BuildLighting();
    SpawnEnemies();
}

AStaticMeshActor* ALFWorldDirector::SpawnShape(
    UStaticMesh* Mesh,
    const FVector& Location,
    const FVector& Scale,
    const FRotator& Rotation,
    const TCHAR* Label)
{
    if (!Mesh || !GetWorld())
    {
        return nullptr;
    }

    FActorSpawnParameters Params;
    Params.SpawnCollisionHandlingOverride = ESpawnActorCollisionHandlingMethod::AlwaysSpawn;

    AStaticMeshActor* Actor = GetWorld()->SpawnActor<AStaticMeshActor>(Location, Rotation, Params);
    if (!Actor)
    {
        return nullptr;
    }

    Actor->Tags.Add(FName(Label));
    Actor->SetActorScale3D(Scale);

    UStaticMeshComponent* MeshComponent = Actor->GetStaticMeshComponent();
    MeshComponent->SetStaticMesh(Mesh);
    MeshComponent->SetMobility(EComponentMobility::Static);
    MeshComponent->SetCollisionEnabled(ECollisionEnabled::QueryAndPhysics);
    MeshComponent->SetCollisionResponseToAllChannels(ECR_Block);

    return Actor;
}

void ALFWorldDirector::BuildGroundAndRoads()
{
    // Main ground slab.
    SpawnShape(CubeMesh, FVector(0.0, 0.0, -30.0), FVector(70.0, 48.0, 0.3), FRotator::ZeroRotator, TEXT("CrownfallGround"));

    // Central boulevard and side streets.
    SpawnShape(CubeMesh, FVector(0.0, 0.0, 2.0), FVector(7.5, 47.0, 0.05), FRotator::ZeroRotator, TEXT("RoyalBoulevard"));
    SpawnShape(CubeMesh, FVector(-2800.0, 0.0, 2.0), FVector(3.0, 47.0, 0.05), FRotator::ZeroRotator, TEXT("WestStreet"));
    SpawnShape(CubeMesh, FVector(2800.0, 0.0, 2.0), FVector(3.0, 47.0, 0.05), FRotator::ZeroRotator, TEXT("EastStreet"));

    for (int32 Y = -3600; Y <= 3600; Y += 900)
    {
        SpawnShape(CubeMesh, FVector(0.0, static_cast<float>(Y), 5.0), FVector(62.0, 1.5, 0.08), FRotator::ZeroRotator, TEXT("CrossStreet"));
    }
}

void ALFWorldDirector::BuildVictorianStronghold()
{
    // Palace body.
    SpawnShape(CubeMesh, FVector(0.0, 2900.0, 500.0), FVector(16.0, 8.0, 5.0), FRotator::ZeroRotator, TEXT("CrownfallPalace"));
    SpawnShape(CubeMesh, FVector(0.0, 2900.0, 1050.0), FVector(9.0, 5.0, 1.0), FRotator::ZeroRotator, TEXT("PalaceUpper"));

    // Palace towers and pointed roofs.
    const float TowerX[] = {-1350.0f, 1350.0f};
    for (float X : TowerX)
    {
        SpawnShape(CylinderMesh, FVector(X, 2900.0, 650.0), FVector(3.0, 3.0, 6.5), FRotator::ZeroRotator, TEXT("PalaceTower"));
        SpawnShape(ConeMesh, FVector(X, 2900.0, 1425.0), FVector(3.6, 3.6, 3.2), FRotator::ZeroRotator, TEXT("PalaceSpire"));
    }

    // Defensive walls with a central gate.
    for (int32 X = -5400; X <= 5400; X += 900)
    {
        if (FMath::Abs(X) > 900)
        {
            SpawnShape(CubeMesh, FVector(static_cast<float>(X), 1900.0, 220.0), FVector(4.0, 1.2, 2.2), FRotator::ZeroRotator, TEXT("StrongholdWall"));
        }
    }

    SpawnShape(CubeMesh, FVector(-1200.0, 1900.0, 420.0), FVector(2.5, 2.5, 4.2), FRotator::ZeroRotator, TEXT("GateTower"));
    SpawnShape(CubeMesh, FVector(1200.0, 1900.0, 420.0), FVector(2.5, 2.5, 4.2), FRotator::ZeroRotator, TEXT("GateTower"));
    SpawnShape(CubeMesh, FVector(0.0, 1900.0, 740.0), FVector(10.0, 2.0, 1.2), FRotator::ZeroRotator, TEXT("GateBridge"));

    // Victorian city blocks.
    for (int32 Side = -1; Side <= 1; Side += 2)
    {
        for (int32 Row = -3; Row <= 2; ++Row)
        {
            const float X = Side * (1700.0f + (Row % 2 == 0 ? 350.0f : 0.0f));
            const float Y = Row * 900.0f;
            const float HeightScale = 2.8f + 0.35f * static_cast<float>((Row + 4) % 3);

            SpawnShape(CubeMesh, FVector(X, Y, HeightScale * 50.0f), FVector(8.0, 5.8, HeightScale), FRotator::ZeroRotator, TEXT("VictorianBlock"));
            SpawnShape(ConeMesh, FVector(X, Y, HeightScale * 100.0f + 220.0f), FVector(5.5, 4.0, 1.8), FRotator(0.0, 45.0, 0.0), TEXT("VictorianRoof"));
        }
    }
}

void ALFWorldDirector::BuildIndustrialDistrict()
{
    // Steam generator district on the west side.
    for (int32 I = 0; I < 4; ++I)
    {
        const float X = -3900.0f + I * 600.0f;
        const float Y = -2100.0f + (I % 2) * 550.0f;

        SpawnShape(CylinderMesh, FVector(X, Y, 250.0), FVector(2.2, 2.2, 5.0), FRotator::ZeroRotator, TEXT("SteamBoiler"));
        SpawnShape(CylinderMesh, FVector(X + 180.0f, Y + 140.0f, 620.0), FVector(0.65, 0.65, 7.0), FRotator::ZeroRotator, TEXT("SmokeStack"));
        SpawnShape(SphereMesh, FVector(X, Y, 560.0), FVector(2.35, 2.35, 1.1), FRotator::ZeroRotator, TEXT("BoilerCap"));
    }

    // Crates and barricades create combat cover.
    for (int32 I = 0; I < 12; ++I)
    {
        const float X = -2600.0f + static_cast<float>((I * 733) % 5200);
        const float Y = -2700.0f + static_cast<float>((I * 997) % 4300);
        SpawnShape(CubeMesh, FVector(X, Y, 90.0), FVector(1.8, 1.8, 1.8), FRotator(0.0, static_cast<float>((I * 31) % 180), 0.0), TEXT("CombatCrate"));
    }
}

void ALFWorldDirector::BuildLighting()
{
    if (!GetWorld())
    {
        return;
    }

    ADirectionalLight* Sun = GetWorld()->SpawnActor<ADirectionalLight>(FVector::ZeroVector, FRotator(-48.0, -35.0, 0.0));
    if (Sun && Sun->GetLightComponent())
    {
        Sun->GetLightComponent()->SetIntensity(6.0f);
        Sun->GetLightComponent()->SetLightColor(FLinearColor(1.0f, 0.78f, 0.58f));
    }

    ASkyLight* Sky = GetWorld()->SpawnActor<ASkyLight>();
    if (Sky && Sky->GetLightComponent())
    {
        Sky->GetLightComponent()->SetIntensity(0.75f);
    }

    AExponentialHeightFog* Fog = GetWorld()->SpawnActor<AExponentialHeightFog>();
    if (Fog && Fog->GetComponent())
    {
        Fog->GetComponent()->SetFogDensity(0.012f);
        Fog->GetComponent()->SetFogHeightFalloff(0.35f);
        Fog->GetComponent()->SetFogInscatteringColor(FLinearColor(0.10f, 0.16f, 0.20f));
    }

    // Warm gas lamps along the boulevard.
    for (int32 Y = -3000; Y <= 3000; Y += 750)
    {
        for (int32 Side = -1; Side <= 1; Side += 2)
        {
            const FVector LampLocation(900.0f * Side, static_cast<float>(Y), 320.0f);
            APointLight* Lamp = GetWorld()->SpawnActor<APointLight>(LampLocation, FRotator::ZeroRotator);
            if (Lamp && Lamp->GetLightComponent())
            {
                Lamp->GetLightComponent()->SetIntensity(2600.0f);
                Lamp->GetLightComponent()->SetAttenuationRadius(900.0f);
                Lamp->GetLightComponent()->SetLightColor(FLinearColor(1.0f, 0.50f, 0.18f));
            }
        }
    }
}

void ALFWorldDirector::SpawnEnemies()
{
    if (!GetWorld())
    {
        return;
    }

    const FVector EnemySpawns[] =
    {
        FVector(-1200.0, -2200.0, 140.0),
        FVector(1500.0, -1800.0, 140.0),
        FVector(-2400.0, 400.0, 140.0),
        FVector(2400.0, 700.0, 140.0),
        FVector(-1800.0, 1450.0, 140.0),
        FVector(1900.0, 1450.0, 140.0)
    };

    for (const FVector& Location : EnemySpawns)
    {
        GetWorld()->SpawnActor<ALFEnemy>(ALFEnemy::StaticClass(), Location, FRotator::ZeroRotator);
    }
}
