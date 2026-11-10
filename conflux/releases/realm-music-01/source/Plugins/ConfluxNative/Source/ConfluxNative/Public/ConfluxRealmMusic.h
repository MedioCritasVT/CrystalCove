#pragma once
#include "CoreMinimal.h"
#include "Subsystems/GameInstanceSubsystem.h"
#include "Tickable.h"
#include "UObject/SoftObjectPath.h"
#include "ConfluxRealmMusic.generated.h"
class UAudioComponent; class USoundWave; struct FStreamableHandle;
struct FConfluxSong { FString Title; FSoftObjectPath Asset; };
UCLASS()
class CONFLUXNATIVE_API UConfluxRealmMusic : public UGameInstanceSubsystem, public FTickableGameObject {
 GENERATED_BODY()
public:
 virtual void Initialize(FSubsystemCollectionBase& Collection) override;
 virtual void Deinitialize() override;
 virtual void Tick(float DeltaTime) override;
 virtual bool IsTickable() const override { return Running && !IsTemplate(); }
 virtual TStatId GetStatId() const override { RETURN_QUICK_DECLARE_CYCLE_STAT(UConfluxRealmMusic, STATGROUP_Tickables); }
 virtual UWorld* GetTickableGameObjectWorld() const override;
 UFUNCTION(BlueprintPure,meta=(WorldContext="Context")) static UConfluxRealmMusic* GetRealmMusic(const UObject* Context);
 UFUNCTION(BlueprintCallable) bool HandleCommand(const FString& Command);
 UFUNCTION(BlueprintCallable) FString Snapshot() const;
 bool GetMuted() const { return Muted; }
private:
 UPROPERTY() TArray<TObjectPtr<UAudioComponent>> Players;
 UPROPERTY() TMap<FString,TObjectPtr<USoundWave>> Waves;
 TMap<FString,FConfluxSong> Songs;
 TMap<FString,TArray<FString>> Playlists;
 TMap<FString,int32> Positions;
 TMap<FString,TSharedPtr<FStreamableHandle>> Handles;
 TSet<FString> Pending,Failed;
 FString Context,DesiredId,CurrentId,Status,PreferencesPath;
 bool Running=false,Muted=false,Writable=true,LoopPending=false;
 float Volume=.25f,FadeSeconds=6.f;
 int32 CurrentSlot=-1,TransitionCount=0;
 double Started=0,TransitionEnd=0,NextPublish=0,RetryAt=0;
 void Request(const FString& Id);
 bool BeginTrack(const FString& Id,double Now);
 void Publish(); void SavePreferences();
};
