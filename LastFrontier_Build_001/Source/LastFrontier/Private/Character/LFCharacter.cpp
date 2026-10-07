#include "Character/LFCharacter.h"

#include "Camera/CameraComponent.h"
#include "Components/CapsuleComponent.h"
#include "Components/InputComponent.h"
#include "Components/StaticMeshComponent.h"
#include "Engine/Engine.h"
#include "Engine/GameViewportClient.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "GameFramework/SpringArmComponent.h"
#include "Kismet/GameplayStatics.h"
#include "UObject/ConstructorHelpers.h"

ALFCharacter::ALFCharacter()
{
    PrimaryActorTick.bCanEverTick = false;

    GetCapsuleComponent()->InitCapsuleSize(44.0f, 96.0f);
    GetCharacterMovement()->MaxWalkSpeed = 540.0f;
    GetCharacterMovement()->JumpZVelocity = 620.0f;
    GetCharacterMovement()->AirControl = 0.3f;
    GetCharacterMovement()->bOrientRotationToMovement = false;

    bUseControllerRotationPitch = false;
    bUseControllerRotationRoll = false;
    bUseControllerRotationYaw = true;

    CameraBoom = CreateDefaultSubobject<USpringArmComponent>(TEXT("CameraBoom"));
    CameraBoom->SetupAttachment(GetCapsuleComponent());
    CameraBoom->TargetArmLength = 360.0f;
    CameraBoom->SocketOffset = FVector(0.0f, 65.0f, 70.0f);
    CameraBoom->bUsePawnControlRotation = true;
    CameraBoom->bEnableCameraLag = true;
    CameraBoom->CameraLagSpeed = 10.0f;

    FollowCamera = CreateDefaultSubobject<UCameraComponent>(TEXT("FollowCamera"));
    FollowCamera->SetupAttachment(CameraBoom, USpringArmComponent::SocketName);
    FollowCamera->bUsePawnControlRotation = false;

    PlayerBody = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("PlayerBody"));
    PlayerBody->SetupAttachment(GetCapsuleComponent());
    PlayerBody->SetRelativeLocation(FVector(0.0f, 0.0f, -5.0f));
    PlayerBody->SetRelativeScale3D(FVector(0.55f, 0.42f, 1.65f));
    PlayerBody->SetCollisionEnabled(ECollisionEnabled::NoCollision);

    RifleBody = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("RifleBody"));
    RifleBody->SetupAttachment(GetCapsuleComponent());
    RifleBody->SetRelativeLocation(FVector(45.0f, 38.0f, 30.0f));
    RifleBody->SetRelativeRotation(FRotator(0.0f, 0.0f, 0.0f));
    RifleBody->SetRelativeScale3D(FVector(0.85f, 0.10f, 0.10f));
    RifleBody->SetCollisionEnabled(ECollisionEnabled::NoCollision);

    static ConstructorHelpers::FObjectFinder<UStaticMesh> CubeAsset(TEXT("/Engine/BasicShapes/Cube.Cube"));
    if (CubeAsset.Succeeded())
    {
        PlayerBody->SetStaticMesh(CubeAsset.Object);
        RifleBody->SetStaticMesh(CubeAsset.Object);
    }
}

void ALFCharacter::BeginPlay()
{
    Super::BeginPlay();
    Health = MaxHealth;
}

void ALFCharacter::SetupPlayerInputComponent(UInputComponent* PlayerInputComponent)
{
    Super::SetupPlayerInputComponent(PlayerInputComponent);

    check(PlayerInputComponent);

    PlayerInputComponent->BindAxis(TEXT("MoveForward"), this, &ALFCharacter::MoveForward);
    PlayerInputComponent->BindAxis(TEXT("MoveRight"), this, &ALFCharacter::MoveRight);
    PlayerInputComponent->BindAxis(TEXT("Turn"), this, &ALFCharacter::Turn);
    PlayerInputComponent->BindAxis(TEXT("LookUp"), this, &ALFCharacter::LookUp);

    PlayerInputComponent->BindAction(TEXT("Jump"), IE_Pressed, this, &ACharacter::Jump);
    PlayerInputComponent->BindAction(TEXT("Jump"), IE_Released, this, &ACharacter::StopJumping);
    PlayerInputComponent->BindAction(TEXT("Fire"), IE_Pressed, this, &ALFCharacter::Fire);
    PlayerInputComponent->BindTouch(IE_Pressed, this, &ALFCharacter::TouchPressed);
}

void ALFCharacter::MoveForward(float Value)
{
    if (Controller && !FMath::IsNearlyZero(Value))
    {
        const FRotator ControlRotation = Controller->GetControlRotation();
        const FRotator YawRotation(0.0f, ControlRotation.Yaw, 0.0f);
        const FVector Direction = FRotationMatrix(YawRotation).GetUnitAxis(EAxis::X);
        AddMovementInput(Direction, Value);
    }
}

void ALFCharacter::MoveRight(float Value)
{
    if (Controller && !FMath::IsNearlyZero(Value))
    {
        const FRotator ControlRotation = Controller->GetControlRotation();
        const FRotator YawRotation(0.0f, ControlRotation.Yaw, 0.0f);
        const FVector Direction = FRotationMatrix(YawRotation).GetUnitAxis(EAxis::Y);
        AddMovementInput(Direction, Value);
    }
}

void ALFCharacter::Turn(float Value)
{
    AddControllerYawInput(Value);
}

void ALFCharacter::LookUp(float Value)
{
    AddControllerPitchInput(Value);
}

void ALFCharacter::Fire()
{
    if (!GetWorld() || !FollowCamera)
    {
        return;
    }

    const FVector Start = FollowCamera->GetComponentLocation();
    const FVector End = Start + FollowCamera->GetForwardVector() * FireRange;

    FHitResult Hit;
    FCollisionQueryParams Params(SCENE_QUERY_STAT(CrownfallFire), true, this);

    if (GetWorld()->LineTraceSingleByChannel(Hit, Start, End, ECC_Visibility, Params))
    {
        UGameplayStatics::ApplyPointDamage(
            Hit.GetActor(),
            FireDamage,
            FollowCamera->GetForwardVector(),
            Hit,
            GetController(),
            this,
            UDamageType::StaticClass());
    }
}

void ALFCharacter::TouchPressed(ETouchIndex::Type FingerIndex, FVector Location)
{
    if (!GEngine || !GEngine->GameViewport || !GEngine->GameViewport->Viewport)
    {
        return;
    }

    const FIntPoint Size = GEngine->GameViewport->Viewport->GetSizeXY();
    if (Size.X > 0 && Location.X > static_cast<float>(Size.X) * 0.62f)
    {
        Fire();
    }
}

float ALFCharacter::TakeDamage(float DamageAmount, FDamageEvent const& DamageEvent, AController* EventInstigator, AActor* DamageCauser)
{
    const float Applied = Super::TakeDamage(DamageAmount, DamageEvent, EventInstigator, DamageCauser);
    const float ActualDamage = Applied > 0.0f ? Applied : DamageAmount;

    Health -= ActualDamage;
    if (Health <= 0.0f)
    {
        Health = MaxHealth;
        SetActorLocation(FVector(0.0f, -3200.0f, 180.0f), false, nullptr, ETeleportType::TeleportPhysics);
        if (Controller)
        {
            Controller->SetControlRotation(FRotator::ZeroRotator);
        }
    }

    return ActualDamage;
}
