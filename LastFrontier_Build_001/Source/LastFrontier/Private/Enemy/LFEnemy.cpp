#include "Enemy/LFEnemy.h"

#include "Character/LFCharacter.h"
#include "Components/CapsuleComponent.h"
#include "Components/StaticMeshComponent.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "Kismet/GameplayStatics.h"
#include "UObject/ConstructorHelpers.h"

ALFEnemy::ALFEnemy()
{
    PrimaryActorTick.bCanEverTick = true;

    GetCapsuleComponent()->InitCapsuleSize(44.0f, 92.0f);
    GetCharacterMovement()->MaxWalkSpeed = ChaseSpeed;
    GetCharacterMovement()->bOrientRotationToMovement = true;
    bUseControllerRotationYaw = false;

    ArmorBody = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("ArmorBody"));
    ArmorBody->SetupAttachment(GetCapsuleComponent());
    ArmorBody->SetRelativeLocation(FVector(0.0, 0.0, 0.0));
    ArmorBody->SetRelativeScale3D(FVector(0.75, 0.55, 1.7));
    ArmorBody->SetCollisionEnabled(ECollisionEnabled::NoCollision);

    static ConstructorHelpers::FObjectFinder<UStaticMesh> BodyAsset(TEXT("/Engine/BasicShapes/Cube.Cube"));
    if (BodyAsset.Succeeded())
    {
        ArmorBody->SetStaticMesh(BodyAsset.Object);
    }
}

void ALFEnemy::BeginPlay()
{
    Super::BeginPlay();
    Health = MaxHealth;
    GetCharacterMovement()->MaxWalkSpeed = ChaseSpeed;
}

void ALFEnemy::Tick(float DeltaSeconds)
{
    Super::Tick(DeltaSeconds);

    AttackCooldown = FMath::Max(0.0f, AttackCooldown - DeltaSeconds);

    ACharacter* Player = UGameplayStatics::GetPlayerCharacter(this, 0);
    if (!Player)
    {
        return;
    }

    FVector Delta = Player->GetActorLocation() - GetActorLocation();
    Delta.Z = 0.0f;
    const float Distance = Delta.Size();

    if (Distance > AttackRange)
    {
        AddMovementInput(Delta.GetSafeNormal(), 1.0f);
    }
    else if (AttackCooldown <= 0.0f)
    {
        UGameplayStatics::ApplyDamage(Player, AttackDamage, GetController(), this, UDamageType::StaticClass());
        AttackCooldown = 1.1f;
    }
}

float ALFEnemy::TakeDamage(float DamageAmount, FDamageEvent const& DamageEvent, AController* EventInstigator, AActor* DamageCauser)
{
    const float Applied = Super::TakeDamage(DamageAmount, DamageEvent, EventInstigator, DamageCauser);
    const float ActualDamage = Applied > 0.0f ? Applied : DamageAmount;

    Health -= ActualDamage;
    if (Health <= 0.0f)
    {
        Destroy();
    }

    return ActualDamage;
}
