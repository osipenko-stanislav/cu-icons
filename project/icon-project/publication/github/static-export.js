// Static hosting adapter. Animation data and runtime are shared with localhost.
(()=>{
 const nativeFetch=window.fetch.bind(window),encoder=new TextEncoder();let assets;
 const json=(value)=>new Response(JSON.stringify(value),{headers:{'Content-Type':'application/json'}});
 const inline=(value)=>JSON.stringify(value).replaceAll('<','\\u003c').replaceAll('>','\\u003e').replaceAll('&','\\u0026');
 const load=()=>assets??=Promise.all(['scenes.json','player.js','export-template.html','licenses/useAnimations-MIT.txt','licenses/lottie-web-MIT.md'].map(async(name)=>{const r=await nativeFetch(new URL(name,document.baseURI));if(!r.ok)throw Error('Missing '+name);return name.endsWith('.json')?r.json():r.text()}));
 const crcTable=Uint32Array.from({length:256},(_,n)=>{for(let i=0;i<8;i++)n=n&1?0xedb88320^(n>>>1):n>>>1;return n>>>0});
 function crc32(bytes){let n=0xffffffff;for(const b of bytes)n=crcTable[(n^b)&255]^(n>>>8);return (n^0xffffffff)>>>0}
 async function zip(files){
  const chunks=[],directory=[];let offset=0;
  for(const [name,text] of files){
   const filename=encoder.encode(name),bytes=encoder.encode(text),crc=crc32(bytes);let payload=bytes,method=0;
   if(bytes.length>4096&&typeof CompressionStream!=='undefined'){try{const zlib=new Uint8Array(await new Response(new Blob([bytes]).stream().pipeThrough(new CompressionStream('deflate'))).arrayBuffer());if(zlib.length-6<bytes.length){payload=zlib.subarray(2,zlib.length-4);method=8}}catch{}}
   const local=new Uint8Array(30+filename.length),v=new DataView(local.buffer);
   v.setUint32(0,0x04034b50,true);v.setUint16(4,20,true);v.setUint16(6,0x800,true);v.setUint16(8,method,true);v.setUint16(12,33,true);v.setUint32(14,crc,true);v.setUint32(18,payload.length,true);v.setUint32(22,bytes.length,true);v.setUint16(26,filename.length,true);local.set(filename,30);chunks.push(local,payload);
   const entry=new Uint8Array(46+filename.length),e=new DataView(entry.buffer);e.setUint32(0,0x02014b50,true);e.setUint16(4,20,true);e.setUint16(6,20,true);e.setUint16(8,0x800,true);e.setUint16(10,method,true);e.setUint16(14,33,true);e.setUint32(16,crc,true);e.setUint32(20,payload.length,true);e.setUint32(24,bytes.length,true);e.setUint16(28,filename.length,true);e.setUint32(42,offset,true);entry.set(filename,46);directory.push(entry);offset+=local.length+payload.length;
  }
  const end=new Uint8Array(22),v=new DataView(end.buffer),length=directory.reduce((n,b)=>n+b.length,0);v.setUint32(0,0x06054b50,true);v.setUint16(8,files.length,true);v.setUint16(10,files.length,true);v.setUint32(12,length,true);v.setUint32(16,offset,true);return new Blob([...chunks,...directory,end],{type:'application/zip'});
 }
 async function makeExport(settings){
  const [config,player,template,useLicense,lottieLicense]=await load(),{preset,speed,strokeWidth=1,icon,prefix='',suffix='',overrides={}}=settings;
  if(!Object.hasOwn(config.presets,preset)||![.75,1,1.25,1.5].includes(speed)||strokeWidth<.5||strokeWidth>3||![prefix,suffix].every(x=>/^[A-Za-z0-9_-]{0,24}$/.test(x)))throw Error('Invalid export settings');
  const modes=['reference','hover','click-replay','hover-click'],scenes=config.scenes.filter(s=>icon==='pack'||s.id===icon).map(s=>({...s,trigger:modes.includes(overrides[s.id])?overrides[s.id]:s.trigger}));if(!scenes.length)throw Error('Unknown icon');
  const names=Object.fromEntries(scenes.map(s=>[s.id,prefix+s.id+suffix])),motion={version:1,defaultPreset:preset,playbackSpeed:speed,presets:config.presets,scenes:scenes.map(({id,label,trigger,duration,tracks})=>({id,label,trigger,duration,tracks})),assetNames:names,strokeWidth};
  const playback={...config.presets[preset],duration:config.presets[preset].duration/speed};
  const preview=template.replace('@@PLAYER@@',player).replace('@@PRESET@@',inline(playback)).replace('@@SCENES@@',inline(scenes)).replace('</style>',`:root{--icon-stroke:${strokeWidth}px}</style>`);
  const files=[['motion.json',JSON.stringify(motion)+'\n'],['preview.html',preview],['player.js',player]];
  for(const scene of scenes){files.push(['svg/'+names[scene.id]+'.svg',scene.source],['geometry/'+names[scene.id]+'.svg',scene.svg])}
  files.push(['licenses/useAnimations-MIT.txt',useLicense],['licenses/lottie-web-MIT.md',lottieLicense]);return zip(files);
 }
 window.CUStaticExport=makeExport;
 window.fetch=async(input,options={})=>{
  const url=new URL(input instanceof Request?input.url:input,document.baseURI);
  if(url.origin===location.origin&&url.pathname==='/api/export'){
   try{return new Response(await makeExport(JSON.parse(options.body)),{headers:{'Content-Type':'application/zip'}})}catch(e){return new Response(String(e),{status:400})}
  }
  if(url.origin===location.origin&&url.pathname==='/api/triggers'){
   const key='cu-iconizer-triggers:reference-series-v1';let values={};try{values=JSON.parse(localStorage.getItem(key)||'{}')}catch{}
   if(options.method==='POST'){values={...values,...JSON.parse(options.body)};try{localStorage.setItem(key,JSON.stringify(values))}catch{}}
   return json(values);
  }
  return nativeFetch(input,options);
 };
})();
