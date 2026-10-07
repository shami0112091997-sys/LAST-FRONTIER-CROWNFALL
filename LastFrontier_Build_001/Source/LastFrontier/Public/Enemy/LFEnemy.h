#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Character.h"
#include "LFEnemy.generated.h"

class UStaticMeshComponent;

UCLASS()
class LASTFRONTIER_API ALFEnemy : public ACharacter
{
    GENERATED_BODY()

public:
    ALFEnemy();

    virtual void Tick(float DeltaSeconds) override;
    virtual float TakeDamage(float DamageAmount, struct FDamageEvent const& DamageEvent, class AController* EventInstigator, AActor* DamageCauser) override;

protected:
    virtual void BeginPlay() override;

private:
    UPROPERTY(VisibleAnywhere, Category="Crownfall|Enemy")
    TObjectPtr<UStaticMeshComponent> ArmorBody;

    UPROPERTY(EditDefaultsOnly, Category="Crownfall|Enemy")
    float MaxHealth = 100.0f;

    UPROPERTY(EditDefaultsOnly, Category="Crownfall|Enemy")
    float ChaseSpeed = 330.0f;

    UPROPERTY(EditDefaultsOnly, Category="Crownfall|Enemy")
    float AttackRange = 155.0f;

    UPROPERTY(EditDefaultsOnly, Category="Crownfall|Enemy")
    float AttackDamage = 12.0f;

    float Health = 100.0f;
    float AttackCooldown = 0.0f;
};
