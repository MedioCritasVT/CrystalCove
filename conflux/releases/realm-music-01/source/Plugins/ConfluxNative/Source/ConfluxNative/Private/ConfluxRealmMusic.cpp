#include "ConfluxRealmMusic.h"
#include "ConfluxSanctuary.h"
#include "Components/AudioComponent.h"
#include "Sound/SoundWave.h"
#include "Engine/AssetManager.h"
#include "Engine/StreamableManager.h"
#include "Engine/GameInstance.h"
#include "Kismet/GameplayStatics.h"
#include "Interfaces/IPluginManager.h"
#include "Misc/Paths.h"
#include "Misc/FileHelper.h"
#include "HAL/FileManager.h"
#include "Serialization/JsonSerializer.h"
namespace {
FString MusicJson(const TSharedRef<FJsonObject>& J){FString S;FJsonSerializer::Serialize(J,TJsonWriterFactory<>::Create(&S));return S;}
}
UConfluxRealmMusic* UConfluxRealmMusic::GetRealmMusic(const UObject* Context){auto* GI=UGameplayStatics::GetGameInstance(Context);return GI?GI->GetSubsystem<UConfluxRealmMusic>():nullptr;}
UWorld* UConfluxRealmMusic::GetTickableGameObjectWorld()const{return GetGameInstance()?GetGameInstance()->GetWorld():nullptr;}
void UConfluxRealmMusic::Initialize(FSubsystemCollectionBase& C){
 Super::Initialize(C);Players.SetNum(2);Running=true;Status=TEXT("Loading soundtrack configuration.");
 auto Plugin=IPluginManager::Get().FindPlugin(TEXT("ConfluxNative"));FString Text;TSharedPtr<FJsonObject> J;
 if(!Plugin||!FFileHelper::LoadFileToString(Text,*(Plugin->GetContentDir()/TEXT("BrowserUI/native/music-catalog.json")))||!FJsonSerializer::Deserialize(TJsonReaderFactory<>::Create(Text),J)||!J.IsValid()){Status=TEXT("Soundtrack configuration is unavailable.");return;}
 double Version=0;if(!J->TryGetNumberField(TEXT("version"),Version)||Version!=1){Status=TEXT("Soundtrack configuration version is unsupported.");return;}
 const TArray<TSharedPtr<FJsonValue>>* Tracks=nullptr;const TSharedPtr<FJsonObject>* Lists=nullptr;
 if(!J->TryGetArrayField(TEXT("tracks"),Tracks)||!J->TryGetObjectField(TEXT("playlists"),Lists)){Status=TEXT("Soundtrack configuration is incomplete.");return;}
 for(auto V:*Tracks){auto O=V->AsObject();if(!O.IsValid())continue;FConfluxSong S;FString Id,Asset;if(!O->TryGetStringField(TEXT("id"),Id)||!O->TryGetStringField(TEXT("title"),S.Title)||!O->TryGetStringField(TEXT("asset"),Asset)||!Asset.StartsWith(TEXT("/Game/Conflux/Audio/RealmMusic01/")))continue;S.Asset=FSoftObjectPath(Asset);Songs.Add(Id,S);}
 for(auto Pair:(*Lists)->Values){const TArray<TSharedPtr<FJsonValue>>* Values=nullptr;if(!Pair.Value->TryGetArray(Values))continue;TArray<FString> Ids;for(auto V:*Values){FString Id;if(V->TryGetString(Id)&&Songs.Contains(Id))Ids.Add(Id);}if(!Ids.IsEmpty())Playlists.Add(FString(Pair.Key.ToView()),Ids);}
 PreferencesPath=FPaths::ProjectSavedDir()/TEXT("MusicPreferences.json");FString PrefText;
 if(FPaths::FileExists(PreferencesPath)){
  TSharedPtr<FJsonObject> P;double V=0,N=0;bool M=false;
  if(!FFileHelper::LoadFileToString(PrefText,*PreferencesPath)||!FJsonSerializer::Deserialize(TJsonReaderFactory<>::Create(PrefText),P)||!P.IsValid()||!P->TryGetNumberField(TEXT("version"),V)||V!=1||!P->TryGetNumberField(TEXT("volume"),N)||!FMath::IsFinite(N)||N<0||N>1||!P->TryGetBoolField(TEXT("muted"),M)){Writable=false;Status=TEXT("Existing music preferences could not be read; preserved unchanged.");}else{Volume=N;Muted=M;}
 }
 if(Writable)Status=TEXT("Soundtrack ready; realm assignments are temporary.");
}
void UConfluxRealmMusic::Request(const FString& Id){
 if(Waves.Contains(Id)||Pending.Contains(Id)||Failed.Contains(Id)||!Songs.Contains(Id))return;
 Pending.Add(Id);TWeakObjectPtr<UConfluxRealmMusic> Weak(this);
 auto Handle=UAssetManager::GetStreamableManager().RequestAsyncLoad(Songs[Id].Asset,FStreamableDelegate::CreateLambda([Weak,Id](){
  if(auto* S=Weak.Get()){if(!S->Running)return;S->Pending.Remove(Id);S->Handles.Remove(Id);auto* Wave=Cast<USoundWave>(S->Songs[Id].Asset.ResolveObject());if(Wave)S->Waves.Add(Id,Wave);else{S->Failed.Add(Id);S->Status=TEXT("A soundtrack asset is unavailable; existing audio is retained.");}}
 }));
 if(Pending.Contains(Id))Handles.Add(Id,Handle);
}
bool UConfluxRealmMusic::BeginTrack(const FString& Id,double Now){
 auto Wave=Waves.FindRef(Id);if(!Wave)return false;
 const int32 Slot=CurrentSlot==0?1:0;
 if(Players[Slot]){Players[Slot]->Stop();Players[Slot]->DestroyComponent();Players[Slot]=nullptr;}
 auto* P=UGameplayStatics::CreateSound2D(GetTickableGameObjectWorld(),Wave,1,1,0,nullptr,true,false);
 if(!P){Status=TEXT("Audio output is unavailable; playback has not started.");RetryAt=Now+5;return false;}
 Players[Slot]=P;P->SetUISound(true);P->bAutoDestroy=false;
 const float Gain=Muted?0.f:Volume;
 if(CurrentSlot>=0&&Players[CurrentSlot])Players[CurrentSlot]->FadeOut(FadeSeconds,0,EAudioFaderCurve::Sin);
 P->FadeIn(FadeSeconds,Gain,0,EAudioFaderCurve::Sin);
 CurrentSlot=Slot;CurrentId=Id;Started=Now;TransitionEnd=Now+FadeSeconds;LoopPending=false;TransitionCount++;Status=TEXT("Playing; realm assignments are temporary.");return true;
}
void UConfluxRealmMusic::Tick(float DeltaTime){
 auto* W=GetTickableGameObjectWorld();if(!W||Songs.IsEmpty())return;auto* G=Cast<AConfluxSanctuary>(W->GetAuthGameMode());if(!G)return;
 const double Now=FPlatformTime::Seconds();static const TCHAR* Nodes[]={TEXT("medio"),TEXT("ratio"),TEXT("specula"),TEXT("nexus"),TEXT("limen")};
 const FString Next=G->FrontEndActive?TEXT("title"):!G->FantasyWorld?TEXT("developer"):Nodes[FMath::Clamp(G->RealmNodeIndex(),0,4)];
 if(Next!=Context){Context=Next;LoopPending=false;auto* List=Playlists.Find(Context);DesiredId=List&&!List->IsEmpty()?(*List)[Positions.FindOrAdd(Context)%List->Num()]:FString();}
 if(DesiredId.IsEmpty()){Status=TEXT("No soundtrack assigned to this context.");return;}
 Request(DesiredId);
 if(CurrentSlot>=0&&CurrentId==DesiredId&&!LoopPending&&Now>=TransitionEnd){
  auto Wave=Waves.FindRef(CurrentId);const double Duration=Wave?Wave->GetDuration():0;
  if(Duration>FadeSeconds+1&&Now-Started>=Duration-FadeSeconds){
   auto* List=Playlists.Find(Context);if(List&&!List->IsEmpty()){int32& Position=Positions.FindOrAdd(Context);Position=(Position+1)%List->Num();DesiredId=(*List)[Position];LoopPending=true;Request(DesiredId);}
  }
 }
 // Two voices maximum. Rapid swaps coalesce to the latest request and wait for
 // the current envelope to finish; no third voice or audible hard-stop is used.
 if(Now>=TransitionEnd&&Now>=RetryAt&&(CurrentId!=DesiredId||LoopPending||CurrentSlot<0))BeginTrack(DesiredId,Now);
 if(Now>=NextPublish){NextPublish=Now+.5;Publish();}
}
void UConfluxRealmMusic::SavePreferences(){
 if(!Writable){Status=TEXT("Music adjusted for this session; unreadable preferences preserved.");return;}
 auto J=MakeShared<FJsonObject>();J->SetNumberField(TEXT("version"),1);J->SetNumberField(TEXT("volume"),Volume);J->SetBoolField(TEXT("muted"),Muted);const FString Text=MusicJson(J),Temp=PreferencesPath+TEXT(".pending");FString Check;
 if(!IFileManager::Get().MakeDirectory(*FPaths::GetPath(PreferencesPath),true)||!FFileHelper::SaveStringToFile(Text,*Temp)||!FFileHelper::LoadFileToString(Check,*Temp)||Check!=Text||!IFileManager::Get().Move(*PreferencesPath,*Temp,true,true)){Status=TEXT("Music preference save failed; current session settings remain active.");}
}
bool UConfluxRealmMusic::HandleCommand(const FString& A){
 if(!A.StartsWith(TEXT("music:")))return false;
 if(A==TEXT("music:status")){Publish();return true;}
 if(A.StartsWith(TEXT("music:volume:"))){const FString Value=A.Mid(13);float N;if(!LexTryParseString(N,*Value)||!FMath::IsFinite(N)||N<0||N>1){Status=TEXT("Choose a music volume between 0 and 100 percent.");Publish();return true;}Volume=N;}
 else if(A==TEXT("music:mute:1"))Muted=true;else if(A==TEXT("music:mute:0"))Muted=false;else return true;
 const double Now=FPlatformTime::Seconds();for(int32 I=0;I<Players.Num();I++)if(Players[I])Players[I]->AdjustVolume(FMath::Max(.75f,float(TransitionEnd-Now)),I==CurrentSlot&&!Muted?Volume:0,EAudioFaderCurve::Sin);
 TransitionEnd=FMath::Max(TransitionEnd,Now+.75);SavePreferences();Publish();return true;
}
FString UConfluxRealmMusic::Snapshot()const{
 auto J=MakeShared<FJsonObject>();J->SetStringField(TEXT("context"),Context);J->SetStringField(TEXT("currentId"),CurrentId);J->SetStringField(TEXT("desiredId"),DesiredId);J->SetStringField(TEXT("title"),Songs.Contains(CurrentId)?Songs[CurrentId].Title:TEXT("Not playing"));J->SetStringField(TEXT("status"),Status);J->SetBoolField(TEXT("muted"),Muted);J->SetBoolField(TEXT("preferencesWritable"),Writable);J->SetNumberField(TEXT("volume"),Volume);J->SetNumberField(TEXT("fadeSeconds"),FadeSeconds);J->SetNumberField(TEXT("transitionCount"),TransitionCount);J->SetBoolField(TEXT("transitioning"),FPlatformTime::Seconds()<TransitionEnd);J->SetNumberField(TEXT("loadedTracks"),Waves.Num());J->SetNumberField(TEXT("pendingLoads"),Pending.Num());J->SetNumberField(TEXT("failedLoads"),Failed.Num());int Active=0;for(auto P:Players)if(P&&P->IsPlaying())Active++;J->SetNumberField(TEXT("activeVoices"),Active);J->SetBoolField(TEXT("queued"),CurrentId!=DesiredId);return MusicJson(J);
}
void UConfluxRealmMusic::Publish(){if(auto* W=GetTickableGameObjectWorld())if(auto* G=Cast<AConfluxSanctuary>(W->GetAuthGameMode()))G->EvaluateInterface(TEXT("window.confluxMusicState?.(")+Snapshot()+TEXT(");"));}
void UConfluxRealmMusic::Deinitialize(){Running=false;for(auto Pair:Handles)if(Pair.Value)Pair.Value->CancelHandle();Handles.Empty();for(auto P:Players)if(IsValid(P.Get())){P->Stop();P->DestroyComponent();}Players.Empty();Waves.Empty();Super::Deinitialize();}
