#define WIN32_LEAN_AND_MEAN
#define NOMINMAX
#include <windows.h>
#include <mmsystem.h>
#include <bcrypt.h>
#include <shellapi.h>
#include <xinput.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include <vector>
#include <string>
#include <fstream>
#include <filesystem>
#include <iterator>
#include <algorithm>
#include <stdexcept>
#include <array>
#include <cmath>
#include "libretro.h"
#include "gamepad_mapping.h"
static HMODULE core;
static HWND window;
static HWAVEOUT audioDevice;
static std::vector<uint32_t> pixels;
static unsigned videoWidth=320,videoHeight=224,pixelFormat=RETRO_PIXEL_FORMAT_RGB565;
static bool running=true,manualPause=false,focused=true,fullscreen=false;
static std::array<bool,256> heldKeys{};
static std::string baseDir;
static double fps=59.922743;
static unsigned sampleRate=44100;
static unsigned frameNumber;
static uint64_t videoHash=14695981039346656037ull,audioHash=14695981039346656037ull;
static bool headless=false,diagnostics=false;
static unsigned videoCalls=0,audioCalls=0;
static void (*initCore)();static void (*runCore)();static void (*unloadCore)();static void (*deinitCore)();static void (*resetCore)();
static bool (*loadGame)(const retro_game_info*);static void(*avInfo)(retro_system_av_info*);static uint64_t(*nativeCount)();
static WINDOWPLACEMENT normalWindow={sizeof(WINDOWPLACEMENT)};
static std::array<WAVEHDR,12> audioHeaders{};
static std::array<std::array<int16_t,8192>,12> audioData{};
static unsigned audioIndex;
static HMODULE gamepadLibrary;
static DWORD (WINAPI *getPadState)(DWORD,XINPUT_STATE*);
static bool gamepadInitialized=false,gamepadConnected=false;
static DWORD gamepadSlot=XUSER_MAX_COUNT;
static ULONGLONG nextGamepadScan=0;
static uint16_t gamepadMask=0;
static void initGamepad(){
 if(gamepadInitialized)return;gamepadInitialized=true;
 for(const wchar_t*name:{L"xinput1_4.dll",L"xinput9_1_0.dll",L"xinput1_3.dll"}){
  gamepadLibrary=LoadLibraryExW(name,nullptr,LOAD_LIBRARY_SEARCH_SYSTEM32);
  if(!gamepadLibrary)continue;
  getPadState=reinterpret_cast<decltype(getPadState)>(GetProcAddress(gamepadLibrary,"XInputGetState"));
  if(getPadState)return;FreeLibrary(gamepadLibrary);gamepadLibrary=nullptr;
 }
}
static void readGamepad(ULONGLONG now){
 gamepadMask=0;
 if(!getPadState){gamepadConnected=false;return;}
 XINPUT_STATE state={};
 if(gamepadSlot<XUSER_MAX_COUNT){
  if(getPadState(gamepadSlot,&state)==ERROR_SUCCESS){
   gamepadConnected=true;auto&g=state.Gamepad;gamepadMask=xboxMask(g.wButtons,g.sThumbLX,g.sThumbLY,g.bLeftTrigger,g.bRightTrigger);return;
  }
  gamepadSlot=XUSER_MAX_COUNT;gamepadConnected=false;nextGamepadScan=now;
 }
 if(now<nextGamepadScan)return;nextGamepadScan=now+500;
 for(DWORD slot=0;slot<XUSER_MAX_COUNT;++slot){
  if(getPadState(slot,&state)==ERROR_SUCCESS){
   gamepadSlot=slot;gamepadConnected=true;auto&g=state.Gamepad;gamepadMask=xboxMask(g.wButtons,g.sThumbLX,g.sThumbLY,g.bLeftTrigger,g.bRightTrigger);return;
  }
 }
 gamepadConnected=false;
}
static void hashBytes(uint64_t& value,const void*ptr,size_t len){auto b=(const uint8_t*)ptr;for(size_t i=0;i<len;++i){value^=b[i];value*=1099511628211ull;}}
static bool environment(unsigned cmd,void*data){
 switch(cmd){
 case RETRO_ENVIRONMENT_GET_SYSTEM_DIRECTORY:case RETRO_ENVIRONMENT_GET_SAVE_DIRECTORY:case RETRO_ENVIRONMENT_GET_CONTENT_DIRECTORY:
  *(const char**)data=baseDir.c_str();return true;
 case RETRO_ENVIRONMENT_SET_PIXEL_FORMAT:pixelFormat=*(unsigned*)data;return pixelFormat==RETRO_PIXEL_FORMAT_RGB565||pixelFormat==RETRO_PIXEL_FORMAT_0RGB1555;
 case RETRO_ENVIRONMENT_GET_VARIABLE_UPDATE:*(bool*)data=false;return true;
 case RETRO_ENVIRONMENT_SET_ROTATION:case RETRO_ENVIRONMENT_SET_INPUT_DESCRIPTORS:case RETRO_ENVIRONMENT_SET_VARIABLES:
 case RETRO_ENVIRONMENT_SET_SUPPORT_NO_GAME:case RETRO_ENVIRONMENT_SET_SYSTEM_AV_INFO:case RETRO_ENVIRONMENT_SET_CONTROLLER_INFO:
 case RETRO_ENVIRONMENT_SET_GEOMETRY:case RETRO_ENVIRONMENT_SET_SERIALIZATION_QUIRKS:case RETRO_ENVIRONMENT_SET_SUPPORT_ACHIEVEMENTS:
 case RETRO_ENVIRONMENT_SET_CORE_OPTIONS_DISPLAY:case RETRO_ENVIRONMENT_SET_MINIMUM_AUDIO_LATENCY:case RETRO_ENVIRONMENT_SET_CONTENT_INFO_OVERRIDE:
 return true;
 default:return false;
 }
}
static void video(const void*ptr,unsigned w,unsigned h,size_t pitch){
 if(!ptr)return;videoWidth=w;videoHeight=h;++videoCalls;
 if(headless){for(unsigned y=0;y<h;++y)hashBytes(videoHash,(const uint8_t*)ptr+y*pitch,w*2);return;}
 pixels.resize(size_t(w)*h);
 for(unsigned y=0;y<h;++y){auto row=(const uint16_t*)((const uint8_t*)ptr+y*pitch);
  for(unsigned x=0;x<w;++x){unsigned v=row[x];unsigned r,g,b;
   if(pixelFormat==RETRO_PIXEL_FORMAT_RGB565){r=((v>>11)&31)*255/31;g=((v>>5)&63)*255/63;b=(v&31)*255/31;}
   else{r=((v>>10)&31)*255/31;g=((v>>5)&31)*255/31;b=(v&31)*255/31;}
   pixels[size_t(y)*w+x]=(r<<16)|(g<<8)|b;
  }
 }
}
static size_t audioBatch(const int16_t*data,size_t frames){
 ++audioCalls;
 if(headless){hashBytes(audioHash,data,frames*4);return frames;}
 if(!audioDevice||frames>4096)return frames;
 auto&header=audioHeaders[audioIndex];
 if(header.dwFlags&WHDR_PREPARED){if(!(header.dwFlags&WHDR_DONE))return frames;waveOutUnprepareHeader(audioDevice,&header,sizeof(header));}
 memcpy(audioData[audioIndex].data(),data,frames*4);header={};header.lpData=(LPSTR)audioData[audioIndex].data();header.dwBufferLength=DWORD(frames*4);
 if(waveOutPrepareHeader(audioDevice,&header,sizeof(header))==MMSYSERR_NOERROR)waveOutWrite(audioDevice,&header,sizeof(header));
 audioIndex=(audioIndex+1)%audioHeaders.size();return frames;
}
static void audioSample(int16_t l,int16_t r){int16_t data[2]={l,r};audioBatch(data,1);}
static void pollInput(){if(headless)return;initGamepad();readGamepad(GetTickCount64());}
static bool key(int vk){return vk>=0&&vk<256&&heldKeys[size_t(vk)];}
static int16_t input(unsigned port,unsigned device,unsigned index,unsigned id){
 (void)index;if(port||device!=RETRO_DEVICE_JOYPAD)return 0;
 if(headless){
  if(id==3)return (frameNumber>=300&&frameNumber<304)||(frameNumber>=420&&frameNumber<424);
  if(id==0)return frameNumber>480&&(frameNumber%180)<60;
  if(id==1)return frameNumber>480&&(frameNumber%60)<30;
  if(id==8)return frameNumber>480&&(frameNumber%80)<30;
  return 0;
 }
 if(!focused)return 0;
 if(id<16&&(gamepadMask&(1u<<id)))return 1;
 switch(id){case RETRO_DEVICE_ID_JOYPAD_Y:return key('Z');case RETRO_DEVICE_ID_JOYPAD_B:return key('X');case RETRO_DEVICE_ID_JOYPAD_A:return key('C');
 case RETRO_DEVICE_ID_JOYPAD_START:return key(VK_RETURN);case RETRO_DEVICE_ID_JOYPAD_UP:return key(VK_UP);case RETRO_DEVICE_ID_JOYPAD_DOWN:return key(VK_DOWN);
 case RETRO_DEVICE_ID_JOYPAD_LEFT:return key(VK_LEFT);case RETRO_DEVICE_ID_JOYPAD_RIGHT:return key(VK_RIGHT);default:return 0;}
}
static void paint(HDC dc){
 RECT r;GetClientRect(window,&r);FillRect(dc,&r,(HBRUSH)GetStockObject(BLACK_BRUSH));
 const int footer=fullscreen?0:38;int availW=r.right,availH=std::max(1,int(r.bottom)-footer);
 int drawW=availW,drawH=drawW*3/4;if(drawH>availH){drawH=availH;drawW=drawH*4/3;}
 int x=(availW-drawW)/2,y=(availH-drawH)/2;
 if(!pixels.empty()){BITMAPINFO info={};info.bmiHeader.biSize=sizeof(BITMAPINFOHEADER);info.bmiHeader.biWidth=LONG(videoWidth);info.bmiHeader.biHeight=-LONG(videoHeight);info.bmiHeader.biPlanes=1;info.bmiHeader.biBitCount=32;info.bmiHeader.biCompression=BI_RGB;
  SetStretchBltMode(dc,COLORONCOLOR);StretchDIBits(dc,x,y,drawW,drawH,0,0,videoWidth,videoHeight,pixels.data(),&info,DIB_RGB_COLORS,SRCCOPY);}
 if(footer){SetBkMode(dc,TRANSPARENT);SetTextColor(dc,RGB(220,220,220));RECT text={12,r.bottom-footer,availW-12,r.bottom};
  const char*help=(manualPause||!focused)?"PAUSED   |   P resumes   |   Z / X / C = Genesis A / B / C":
   gamepadConnected?"Xbox connected  |  X / A / B: Genesis A / B / C  |  LB / RB: A / C  |  Menu: Start  |  D-pad or left stick  |  Keys also work":
   "Enter: Start   |   Z / X / C: A / B / C   |   Arrows: D-pad   |   Xbox controller: auto-detect   |   P: Pause   F11: Fullscreen";
  DrawTextA(dc,help,-1,&text,DT_SINGLELINE|DT_VCENTER|DT_CENTER);}
}
static void toggleFullscreen(){
 fullscreen=!fullscreen;
 if(fullscreen){GetWindowPlacement(window,&normalWindow);MONITORINFO monitor={sizeof(MONITORINFO)};GetMonitorInfo(MonitorFromWindow(window,MONITOR_DEFAULTTOPRIMARY),&monitor);
  SetWindowLongPtr(window,GWL_STYLE,WS_POPUP|WS_VISIBLE);SetWindowPos(window,HWND_TOP,monitor.rcMonitor.left,monitor.rcMonitor.top,monitor.rcMonitor.right-monitor.rcMonitor.left,monitor.rcMonitor.bottom-monitor.rcMonitor.top,SWP_FRAMECHANGED);}
 else{SetWindowLongPtr(window,GWL_STYLE,WS_OVERLAPPEDWINDOW|WS_VISIBLE);SetWindowPlacement(window,&normalWindow);SetWindowPos(window,nullptr,0,0,0,0,SWP_NOMOVE|SWP_NOSIZE|SWP_NOZORDER|SWP_FRAMECHANGED);}
}
static LRESULT CALLBACK windowProc(HWND w,UINT msg,WPARAM wp,LPARAM lp){
 switch(msg){case WM_DESTROY:running=false;PostQuitMessage(0);return 0;
 case WM_ACTIVATEAPP:focused=wp!=0;if(!focused)heldKeys.fill(false);return 0;
 case WM_KEYUP:if(wp<256)heldKeys[size_t(wp)]=false;return 0;
 case WM_KEYDOWN:if(wp<256)heldKeys[size_t(wp)]=true;if(!(lp&(1L<<30))){if(wp==VK_ESCAPE){DestroyWindow(w);return 0;}if(wp=='P')manualPause=!manualPause;if(wp==VK_F11)toggleFullscreen();if(wp==VK_F5){resetCore();if(audioDevice)waveOutReset(audioDevice);}}return 0;
 case WM_ERASEBKGND:return 1;
 case WM_PAINT:{PAINTSTRUCT ps;HDC dc=BeginPaint(w,&ps);paint(dc);EndPaint(w,&ps);return 0;}
 }return DefWindowProc(w,msg,wp,lp);
}
static void checkRom(const std::string&path){
 std::ifstream f(std::filesystem::u8path(path),std::ios::binary);if(!f)throw std::runtime_error("ROM not found. Put game.md beside DevilCrash.exe, or drag your unzipped MD ROM onto the executable.");
 std::vector<uint8_t> rom((std::istreambuf_iterator<char>(f)),{});if(rom.size()!=524288)throw std::runtime_error("This build requires the supplied 512 KB Japanese ROM.");
 BCRYPT_ALG_HANDLE alg=nullptr;BCRYPT_HASH_HANDLE hash=nullptr;DWORD size=0,got=0;std::array<uint8_t,32> digest{};
 if(BCryptOpenAlgorithmProvider(&alg,BCRYPT_SHA256_ALGORITHM,nullptr,0)<0)throw std::runtime_error("SHA256 provider unavailable.");
 BCryptGetProperty(alg,BCRYPT_OBJECT_LENGTH,(PUCHAR)&size,sizeof(size),&got,0);std::vector<uint8_t> object(size);
 NTSTATUS status=BCryptCreateHash(alg,&hash,object.data(),size,nullptr,0,0);
 if(status>=0)status=BCryptHashData(hash,rom.data(),ULONG(rom.size()),0);
 if(status>=0)status=BCryptFinishHash(hash,digest.data(),digest.size(),0);
 if(hash)BCryptDestroyHash(hash);BCryptCloseAlgorithmProvider(alg,0);
 static const uint8_t expected[]={0x9e,0x97,0x34,0xa2,0x90,0x4d,0x61,0xd2,0x75,0x85,0x49,0x6e,0xda,0xd8,0x30,0xe3,0x29,0xdd,0x6b,0xfe,0x4e,0x58,0x59,0xc1,0x15,0x35,0x53,0x20,0x46,0xd0,0x72,0x62};
 if(status<0||memcmp(digest.data(),expected,32))throw std::runtime_error("Unsupported ROM revision. Use Devil Crash MD (Japan) from your uploaded archive.");
}
template<class T>static T proc(const char*name){auto p=GetProcAddress(core,name);if(!p)throw std::runtime_error(std::string("Missing compatibility function: ")+name);return reinterpret_cast<T>(p);}
int WINAPI WinMain(HINSTANCE instance,HINSTANCE,LPSTR,int show){
 try{
  wchar_t exe[32768];GetModuleFileNameW(nullptr,exe,32768);int exeLen=WideCharToMultiByte(CP_UTF8,0,exe,-1,nullptr,0,nullptr,nullptr);std::vector<char> exeUtf8(exeLen);WideCharToMultiByte(CP_UTF8,0,exe,-1,exeUtf8.data(),exeLen,nullptr,nullptr);baseDir=exeUtf8.data();baseDir=baseDir.substr(0,baseDir.find_last_of("\\/"));
  int count=0;LPWSTR*args=CommandLineToArgvW(GetCommandLineW(),&count);std::string romPath=baseDir+"\\game.md";unsigned selftestFrames=1800;
  for(int i=1;i<count;++i){if(wcscmp(args[i],L"--diagnostics")==0){diagnostics=true;continue;}if(wcsncmp(args[i],L"--selftest",10)==0){headless=true;if(args[i][10]==L'=')selftestFrames=unsigned(_wtoi(args[i]+11));}
   else{int n=WideCharToMultiByte(CP_UTF8,0,args[i],-1,nullptr,0,nullptr,nullptr);std::vector<char> path(n);WideCharToMultiByte(CP_UTF8,0,args[i],-1,path.data(),n,nullptr,nullptr);romPath=path.data();}}
  LocalFree(args);checkRom(romPath);
  std::string dllPath=baseDir+"\\devil-native.dll";int dllLen=MultiByteToWideChar(CP_UTF8,0,dllPath.c_str(),-1,nullptr,0);std::vector<wchar_t> dllWide(dllLen);MultiByteToWideChar(CP_UTF8,0,dllPath.c_str(),-1,dllWide.data(),dllLen);core=LoadLibraryW(dllWide.data());if(!core)throw std::runtime_error("Could not load devil-native.dll. Keep it beside DevilCrash.exe.");
  proc<void(*)(retro_environment_t)>("retro_set_environment")(environment);proc<void(*)(retro_video_refresh_t)>("retro_set_video_refresh")(video);
  proc<void(*)(retro_audio_sample_t)>("retro_set_audio_sample")(audioSample);proc<void(*)(retro_audio_sample_batch_t)>("retro_set_audio_sample_batch")(audioBatch);
  proc<void(*)(retro_input_poll_t)>("retro_set_input_poll")(pollInput);proc<void(*)(retro_input_state_t)>("retro_set_input_state")(input);
  initCore=proc<void(*)()>("retro_init");runCore=proc<void(*)()>("retro_run");unloadCore=proc<void(*)()>("retro_unload_game");deinitCore=proc<void(*)()>("retro_deinit");resetCore=proc<void(*)()>("retro_reset");
  loadGame=proc<bool(*)(const retro_game_info*)>("retro_load_game");avInfo=proc<void(*)(retro_system_av_info*)>("retro_get_system_av_info");nativeCount=proc<uint64_t(*)()>("retro_native_instructions");
  initCore();retro_game_info game={romPath.c_str(),nullptr,0,nullptr};if(!loadGame(&game))throw std::runtime_error("The compatibility runtime could not load the ROM.");
  retro_system_av_info av={};avInfo(&av);fps=av.timing.fps;sampleRate=unsigned(av.timing.sample_rate);
  std::ofstream diagnostic;if(diagnostics){diagnostic.open(std::filesystem::u8path(baseDir+"\\player-diagnostics.txt"));diagnostic<<"fps="<<fps<<" rate="<<sampleRate<<"\n";diagnostic.flush();}
  if(headless){for(frameNumber=0;frameNumber<selftestFrames;++frameNumber)runCore();std::ofstream f(std::filesystem::u8path(baseDir+"\\selftest.txt"));f<<"frames="<<selftestFrames<<"\nvideo_callbacks="<<videoCalls<<"\naudio_callbacks="<<audioCalls<<"\nvideo_fnv64="<<std::hex<<videoHash<<"\naudio_fnv64="<<audioHash<<std::dec<<"\nnative_instructions="<<nativeCount()<<"\n";if(!f)throw std::runtime_error("Could not write selftest.txt.");unloadCore();deinitCore();return nativeCount()>0&&videoCalls>0?0:1;}
  WNDCLASSA wc={};wc.lpfnWndProc=windowProc;wc.hInstance=instance;wc.lpszClassName="DevilCrashNativeWindow";wc.hCursor=LoadCursor(nullptr,IDC_ARROW);RegisterClassA(&wc);
  RECT rect={0,0,960,758};AdjustWindowRect(&rect,WS_OVERLAPPEDWINDOW,FALSE);
  window=CreateWindowA(wc.lpszClassName,"Devil Crash MD - native instruction build",WS_OVERLAPPEDWINDOW,CW_USEDEFAULT,CW_USEDEFAULT,rect.right-rect.left,rect.bottom-rect.top,nullptr,nullptr,instance,nullptr);
  if(!window)throw std::runtime_error("Could not create the game window.");ShowWindow(window,show);SetForegroundWindow(window);SetFocus(window);UpdateWindow(window);
  WAVEFORMATEX format={};format.wFormatTag=WAVE_FORMAT_PCM;format.nChannels=2;format.nSamplesPerSec=sampleRate;format.wBitsPerSample=16;format.nBlockAlign=4;format.nAvgBytesPerSec=sampleRate*4;
  waveOutOpen(&audioDevice,WAVE_MAPPER,&format,0,0,CALLBACK_NULL);timeBeginPeriod(1);
  LARGE_INTEGER frequency,now;QueryPerformanceFrequency(&frequency);QueryPerformanceCounter(&now);double next=double(now.QuadPart),period=double(frequency.QuadPart)/fps;bool wasPaused=false;
  while(running){MSG msg;while(PeekMessage(&msg,nullptr,0,0,PM_REMOVE)){if(msg.message==WM_QUIT)running=false;TranslateMessage(&msg);DispatchMessage(&msg);}if(!running)break;
   bool paused=manualPause||!focused;if(paused!=wasPaused){if(audioDevice){if(paused)waveOutPause(audioDevice);else waveOutRestart(audioDevice);}wasPaused=paused;InvalidateRect(window,nullptr,FALSE);}
   QueryPerformanceCounter(&now);double current=double(now.QuadPart);
   if(paused){next=current+period;Sleep(10);continue;}
   if(current<next){Sleep(1);continue;}
   // Preserve every game frame; reset the host deadline after an extended stall.
   if(current-next>period*4)next=current;
   runCore();++frameNumber;if(diagnostics&&frameNumber%60==0){diagnostic<<"frame="<<frameNumber<<" native="<<nativeCount()<<" time="<<current/double(frequency.QuadPart)<<"\n";diagnostic.flush();}next+=period;InvalidateRect(window,nullptr,FALSE);UpdateWindow(window);
  }
  if(audioDevice){waveOutReset(audioDevice);for(auto&h:audioHeaders)if(h.dwFlags&WHDR_PREPARED)waveOutUnprepareHeader(audioDevice,&h,sizeof(h));waveOutClose(audioDevice);}timeEndPeriod(1);
  unloadCore();deinitCore();FreeLibrary(core);if(gamepadLibrary)FreeLibrary(gamepadLibrary);return 0;
 }catch(const std::exception&e){if(headless){std::ofstream f(std::filesystem::u8path(baseDir+"\\selftest-error.txt"));f<<e.what();}else MessageBoxA(nullptr,e.what(),"Devil Crash MD",MB_OK|MB_ICONERROR);return 1;}
}
