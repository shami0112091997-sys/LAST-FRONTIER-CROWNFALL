#include "UI/LFHUD.h"

#include "Character/LFCharacter.h"
#include "Enemy/LFEnemy.h"
#include "Engine/Canvas.h"
#include "Engine/Engine.h"
#include "Engine/Font.h"
#include "Kismet/GameplayStatics.h"

void ALFHUD::DrawHUD()
{
    Super::DrawHUD();

    if (!Canvas)
    {
        return;
    }

    const float CX = Canvas->ClipX * 0.5f;
    const float CY = Canvas->ClipY * 0.5f;

    // Crosshair.
    const FLinearColor CrosshairColor(0.95f, 0.72f, 0.28f, 1.0f);
    DrawLine(CX - 10.0f, CY, CX + 10.0f, CY, CrosshairColor, 2.0f);
    DrawLine(CX, CY - 10.0f, CX, CY + 10.0f, CrosshairColor, 2.0f);

    UFont* Font = GEngine ? GEngine->GetSmallFont() : nullptr;
    if (!Font)
    {
        return;
    }

    ALFCharacter* Player = Cast<ALFCharacter>(UGameplayStatics::GetPlayerCharacter(this, 0));

    TArray<AActor*> Enemies;
    UGameplayStatics::GetAllActorsOfClass(this, ALFEnemy::StaticClass(), Enemies);

    const FString Title = TEXT("LAST FRONTIER: CROWNFALL  |  UNREAL FIRST PLAYABLE");
    DrawText(Title, FLinearColor(0.95f, 0.72f, 0.28f, 1.0f), 32.0f, 28.0f, Font, 1.25f, false);

    const FString Status = FString::Printf(
        TEXT("HP %d / 100     Enemies %d     Objective: clear the Royal District"),
        Player ? FMath::RoundToInt(Player->GetHealth()) : 0,
        Enemies.Num());
    DrawText(Status, FLinearColor::White, 32.0f, 62.0f, Font, 1.0f, false);

    DrawText(TEXT("Move: WASD / left stick   Look: mouse / right stick   Fire: LMB / trigger / tap right side"),
        FLinearColor(0.72f, 0.82f, 0.88f, 1.0f), 32.0f, Canvas->ClipY - 46.0f, Font, 0.9f, false);

    if (Enemies.Num() == 0)
    {
        DrawText(TEXT("ROYAL DISTRICT SECURED"),
            FLinearColor(0.95f, 0.72f, 0.28f, 1.0f), CX - 145.0f, CY - 90.0f, Font, 1.6f, false);
    }
}
