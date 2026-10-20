#pragma once
#include <cstdint>
#include "libretro.h"
// XInput values are fixed by Microsoft's controller ABI.
inline uint16_t xboxMask(uint16_t buttons,int16_t x,int16_t y,uint8_t leftTrigger,uint8_t rightTrigger){
 uint16_t mask=0;
 auto add=[&](bool pressed,unsigned id){if(pressed)mask|=uint16_t(1u<<id);};
 add((buttons&(0x4000|0x0100))!=0||leftTrigger>30,RETRO_DEVICE_ID_JOYPAD_Y); // X/LB/LT -> Genesis A
 add((buttons&0x1000)!=0,RETRO_DEVICE_ID_JOYPAD_B); // A -> Genesis B
 add((buttons&(0x2000|0x0200))!=0||rightTrigger>30,RETRO_DEVICE_ID_JOYPAD_A); // B/RB/RT -> Genesis C
 add((buttons&0x0010)!=0,RETRO_DEVICE_ID_JOYPAD_START);
 constexpr int deadzone=7849;
 add((buttons&0x0001)!=0||y>deadzone,RETRO_DEVICE_ID_JOYPAD_UP);
 add((buttons&0x0002)!=0||y<-deadzone,RETRO_DEVICE_ID_JOYPAD_DOWN);
 add((buttons&0x0004)!=0||x<-deadzone,RETRO_DEVICE_ID_JOYPAD_LEFT);
 add((buttons&0x0008)!=0||x>deadzone,RETRO_DEVICE_ID_JOYPAD_RIGHT);
 return mask;
}
