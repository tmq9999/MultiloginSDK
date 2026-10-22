const http = require('http');
const key = 'sdk_launcher_state';
function send(res,code,data,error='') {
  res.writeHead(code,{'Content-Type':'application/json'});
  res.end(JSON.stringify({status:{http_code:code,error_code:error,message:''},data}));
}
http.createServer(async (req,res) => {
  const path=new URL(req.url,'http://localhost').pathname;
  let state=await pm.state.get(key)||{starts:0,stops:0,profiles:{}};
  if (path==='/__reset') {await pm.state.set(key,{starts:0,stops:0,profiles:{}});return send(res,200,null);}
  if (path==='/__stats') {res.writeHead(200,{'Content-Type':'application/json'});return res.end(JSON.stringify(state));}
  let match=path.match(/^\/api\/v2\/profile\/f\/([^/]+)\/p\/([^/]+)\/start$/);
  if (req.method==='GET' && match) {
    const id=decodeURIComponent(match[2]);state.starts++;await pm.state.set(key,state);
    if (id==='start-503') return send(res,503,null,'UNAVAILABLE');
    state.profiles[id]='browser_running';await pm.state.set(key,state);
    return send(res,200,{id,port:'55513',browser_type:'mimic',core_version:132,is_quick:false});
  }
  match=path.match(/^\/api\/v1\/profile\/stop\/p\/([^/]+)$/);
  if (req.method==='GET' && match) {
    const id=decodeURIComponent(match[1]);state.stops++;state.profiles[id]='stopped';await pm.state.set(key,state);return send(res,200,null);
  }
  match=path.match(/^\/api\/v1\/profile\/status\/p\/([^/]+)$/);
  if (req.method==='GET' && match) {
    const id=decodeURIComponent(match[1]);
    if (id==='status-hang') await new Promise(r=>setTimeout(r,200));
    if (!state.profiles[id]) return send(res,404,null,'NOT_FOUND');
    return send(res,200,{profile_id:id,status:state.profiles[id]});
  }
  return send(res,501,null,'UNMODELED');
}).listen(process.env.PORT || 4500);
