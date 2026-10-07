#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Character.h"
#include "LFCharacter.generated.h"

class UCameraComponent;
class USpringArmComponent;
class UStaticMeshComponent;

UCLASS()
class LASTFRONTIER_API ALFCharacter : public ACharacter
{
    GENERATED_BODY()

public:
    ALFCharacter();

    virtual void SetupPlayerInputComponent(class UInputComponent* PlayerInputComponent) override;
    virtual float TakeDamage(float DamageAmount, struct FDamageEvent const& DamageEvent, class AController* EventInstigator, AActor* DamageCauser) override;

    UFUNCTION(BlueprintPure, Category="Crownfall|Player")
    float GetHealth() const { return Health; }

protected:
    virtual void BeginPlay() override;

private:
    UPROPERTY(VisibleAnywhere, Category="Crownfall|Camera")
    TObjectPtr<USpringArmComponent> CameraBoom;

    UPROPERTY(VisibleAnywhere, Category="Crownfall|Camera")
    TObjectPtr<UCameraComponent> FollowCamera;

    UPROPERTY(VisibleAnywhere, Category="Crownfall|Visual")
    TObjectPtr<UStaticMeshComponent> PlayerBody;

    UPROPERTY(VisibleAnywhere, Category="Crownfall|Visual")
    TObjectPtr<UStaticMeshComponent> RifleBody;

    UPROPERTY(EditDefaultsOnly, Category="Crownfall|Combat")
    float MaxHealth = 100.0f;

    UPROPERTY(EditDefaultsOnly, Category="Crownfall|Combat")
    float FireDamage = 42.0f;

    UPROPERTY(EditDefaultsOnly, Category="Crownfall|Combat")
    float FireRange = 12000.0f;

    float Health = 100.0f;

    void MoveForward(float Value);
    void MoveRight(float Value);
    void Turn(float Value);
    void LookUp(float Value);
    void Fire();
    void TouchPressed(ETouchIndex::Type FingerIndex, FVector Location);
};
