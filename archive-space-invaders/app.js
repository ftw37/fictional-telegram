(function(){
 'use strict';
 const {Game,rasterize}=window.ArchiveInvaders,$=id=>document.getElementById(id);
 const canvas=$('game'),context=canvas.getContext('2d'),frame=context.createImageData(320,200);
 let game=new Game(),last=null,audio=null,oscillator=null,gain=null,sound=false;const keys=new Set(),touch=new Set();
 context.imageSmoothingEnabled=false;
 function clear(){keys.clear();touch.clear();for(const id of ['left','right','fire'])$(id).classList.remove('held');}
 function draw(){rasterize(game.screen,frame.data);context.putImageData(frame,0,0);}
 function sync(){
   $('pause').disabled=!['playing','paused'].includes(game.state);
   $('pause').textContent=game.state==='paused'?'RESUME [P]':'PAUSE [P]';
   $('start').textContent=game.state==='ready'?'BEGIN GAME [B]':'RESTART [B]';
   $('status').textContent=game.state==='ready'?'ORIGINAL INSTRUCTIONS':game.state==='paused'?'PAUSED':game.state==='over'?'GAME OVER — PRESS B':'ORIGINAL ARCHIVE PROGRAM RUNNING';
 }
 function begin(){clear();game.start();last=null;canvas.focus();sync();draw();}
 function pause(){clear();if(game.state==='playing')game.pause();else game.resume();last=null;sync();draw();}
 $('sound').addEventListener('click',()=>{
   sound=!sound;$('sound').textContent=sound?'SOUND ON':'SOUND OFF';$('sound').setAttribute('aria-pressed',String(sound));
   const Audio=window.AudioContext||window.webkitAudioContext;
   if(sound&&Audio&&!audio){audio=new Audio();oscillator=audio.createOscillator();gain=audio.createGain();oscillator.type='square';gain.gain.value=0;oscillator.connect(gain);gain.connect(audio.destination);oscillator.start();}
   if(audio&&sound)audio.resume().catch(()=>{});
 });
 function syncAudio(){
   if(!audio)return;
   // Approximation of the PET's external CB2 amplifier from VIA timer values.
   const timer=game.memory[0xe848],active=sound&&game.state==='playing'&&timer>0&&timer<255;
   gain.gain.setTargetAtTime(active?.018:0,audio.currentTime,.008);
   oscillator.frequency.setTargetAtTime(1000000/(16*(timer+2)),audio.currentTime,.008);
 }
 $('start').addEventListener('click',begin);$('pause').addEventListener('click',pause);
 $('instructions').addEventListener('click',()=>{clear();game=new Game();last=null;sync();draw();});
 const relevant=new Set(['ArrowLeft','ArrowRight',' ','b','B','p','P','Escape',',','.']);
 addEventListener('keydown',event=>{
   if(!relevant.has(event.key)||event.ctrlKey||event.metaKey||event.altKey)return;
   // Preserve native keyboard operation of focused buttons.
   if(event.key===' '&&event.target instanceof HTMLButtonElement)return;
   event.preventDefault();keys.add(event.key);
   if(event.repeat)return;
   if(event.key.toLowerCase()==='b')begin();
   if(event.key.toLowerCase()==='p'||event.key==='Escape')pause();
 });
 addEventListener('keyup',event=>{keys.delete(event.key);});
 for(const id of ['left','right','fire']){
   const button=$(id);
   button.addEventListener('pointerdown',event=>{event.preventDefault();button.setPointerCapture(event.pointerId);touch.add(id);button.classList.add('held');});
   for(const type of ['pointerup','pointercancel','lostpointercapture'])button.addEventListener(type,()=>{touch.delete(id);button.classList.remove('held');});
 }
 function background(){clear();game.pause();last=null;sync();}
 addEventListener('blur',background);document.addEventListener('visibilitychange',()=>{if(document.hidden)background();});
 function tick(time){
   const dt=last===null?0:Math.min((time-last)/1000,.1);last=time;
   try{if(dt)game.update(dt,{left:keys.has('ArrowLeft')||keys.has(',')||touch.has('left'),right:keys.has('ArrowRight')||keys.has('.')||touch.has('right'),fire:keys.has(' ')||touch.has('fire')});}
   catch(error){game.pause();$('announcement').textContent='Game stopped: '+error.message;console.error(error);}
   draw();sync();syncAudio();requestAnimationFrame(tick);
 }
 sync();draw();requestAnimationFrame(tick);
})();
