// Contract-derived stand-in; no owner mock exists in the supplied workspace.
const http = require('http');
const key = 'sdk_cloud_state';
function send(res, code, data, error='') {
  res.writeHead(code, {'Content-Type':'application/json', 'Retry-After':'0'});
  res.end(JSON.stringify({status:{http_code:code,error_code:error,message:''},data}));
}
http.createServer(async (req,res) => {
  const body = req.body || {};
  const path = new URL(req.url,'http://localhost').pathname;
  let state = await pm.state.get(key) || {profiles:[],searches:0};
  if (path==='/__reset') { await pm.state.set(key,{profiles:[],searches:0});return send(res,200,null); }
  if (path==='/__stats') { res.writeHead(200,{'Content-Type':'application/json'});return res.end(JSON.stringify(state)); }
  if (req.method==='POST' && path==='/profile/create') {
    if (typeof body.name!=='string' || typeof body.folder_id!=='string') return send(res,400,null,'INVALID');
    const id='sim-profile-'+(state.profiles.length+1);
    state.profiles.push({id,name:body.name,browser_type:body.browser_type||'mimic'});
    await pm.state.set(key,state);return send(res,200,{ids:[id]});
  }
  if (req.method==='POST' && path==='/profile/search') {
    state.searches++;await pm.state.set(key,state);
    if (body.search_text==='rate-limit' && state.searches===1) return send(res,429,null,'LIMIT');
    return send(res,200,{profiles:state.profiles});
  }
  return send(res,501,null,'UNMODELED');
}).listen(process.env.PORT || 4500);
