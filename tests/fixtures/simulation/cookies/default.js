const http=require('http');
http.createServer((req,res)=>{
  res.writeHead(req.url==='/__reset'?200:501,{'Content-Type':'application/json'});
  res.end(JSON.stringify({status:{http_code:req.url==='/__reset'?200:501,error_code:'',message:''},data:null}));
}).listen(process.env.PORT||4500);
