/* Focused PET adapter for the unmodified Internet Archive SPACE INVADERS PRG.
 * Gameplay, graphics, scoring and waves execute as original 6502 instructions. */
(function(root){
  'use strict';
  const {Cpu6502}=typeof module!=='undefined'&&module.exports?require('./cpu6502.js'):root.PetCpu;
  const data=typeof module!=='undefined'&&module.exports?require('./data.js'):root.ArchiveData;
  const CLOCK=1000000, PERIOD=CLOCK/60;
  class Game {
    constructor(){this.reset();this.state='ready';this.runCycles(100000);}
    get memory(){return this.cpu.memory;}
    get screen(){return this.memory.subarray(0x8000,0x83e8);}
    get playerX(){return this.memory[0x3ca];}
    get lives(){return this.memory[0x3db];}
    get score(){const a=this.memory[0x33c],b=this.memory[0x33d];return (b>>4)*1000+(b&15)*100+(a>>4)*10+(a&15);}
    reset(){
      this.cpu=new Cpu6502();this.input={};this.state='ready';this.target=0;this.nextIrq=PERIOD;
      this.memory.set(data.program.subarray(2),data.program[0]|data.program[1]<<8);
      this.memory.fill(32,0x8000,0x8400);
      // PET ROM IRQ entry saves A/X/Y before dispatching through $0090.
      this.memory.set([0x48,0x8a,0x48,0x98,0x48,0x6c,0x90,0x00],0xff80);
      this.memory.set([0x68,0xa8,0x68,0xaa,0x68,0x40],0xe631);
      this.memory.set([0x4c,0x31,0xe6],0xe62e);
      this.memory[0xfffe]=0x80;this.memory[0xffff]=0xff;
      this.memory[0x90]=0x2e;this.memory[0x91]=0xe6;
      this.cpu.pc=1039;
      const originalRead=this.cpu.read.bind(this.cpu);
      this.cpu.read=address=>{
        if(address===0xe812)return 255&~(this.input.left?64:0)&~(this.input.right?128:0)&~(this.input.fire?1:0);
        if(address===0xe849)return (65535-this.cpu.cycles)&255;
        // VIA port B bit 5 carries vertical retrace. The game waits for both
        // edges between formation updates; a fixed value would freeze it.
        if(address===0xe840)return this.cpu.cycles%PERIOD<PERIOD/2?32:0;
        return originalRead(address);
      };
    }
    start(){
      this.reset();this.state='playing';
      // The ROM-free host calls the original parameter initializer, then the
      // original new-game entry. The PRG itself is never patched.
      this.memory.set([0x20,0x00,0x0e,0x4c,0x90,0x04],0xff40);
      this.cpu.pc=0xff40;this.runCycles(100000);
    }
    pause(){if(this.state==='playing')this.state='paused';}
    resume(){if(this.state==='paused')this.state='playing';}
    runCycles(cycles,input={}){
      this.input=input;this.target+=cycles;
      while(this.cpu.cycles<this.target){
        // GETIN: startup screen waits for a key; browser Begin is the host entry.
        if(this.cpu.pc===0xffe4){this.cpu.a=this.cpu.nz(0);this.cpu.pc=(this.cpu.popWord()+1)&65535;this.cpu.cycles+=6;continue;}
        // CHROUT is used for the startup clear-screen command.
        if(this.cpu.pc===0xffd2){if(this.cpu.a===147)this.screen.fill(32);this.cpu.pc=(this.cpu.popWord()+1)&65535;this.cpu.cycles+=6;continue;}
        // Original game-over display begins here, before its attract-mode return.
        if(this.state==='playing'&&this.cpu.pc===0x18f7){this.state='over';break;}
        if(this.cpu.cycles>=this.nextIrq&&!(this.cpu.p&4)){
          this.nextIrq+=PERIOD;this.memory[0x8f]=(this.memory[0x8f]+1)&255;this.cpu.irq();
        }
        this.cpu.step();
      }
    }
    update(seconds,input={}){if(this.state==='playing')this.runCycles(Math.min(seconds,0.1)*CLOCK,input);}
  }
  function rasterize(screen,target=new Uint8ClampedArray(320*200*4)){
    for(let cell=0;cell<1000;cell++)for(let y=0;y<8;y++){
      const code=screen[cell],bits=data.characters[(code&127)*8+y]^(code&128?255:0);
      for(let x=0;x<8;x++){const offset=((Math.floor(cell/40)*8+y)*320+(cell%40)*8+x)*4,lit=bits&(128>>x);target[offset]=lit?100:0;target[offset+1]=lit?255:0;target[offset+2]=lit?125:0;target[offset+3]=255;}
    }
    return target;
  }
  const api={Game,rasterize};if(typeof module!=='undefined'&&module.exports)module.exports=api;else root.ArchiveInvaders=api;
})(globalThis);
