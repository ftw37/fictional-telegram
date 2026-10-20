const {test}=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const {createHash}=require('node:crypto');
const {Game,rasterize}=require('../game.js');
const data=require('../data.js');
const sha=(bytes,algorithm='sha256')=>createHash(algorithm).update(bytes).digest('hex');
const original=name=>fs.readFileSync(path.join(__dirname,'../original',name));
const tick=(game,n,input={})=>{for(let i=0;i<n;i++)game.update(.1,input);};
const fresh=()=>{const g=new Game();g.start();tick(g,20);return g;};

test('disk matches Internet Archive SHA-1; extracted PRG matches browser bytes',()=>{
 const disk=original('PET_Games_Disk_04_19xx_-.d64');
 assert.equal(sha(disk,'sha1'),'a4c10db6937a609e15f30d448b08f2130663250a');
 const sector=(track,number)=>{
   let offset=number;for(let t=1;t<track;t++)offset+=t<=17?21:t<=24?19:t<=30?18:17;
   return disk.subarray(offset*256,offset*256+256);
 };
 let t=18,s=1,entry;
 while(t){const block=sector(t,s);for(let i=0;i<8;i++){
   const row=block.subarray(i*32,i*32+32);
   if(row[2]&&row.subarray(5,21).toString('latin1').replace(/\xa0+$/,'')==='SPACE INVADERS')entry=row;
 }[t,s]=block;}
 assert.ok(entry);[t,s]=entry.subarray(3,5);const parts=[],seen=new Set();
 while(t){const key=t+':'+s;assert.ok(!seen.has(key));seen.add(key);const block=sector(t,s);parts.push(block.subarray(2,block[0]?256:block[1]+1));[t,s]=block;}
 const prg=Buffer.concat(parts);
 assert.equal(prg.length,7169);assert.equal(sha(prg),'b3a350bc7b74b017f70961588c661529390d04efdd588e268bc89b2cc445b8ef');
 assert.deepEqual(prg,original('space-invaders.prg'));assert.deepEqual(Buffer.from(data.program),prg);
});
test('startup copies the original archive opening screen into PET screen memory',()=>{
 const g=new Game();assert.equal(g.state,'ready');assert.equal(g.cpu.pc,0x43e);
 assert.deepEqual(g.screen, data.program.subarray(0x1c00-0x401+2,0x1c00-0x401+2+1000));
});
test('new game draws original formations, initializes three lives, and advances with retrace',()=>{
 const g=fresh();assert.equal(g.lives,3);assert.equal(g.score,0);
 const screen=sha(g.screen);tick(g,20);assert.notEqual(sha(g.screen),screen);
 assert.equal(g.state,'playing');assert.ok(g.screen.some(b=>b!==32));
});
test('keyboard matrix moves in both directions and clamps at the original edges',()=>{
 const g=fresh(),x=g.playerX;tick(g,5,{right:true});assert.ok(g.playerX>x);
 tick(g,5,{left:true});assert.equal(g.playerX,x);
 tick(g,25,{left:true});assert.equal(g.playerX,4);
 tick(g,25,{right:true});assert.equal(g.playerX,63);
});
test('Space drives the original fire bit and creates an original-code projectile',()=>{
 const g=fresh();assert.equal(g.memory[0xd7],1);tick(g,1,{fire:true});
 assert.equal(g.memory[0x3c9]&1,0);assert.equal(g.memory[0x3d1],1);assert.ok(g.memory[0xd7]>=128);
 tick(g,1);assert.equal(g.memory[0x3c9]&1,1);
});
test('pause freezes CPU and screen; restart restores a deterministic new game',()=>{
 const g=fresh();g.pause();const cycles=g.cpu.cycles,screen=sha(g.screen);
 tick(g,10,{right:true,fire:true});assert.equal(g.cpu.cycles,cycles);assert.equal(sha(g.screen),screen);
 g.resume();tick(g,3);assert.ok(g.cpu.cycles>cycles);
 g.start();const other=new Game();other.start();assert.equal(sha(g.memory),sha(other.memory));
});
test('full unattended game reaches original game-over screen and can restart',()=>{
 const g=fresh();let n=0;while(g.state==='playing'&&n++<1800)g.update(.1);
 assert.equal(g.state,'over');assert.equal(g.lives,0);assert.equal(g.cpu.pc,0x18f7);
 g.start();assert.equal(g.state,'playing');assert.equal(g.lives,3);
});
test('PET character raster preserves ROM bytes, inverse characters, and opaque pixels',()=>{
 assert.deepEqual(Buffer.from(data.characters),original('pet-characters.bin'));
 const screen=new Uint8Array(1000).fill(32);screen[0]=1;screen[1]=129;const p=rasterize(screen);
 for(let y=0;y<8;y++)for(let x=0;x<8;x++){const a=(y*320+x)*4,b=(y*320+x+8)*4;assert.equal(p[a+1]+p[b+1],255);assert.equal(p[a+3],255);}
});
