const http=require('node:http'),fs=require('node:fs'),path=require('node:path');
const types={'.html':'text/html; charset=utf-8','.js':'text/javascript; charset=utf-8','.css':'text/css; charset=utf-8','.md':'text/plain; charset=utf-8'};
http.createServer((req,res)=>{
 let name;try{name=decodeURIComponent(new URL(req.url,'http://localhost').pathname);}catch{res.writeHead(400);res.end();return;}
 const file=path.resolve(__dirname,'.'+(name==='/'?'/index.html':name));
 if(!file.startsWith(__dirname+path.sep)){res.writeHead(403);res.end();return;}
 fs.readFile(file,(error,bytes)=>{if(error){res.writeHead(404);res.end('Not found');return;}res.writeHead(200,{'Content-Type':types[path.extname(file)]||'application/octet-stream','Cache-Control':'no-store'});res.end(bytes);});
}).listen(8082,'127.0.0.1',()=>console.log('Space Invaders: http://127.0.0.1:8082/'));
