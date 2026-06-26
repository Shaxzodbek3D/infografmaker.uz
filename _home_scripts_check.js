






/* 
 ACTION LABELS (Uzbek translations)
 */
const AL = {
 'LOGIN':'Tizimga Kirish','LOGOUT':'Tizimdan Chiqish',
 'VIEW':"Ma'lumotlarni Ko'rish",'READ':"O'qish",
 'CREATE':"Yangi Ma'lumot Qo'shish",'UPDATE':"O'zgartirish",
 'DELETE':"O'chirish",'EXPORT':"Eksport",'IMPORT':"Import",
 'EDIT':"Tahrirla",'ADD':"Qo'shish",'REMOVE':"O'chirish",
 'DOWNLOAD':"Yuklab Olish",'UPLOAD':"Yuklash",'SAVE':"Saqlash",
 'APPROVE':"Tasdiqlash",'REJECT':"Rad Etish",'VERIFY':"Tekshirish",
 'dashboard/auth':"Autentifikatsiya",'dashboard/index':"Bosh Sahifa",
 'dashboard/login':"Kirish",'dashboard/profile':"Profil",
 'dashboard/switch-role':"Rolni O'zgartirish",
 'student/student':"O'quvchi",'student/gpa':"O'rtacha Ball",
 'student/grade-view':"Baholarni Ko'rish",
 'student/attendance-view':"Davomat Ko'rish",
 'student/profile-view':"Profil Ko'rish",
 'student/profile-edit':"Profil O'zgartirish",
 'student/contract':"Shartnoma",'student/reference':"Spravka",
 'teacher/time-table':"Jadval",'teacher/attendance-journal':"Davomat Jurnali",
 'teacher/subject-topics':"Mavzular",
 'teacher/training-list':"O'quv Ro'yxati",
 'curriculum/schedule':"Jadval",'curriculum/curriculum':"O'quv Dasturi",
 'education/attendance':"Davomat",'education/subjects':"Fanlar",
 'education/time-table':"Jadval",
 'archive/diploma-view':"Diplom Ko'rish",
 'archive/transcript-view':"Transkript Ko'rish",
 'credit/grade-register':"Baho Ro'yxati",
 'credit/exam-schedule':"Imtihon Jadvali",
 'performance/gpa':"O'rtacha Ball",
 'system/classifier':"Klassifikator",
 'file-resource/index':"Fayllar",
 'message/my-messages':"Mening Xabarlarim",
};

function tA(a){
 if(!a) return '-';
 if(AL[a]) return AL[a];
 if(AL[a.toLowerCase()]) return AL[a.toLowerCase()];
 const p = a.includes('/') ? a.split('/').pop() : a;
 return p.replace(/[-_]/g,' ').replace(/\w/g,c=>c.toUpperCase());
}

/* 
 STATE
 */
let charts = {};
let selectedFiles = [];
let fileInputEl = null;
let dropZoneEl = null;

/* 
 INIT
 */
window.addEventListener('DOMContentLoaded', () =>{
 fileInputEl = document.getElementById('fileInput');
 dropZoneEl = document.getElementById('dropZone');

 // Drop zone handlers
 dropZoneEl.addEventListener('click', () =>fileInputEl.click());
 dropZoneEl.addEventListener('dragover', e =>{
 e.preventDefault();
 dropZoneEl.classList.add('drag-over');
 });
 dropZoneEl.addEventListener('dragleave', () =>dropZoneEl.classList.remove('drag-over'));
 dropZoneEl.addEventListener('drop', e =>{
 e.preventDefault();
 dropZoneEl.classList.remove('drag-over');
 fileInputEl.files = e.dataTransfer.files;
 handleFileSelect();
 });
 fileInputEl.addEventListener('change', handleFileSelect);

 document.getElementById('statusText').textContent = 'Tayyor';
});

/* 
 FILE SELECT
 */
function handleFileSelect(){
 selectedFiles = Array.from(fileInputEl.files);
 renderFileList();
}

function renderFileList(){
 const fl = document.getElementById('fileList');
 const st = document.getElementById('uploadStatus');
 if(!selectedFiles.length){ fl.style.display='none'; st.textContent=''; return; }
 fl.style.display = 'flex';
 fl.innerHTML = selectedFiles.map((f,i)=>`
<div class="file-item">
<div class="file-icon"></div>
<span class="file-name">${f.name}</span>
<span class="file-size">${(f.size/1024).toFixed(1)} KB</span>
<button class="file-remove" onclick="removeFile(${i})">x</button>
</div>`).join('');
 const total = selectedFiles.reduce((s,f)=>s+f.size,0);
 st.textContent = `OK ${selectedFiles.length} ta fayl - ${(total/1024/1024).toFixed(2)} MB`;
}

function removeFile(i){
 selectedFiles.splice(i,1);
 const dt = new DataTransfer();
 selectedFiles.forEach(f=>dt.items.add(f));
 fileInputEl.files = dt.files;
 renderFileList();
}

/* 
 PROGRESS
 */
function setProgress(pct, msg){
 const fill = document.getElementById('progressFill');
 const pctEl = document.getElementById('progressPct');
 const msgEl = document.getElementById('analysisMsgEl');
 if(fill) fill.style.width = Math.min(pct,99)+'%';
 if(pctEl) pctEl.textContent = Math.min(pct,99)+'%';
 if(msgEl && msg) msgEl.textContent = msg;
}

function showOverlay(){
 const o = document.getElementById('analysisOverlay');
 o.classList.add('active');
}
function hideOverlay(){
 const o = document.getElementById('analysisOverlay');
 o.classList.remove('active');
}

/* 
 MAIN: analyzeFiles
 */
async function analyzeFiles(){
 if(!selectedFiles.length){ alert('Iltimos fayl tanlang!'); return; }

 const btn = document.getElementById('analyzeBtn');
 btn.disabled = true;
 btn.textContent = '* Tahlil...';
 showOverlay();
 setProgress(0, 'Fayllar serverga yuklanmoqda...');

 let hardTO = setTimeout(()=>{
 hideOverlay();
 btn.disabled=false;
 btn.innerHTML=' Tahlil Boshlash';
 alert('Vaqt tugdi. Qayta urining.');
 }, 90000);

 let uploadData = null;

 try {
 // Upload
 const fd = new FormData();
 selectedFiles.forEach(f =>fd.append('files',f));
 setProgress(8,'Fayllar yuklanmoqda...');

 const upRes = await fetch('/api/upload-files',{method:'POST',body:fd,signal:AbortSignal.timeout(40000)});
 const upData = await upRes.json();
 if(!upRes.ok) throw new Error(upData.error || 'Yuklash xatosi');
 uploadData = upData;
 setProgress(15,`OK ${upData.files} ta fayl yuklandi`);

 // Show dashboard
 document.getElementById('uploadSection').style.display = 'none';
 document.getElementById('dashboard').style.display = 'block';
 showDashSections();

 // Load filter options
 loadFilterOptions();

 // Show nav buttons
 document.getElementById('nlpBtnNav').style.display = 'flex';
 document.getElementById('pdfBtnNav').style.display = 'flex';
 document.getElementById('nlpBtnDash').style.display = 'flex';

 // Parallel load all analytics
 setProgress(18,'Tahlillar boshlanmoqda...');

 const tasks = [
 { fn: loadStats, pct: 25, msg: 'OK Statistika' },
 { fn: loadAdminChart, pct: 30, msg: 'OK Admin chart' },
 { fn: loadActionChart, pct: 34, msg: 'OK Amal chart' },
 { fn: loadTimelineChart, pct: 38, msg: 'OK Timeline' },
 { fn: loadIpChart, pct: 42, msg: 'OK IP chart' },
 { fn: loadHourlyHeatmap, pct: 46, msg: 'OK Soatlik' },
 { fn: loadInfographics, pct: 50, msg: 'OK Infografika' },
 { fn: loadSankeyChart, pct: 55, msg: 'OK Sankey' },
 { fn: loadParallelChart, pct: 59, msg: 'OK Parallel' },
 { fn: loadAnomalies, pct: 64, msg: 'OK Anomaliyalar' },
 { fn: loadRiskScores, pct: 70, msg: 'OK Risk ballari' },
 { fn: loadAIInsights, pct: 77, msg: 'OK AI insights' },
 { fn: loadPredictions, pct: 83, msg: 'OK Prognozlar' },
 { fn: loadRecommendations,pct: 88, msg: 'OK Tavsiyalar' },
 { fn: loadUserRoles, pct: 92, msg: 'OK Rollar' },
 { fn: loadCategoryTreemap, pct: 91, msg: 'OK Kategoriya treemap' },
 { fn: loadWeeklyHeatmap, pct: 94, msg: 'OK Haftalik heatmap' },
 { fn: loadSuspSequences, pct: 97, msg: 'OK Ketma-ketlik' },
 { fn: loadUntranslated, pct: 99, msg: 'OK Tarjima tekshiruvi' },
 ];

 const wrapped = tasks.map(t =>Promise.race([
 t.fn().then(()=>setProgress(t.pct, t.msg)),
 new Promise((_,rej)=>setTimeout(()=>rej(new Error(t.msg+' timeout')),8000))
 ]).catch(e=>console.warn('Task warn:',e.message)));

 await Promise.allSettled(wrapped);

 setProgress(100,'OK Tahlil tugallandi!');
 document.getElementById('lastUpdate').textContent = new Date().toLocaleString('uz-UZ');
 document.getElementById('dashMeta').textContent =
 `${uploadData.files} ta fayl - ${uploadData.rows.toLocaleString()||''} ta log - ${new Date().toLocaleString('uz-UZ')}`;

 } catch(err){
 console.error(err);
 setProgress(100,'X Xato: '+err.message);
 alert('Xato: '+err.message);
 } finally {
 clearTimeout(hardTO);
 setTimeout(hideOverlay, 800);
 btn.disabled = false;
 btn.innerHTML = ' Tahlil Boshlash';
 selectedFiles = [];
 if(fileInputEl) fileInputEl.value='';
 document.getElementById('fileList').style.display = 'none';
 document.getElementById('uploadStatus').textContent = '';
 document.getElementById('statusText').textContent = uploadData ? 'Tahlil tugadi' : 'Xato';
 }
}

/* show all hidden sections */
function showDashSections(){
 ['filterSection','anomalySection','riskSection','insightsSection',
 'predictionsSection','recsSection','rolesSection',
 'categoryTreemapSection','weeklyHeatmapSection',
 'seqSection','untranslatedSection'].forEach(id=>{
 const el = document.getElementById(id);
 if(el) el.style.display = 'block';
 });
}

/* 
 STATS
 */
async function loadStats(){
 const r = await fetch('/api/stats');
 const d = await r.json();

 const items = [
 {icon:'', val:(d.total_logs || 0).toLocaleString(), lbl:'Jami Loglar', color:'var(--accent)'},
 {icon:'', val:d.unique_admins, lbl:'Adminlar', color:'var(--blue)'},
 {icon:'', val:d.unique_ips, lbl:'IP Manzilar', color:'var(--green)'},
 {icon:'™', val:d.unique_actions, lbl:'Amal Turlari',color:'var(--orange)'},
 ];

 document.getElementById('statsRow').innerHTML = items.map((it,i)=>`
<div class="stat-card fade-up" style="--card-accent:${it.color}">
<div class="stat-icon">${it.icon}</div>
<div class="stat-value">${it.val}</div>
<div class="stat-label">${it.lbl}</div>
</div>`).join('');
}

/* 
 CHART DEFAULTS
 */
Chart.defaults.color = '#52527a';
Chart.defaults.font.family = "'DM Sans',sans-serif";

const PALETTE = ['#7c6bff','#38bdf8','#10e8a0','#ff7c3b','#fbbf24','#ff4e6a','#a78bfa','#06d6d6','#f472b6','#34d399'];

/* 
 ADMIN CHART
 */
async function loadAdminChart(){
 const r = await fetch('/api/admin-activity');
 const d = await r.json();
 if(!d.labels.length) return;

 if(charts.admin) charts.admin.destroy();
 const ctx = document.getElementById('adminChart').getContext('2d');
 charts.admin = new Chart(ctx, {
 type:'bar',
 data:{
 labels: d.labels.slice(0,10).map(l => l.length > 18 ? l.slice(0,16) + '...' : l),
 datasets:[{
 label:'Loglar',
 data: d.data.slice(0,10),
 backgroundColor: PALETTE.slice(0,10).map(c=>c+'cc'),
 borderColor: PALETTE.slice(0,10),
 borderWidth:1.5,
 borderRadius:6,
 }]
 },
 options:{
 responsive:true,
 maintainAspectRatio:false,
 plugins:{legend:{display:false},tooltip:{callbacks:{label:ctx=>`${ctx.raw.toLocaleString()} ta log`}}},
 scales:{
 x:{grid:{color:'rgba(91,79,207,0.07)'},ticks:{font:{size:10}}},
 y:{grid:{color:'rgba(91,79,207,0.07)'},beginAtZero:true,ticks:{font:{size:10}}}
 }
 }
 });
}

/* 
 ACTION CHART (doughnut)
 */
async function loadActionChart(){
 const r = await fetch('/api/action-distribution');
 const d = await r.json();
 if(!d.labels.length) return;

 if(charts.action) charts.action.destroy();
 const ctx = document.getElementById('actionChart').getContext('2d');
 charts.action = new Chart(ctx,{
 type:'doughnut',
 data:{
 labels: d.labels.map(tA),
 datasets:[{data:d.data, backgroundColor:PALETTE, borderColor:'rgba(255,255,255,0.9)', borderWidth:2}]
 },
 options:{
 responsive:true,maintainAspectRatio:false,cutout:'65%',
 plugins:{
 legend:{position:'right',labels:{font:{size:10},boxWidth:10,padding:8}},
 tooltip:{callbacks:{label:ctx=>`${ctx.label}: ${ctx.raw.toLocaleString()}`}}
 }
 }
 });
}

/* 
 TIMELINE CHART
 */
async function loadTimelineChart(){
 const r = await fetch('/api/timeline');
 const d = await r.json();
 if(!d.labels.length) return;

 if(charts.timeline) charts.timeline.destroy();
 const ctx = document.getElementById('timelineChart').getContext('2d');

 const grad = ctx.createLinearGradient(0,0,0,140);
 grad.addColorStop(0,'rgba(124,107,255,0.35)');
 grad.addColorStop(1,'rgba(124,107,255,0)');

 charts.timeline = new Chart(ctx,{
 type:'line',
 data:{
 labels: d.labels,
 datasets:[{
 label:'Loglar',data:d.data,
 borderColor:'#7c6bff',backgroundColor:grad,
 borderWidth:2,fill:true,tension:0.45,
 pointRadius:0,pointHoverRadius:5,
 pointHoverBackgroundColor:'#a78bfa',
 }]
 },
 options:{
 responsive:true,maintainAspectRatio:false,
 plugins:{legend:{display:false}},
 scales:{
 x:{grid:{color:'rgba(91,79,207,0.07)'},ticks:{maxTicksLimit:10,font:{size:9}}},
 y:{grid:{color:'rgba(91,79,207,0.07)'},beginAtZero:true,ticks:{font:{size:9}}}
 }
 }
 });
}

/* 
 IP CHART
 */
async function loadIpChart(){
 const r = await fetch('/api/ip-analysis');
 const d = await r.json();
 if(!d.labels.length) return;

 if(charts.ip) charts.ip.destroy();
 const ctx = document.getElementById('ipChart').getContext('2d');
 charts.ip = new Chart(ctx,{
 type:'bar',
 data:{
 labels: d.labels.slice(0,12),
 datasets:[{
 label:'Kirish',data:d.data.slice(0,12),
 backgroundColor:'rgba(56,189,248,0.6)',
 borderColor:'#38bdf8',borderWidth:1.5,borderRadius:5,
 }]
 },
 options:{
 indexAxis:'y',responsive:true,maintainAspectRatio:false,
 plugins:{legend:{display:false}},
 scales:{
 x:{grid:{color:'rgba(91,79,207,0.07)'},beginAtZero:true,ticks:{font:{size:9}}},
 y:{grid:{display:false},ticks:{font:{size:9}}}
 }
 }
 });
}

/* 
 HOURLY HEATMAP
 */
async function loadHourlyHeatmap(){
 try {
 const r = await fetch('/api/timeline');
 const d = await r.json();

 // Build hourly from timeline data or use zeros
 const hourly = new Array(24).fill(0);

 // Try to get hourly from admin timeline endpoint
 try{
 const hr = await fetch('/api/stats');
 // just use placeholder if no hourly endpoint
 }catch(e){}

 const container = document.getElementById('hourlyHeatmap');
 if(!container) return;

 const maxVal = Math.max(...hourly,1);
 const cells = hourly.map((v,h)=>{
 const intensity = v/maxVal;
 const bg = `rgba(124,107,255,${0.08 + intensity*0.75})`;
 return `<div class="heatmap-cell" style="background:${bg}" title="${h}:00 - ${v} log"></div>`;
 }).join('');

 const labels = Array.from({length:12},(_,i)=>`<span>${i*2}</span>`).join('');

 container.innerHTML = `
<div class="heatmap-grid">${cells}</div>
<div class="heatmap-label">${labels}</div>`;
 } catch(e){ console.warn('Heatmap:',e.message) }
}

/* 
 INFOGRAPHICS (gauge + error pie)
 */
async function loadInfographics(){
 try {
 const hr = await fetch('/api/system-health');
 const h = await hr.json();
 const stab = typeof h.stability_index === 'number' ? h.stability_index : 0;

 document.getElementById('stabilityValue').textContent = stab.toFixed(0);

 if(charts.gauge) charts.gauge.destroy();
 const gc = document.getElementById('stabilityGauge').getContext('2d');
 charts.gauge = new Chart(gc,{
 type:'doughnut',
 data:{
 labels:['Barqaror','Xavf'],
 datasets:[{
 data:[stab,Math.max(0,100-stab)],
 backgroundColor:[stab > 60 ? '#059669' : stab > 30 ? '#d97706' : '#dc2626','rgba(91,79,207,0.08)'],
 borderWidth:0,
 }]
 },
 options:{
 responsive:true,cutout:'72%',rotation:-90,circumference:180,
 plugins:{legend:{display:false},tooltip:{enabled:false}}
 }
 });

 // Error rate chart
 const eR = h.error_rate ? h.error_rate * 100 : 0;
 if(charts.errRate) charts.errRate.destroy();
 const ec = document.getElementById('errorRateChart').getContext('2d');
 charts.errRate = new Chart(ec,{
 type:'doughnut',
 data:{
 labels:['Normal','Xatolik'],
 datasets:[{
 data:[Math.max(0,100-eR), Math.min(100,eR)],
 backgroundColor:['rgba(16,232,160,0.7)','rgba(255,78,106,0.7)'],
 borderColor:['#10e8a0','#ff4e6a'],
 borderWidth:2,
 }]
 },
 options:{
 responsive:true,cutout:'60%',
 plugins:{
 legend:{position:'bottom',labels:{font:{size:10},boxWidth:10,padding:8}},
 tooltip:{callbacks:{label:c=>`${c.label}: ${c.raw.toFixed(1)}%`}}
 }
 }
 });

 // Weekly radar from timeline
 const tr = await fetch('/api/timeline');
 const td = await tr.json();
 const wk = [0,0,0,0,0,0,0];
 if(td.labels&&td.data){
 td.labels.forEach((l,i)=>{
 const day = (new Date(l).getDay()+6)%7;
 wk[day] += Number(td.data[i])||0;
 });
 }
 if(charts.radar) charts.radar.destroy();
 const rc = document.getElementById('weeklyRadar').getContext('2d');
 charts.radar = new Chart(rc,{
 type:'radar',
 data:{
 labels:['Du','Se','Ch','Pa','Ju','Sh','Ya'],
 datasets:[{
 label:'Faollik',data:wk,
 backgroundColor:'rgba(124,107,255,0.15)',
 borderColor:'#7c6bff',pointBackgroundColor:'#a78bfa',
 borderWidth:2,pointRadius:3,
 }]
 },
 options:{
 responsive:true,maintainAspectRatio:false,
 plugins:{legend:{display:false}},
 scales:{r:{
 angleLines:{color:'rgba(91,79,207,0.1)'},
 grid:{color:'rgba(91,79,207,0.1)'},
 pointLabels:{color:'#8888bb',font:{size:10}},
 ticks:{display:false}
 }}
 }
 });
 } catch(e){ console.warn('Infographics:',e.message) }
}

/* 
 SANKEY
 */
async function loadSankeyChart(){
 try {
 const r = await fetch('/api/sankey-flow');
 const d = await r.json();
 const cont = document.getElementById('sankeyChart');
 if(!d.nodes.length){ cont.innerHTML='<div class="empty-state"><span class="es-icon"></span>Ma\'lumot topilmadi</div>'; return; }
 cont.innerHTML='';
 const mg={top:10,right:10,bottom:10,left:10};
 const W=cont.offsetWidth-mg.left-mg.right||600;
 const H=420-mg.top-mg.bottom;
 const svg=d3.select('#sankeyChart').append('svg')
 .attr('width',W+mg.left+mg.right).attr('height',H+mg.top+mg.bottom)
 .append('g').attr('transform',`translate(${mg.left},${mg.top})`);
 const sk=d3.sankey().nodeWidth(14).nodePadding(8).extent([[1,1],[W-1,H-5]]);
 const {nodes,links}=sk({
 nodes:d.nodes.map(n=>({...n})),
 links:d.links.map(l=>({...l}))
 });
 const col=d3.scaleOrdinal().domain(['admin','action','endpoint']).range(['#7c6bff','#10e8a0','#fbbf24']);
 svg.append('g').selectAll('path').data(links).enter().append('path')
 .attr('class','sankey-link')
 .attr('d',d3.sankeyLinkHorizontal())
 .attr('stroke',l=>col(l.source.type))
 .attr('stroke-width',l=>Math.max(1,l.width))
 .append('title').text(l=>`${l.source.name} ->${l.target.name}
${l.value} marta`);
 const nd=svg.append('g').selectAll('g').data(nodes).enter().append('g').attr('class','sankey-node');
 nd.append('rect').attr('x',n=>n.x0).attr('y',n=>n.y0)
 .attr('height',n=>n.y1-n.y0).attr('width',n=>n.x1-n.x0)
 .attr('fill',n=>col(n.type)).attr('rx',3)
 .append('title').text(n=>`${n.name}
${n.value} amal`);
 nd.append('text')
 .attr('x', n => n.x0 < W / 2 ? n.x1 + 6 : n.x0 - 6)
 .attr('y',n=>(n.y1+n.y0)/2).attr('dy','0.35em')
 .attr('text-anchor', n => n.x0 < W / 2 ? 'start' : 'end')
 .attr('font-size',11).attr('fill','#8888bb')
 .text(n => n.name.length > 18 ? n.name.slice(0,16) + '...' : n.name);
 } catch(e){ console.warn('Sankey:',e.message) }
}

/* 
 PARALLEL COORDINATES
 */
async function loadParallelChart(){
 try{
 const r=await fetch('/api/parallel-dimensions');
 const d=await r.json();
 const cont=document.getElementById('parallelChart');
 if(!d.data.length){ cont.innerHTML='<div class="empty-state"><span class="es-icon"></span>Ma\'lumot topilmadi</div>'; return; }
 cont.innerHTML='';
 const mg={top:30,right:10,bottom:10,left:10};
 const W=cont.offsetWidth-mg.left-mg.right||580;
 const H=420-mg.top-mg.bottom;
 const svg=d3.select('#parallelChart').append('svg')
 .attr('width',W+mg.left+mg.right).attr('height',H+mg.top+mg.bottom)
 .append('g').attr('transform',`translate(${mg.left},${mg.top})`);
 const numDims=d.dimensions.filter(dd=>dd.type==='numeric');
 const dims=numDims.map(dd=>dd.key);
 const y={};
 numDims.forEach(dd=>{
 const vals=d.data.map(row=>row[dd.key]);
 y[dd.key]=d3.scaleLinear().domain(d3.extent(vals)).range([H,0]);
 });
 const x=d3.scalePoint().domain(dims).range([0,W]).padding(0.5);
 const cScale=d3.scaleSequential().domain([0,d3.max(d.data,row=>row.risk_score)||100])
 .interpolator(d3.interpolateRgbBasis(['#10e8a0','#fbbf24','#ff4e6a']));
 const line = d3.line().defined(pt => !isNaN(pt[1])).x(pt => x(pt[0])).y(pt => pt[1]);

 svg.append('g').selectAll('path').data(d.data).enter().append('path')
 .attr('class','parallel-line')
 .attr('d',row=>line(dims.map(dd=>[dd,y[dd](row[dd])])))
 .style('stroke',row=>cScale(row.risk_score))
 .on('mouseover',function(){d3.select(this).style('stroke-width','3').style('opacity',1)})
 .on('mouseout',function(){d3.select(this).style('stroke-width','1.5').style('opacity',0.5)})
 .append('title').text(row=>`${row.admin}
Risk: ${row.risk_score}`);

 const axes=svg.selectAll('.parallel-axis').data(dims).enter().append('g')
 .attr('class','parallel-axis').attr('transform',dd=>`translate(${x(dd)},0)`);
 axes.each(function(dd){d3.select(this).call(d3.axisLeft(y[dd]).ticks(4))});
 axes.append('text').style('text-anchor','middle').attr('y',-12)
 .attr('fill','#8888bb').attr('font-size',10).attr('font-weight',600)
 .text(dd=>{const o=d.dimensions.find(dim=>dim.key===dd); return o ? o.label : dd;});
 }catch(e){console.warn('Parallel:',e.message)}
}

/* 
 FILTERS
 */
async function loadFilterOptions(){
 try{
 const r=await fetch('/api/filter-options');
 const o=await r.json();
 const sel=document.getElementById('filterActionType');
 if(!sel) return;
 sel.innerHTML='<option value="">- Amal turini tanlang -</option>';
 const list = (o.actions_translated && o.actions_translated.length) ? o.actions_translated : (o.actions || []).map(a => ({original:a, translated:tA(a)}));
 list.forEach(it=>{
 const op=document.createElement('option');
 op.value=it.original; op.textContent=it.translated;
 sel.appendChild(op);
 });
 }catch(e){console.warn('FilterOpts:',e.message)}
}

function switchFilterTab(tab){
 ['admin','action'].forEach(t=>{
 document.getElementById('tab'+t.charAt(0).toUpperCase()+t.slice(1)).classList.toggle('active',t===tab);
 document.getElementById('body'+t.charAt(0).toUpperCase()+t.slice(1)).classList.toggle('active',t===tab);
 });
 document.getElementById('filterResults').innerHTML='';
}

async function applyAdminFilter(){
 const v=document.getElementById('filterAdminText').value.trim();
 if(!v){alert('Admin nomini kiriting!');return;}
 await runFilter({admin_text:v,ip:null,action:null});
}

async function applyActionFilter(){
 const v=document.getElementById('filterActionType').value;
 if(!v){alert('Amal turini tanlang!');return;}
 await runFilter({admin_text:null,ip:null,action:v});
}

function resetFilters(){
 document.getElementById('filterAdminText').value='';
 document.getElementById('filterActionType').value='';
 document.getElementById('filterResults').innerHTML='';
}

async function runFilter(filters){
 const res=document.getElementById('filterResults');
 res.innerHTML='<div class="empty-state" style="padding:20px"><div class="nlp-spin-wheel" style="width:28px;height:28px;margin:0 auto 8px"></div>Yuklanmoqda...</div>';
 try{
 const r=await fetch('/api/filter',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(filters)});
 const d=await r.json();
 renderFilterResults(d);
 }catch(e){res.innerHTML=`<p style="color:var(--red);padding:12px">Xato: ${e.message}</p>`}
}

function renderFilterResults(d){
 const res=document.getElementById('filterResults');
 const s=d.summary||{};
 const topActs = s.top_actions ? Object.entries(s.top_actions).map(([a,c]) => `${tA(a)} (${c})`).join(' - ') : '-';

 let html=`
<div class="result-stats">
<div class="result-stat-item"><strong>${d.total_filtered||0}</strong>Natija</div>
<div class="result-stat-item"><strong>${s.admin_count||0}</strong>Admin</div>
<div class="result-stat-item"><strong>${s.action_count||0}</strong>Amal turi</div>
<div class="result-stat-item"><strong>${s.ip_count||0}</strong>IP</div>
</div>
<div style="font-size:0.79rem;color:var(--text3);margin-bottom:8px">Eng ko'p: ${topActs}</div>`;

 if(d.data.length){
 html+=`<div class="result-table-wrap"><table class="result-table">
<thead><tr><th>Admin</th><th>Amal</th><th>IP</th><th>Vaqt</th></tr></thead><tbody>`;
 d.data.slice(0,80).forEach(row=>{
 const t = row['Yaratilgan'] ? new Date(row['Yaratilgan']).toLocaleString('uz-UZ') : '-';
 const ip=row['IP']||'-';
 const action=tA(row['Amal'])||row['Amal']||'-';
 html+=`<tr>
<td style="font-weight:600">${row['Admin nomi']||'-'}</td>
<td><span class="badge badge-accent" style="font-size:0.7rem">${action}</span></td>
<td><code style="font-size:0.78rem;color:var(--text2)">${ip}</code></td>
<td style="color:var(--text3);font-size:0.79rem">${t}</td>
</tr>`;
 });
 html+='</tbody></table></div>';
 } else {
 html+='<div class="empty-state"><span class="es-icon"></span>Hech narsa topilmadi</div>';
 }
 document.getElementById('filterResults').innerHTML=html;
}

/* 
 ANOMALIES
 */
async function loadAnomalies(){
 try{
 const r=await fetch('/api/anomalies');
 const d=await r.json();

 document.getElementById('adminsCount').textContent=d.admins.length||0;
 document.getElementById('ipsCount').textContent=d.ips.length||0;

 // Admins panel
 const ap=document.getElementById('anomalyAdminsPanel');
 if(d.admins.length){
 ap.innerHTML=`<div class="anomaly-grid">${d.admins.map(it=>`
<div class="anomaly-card">
<div class="anomaly-admin">
<span style="color:var(--orange)"></span>
<strong>${it.admin}</strong>
<span class="badge badge-orange">${it.ip_count} IP</span>
</div>
<div class="ip-chips">${it.ips.map(ip=>`<span class="ip-chip">${ip}</span>`).join('')}</div>
</div>`).join('')}</div>`;
 } else {
 ap.innerHTML='<div class="empty-state" style="padding:16px"><span class="es-icon">OK</span>Topilmadi</div>';
 }

 // IPs panel
 const ipp=document.getElementById('anomalyIpsPanel');
 if(d.ips.length){
 ipp.innerHTML=`<div class="anomaly-grid">${d.ips.map(it=>`
<div class="anomaly-card" style="border-left-color:var(--blue)">
<div class="anomaly-admin">
<span style="color:var(--blue)"></span>
<code style="font-weight:700;color:var(--text)">${it.ip}</code>
<span class="badge badge-blue">${it.admin_count} admin</span>
</div>
<div class="ip-chips">${it.admins.map(a=>`<span class="ip-chip" style="background:rgba(56,189,248,0.08);border-color:rgba(56,189,248,0.2);color:var(--blue)">${a.length > 20 ? a.slice(0,18) + '...' : a}</span>`).join('')}</div>
</div>`).join('')}</div>`;
 } else {
 ipp.innerHTML='<div class="empty-state" style="padding:16px"><span class="es-icon">OK</span>Topilmadi</div>';
 }
 }catch(e){console.warn('Anomalies:',e.message)}
}

function toggleAnomalyPanel(type){
 const p=document.getElementById('anomalyAdminsPanel');
 const q=document.getElementById('anomalyIpsPanel');
 const bt=document.getElementById('toggleAdminsBtn');
 const bq=document.getElementById('toggleIpsBtn');
 if(type==='admins'){
 const show=!p.classList.contains('on');
 p.classList.toggle('on',show); bt.classList.toggle('on',show);
 q.classList.remove('on'); bq.classList.remove('on');
 } else {
 const show=!q.classList.contains('on');
 q.classList.toggle('on',show); bq.classList.toggle('on',show);
 p.classList.remove('on'); bt.classList.remove('on');
 }
}

/* 
 RISK SCORES
 */
async function loadRiskScores(){
 try{
 const r=await fetch('/api/risk-scores');
 const d=await r.json();
 const grid=document.getElementById('riskGrid');
 if(!d.scores.length){grid.innerHTML='<div class="empty-state"><span class="es-icon"></span>Ma\'lumot topilmadi</div>';return;}

 grid.innerHTML=d.scores.slice(0,15).map(s=>{
 const lvl = s.risk_score > 60 ? 'high' : s.risk_score > 30 ? 'medium' : 'low';
 const col = lvl === 'high' ? 'var(--red)' : lvl === 'medium' ? 'var(--orange)' : 'var(--green)';
 const lbl = lvl === 'high' ? 'YUQORI' : lvl === 'medium' ? "O'RTA" : 'OK PAST';
 const badgeCls = lvl === 'high' ? 'badge-red' : lvl === 'medium' ? 'badge-orange' : 'badge-green';
 return `<div class="risk-card fade-up">
<div class="risk-card-top">
<div class="risk-admin-name"><span>${s.admin}</span></div>
<span class="badge ${badgeCls}">${lbl}</span>
</div>
<div class="risk-score-row">
<div class="risk-score-big" style="color:${col}">${s.risk_score}</div>
<div class="risk-bar-wrap">
<div class="risk-bar-label">Xavf Bali / 100</div>
<div class="risk-bar"><div class="risk-fill" style="width:${s.risk_score}%;background:${col}"></div></div>
</div>
</div>
<div class="risk-stats-mini">
<div class="risk-mini-item"><div class="risk-mini-val">${s.total_actions}</div><div class="risk-mini-lbl">Amallar</div></div>
<div class="risk-mini-item"><div class="risk-mini-val">${s.unique_ips}</div><div class="risk-mini-lbl">IP</div></div>
<div class="risk-mini-item"><div class="risk-mini-val">${s.failed_attempts}</div><div class="risk-mini-lbl">Xatolar</div></div>
</div>
<div class="risk-evidence-list">
<div class="risk-ev-item">Noto'g'ri:<strong>${s.failed_attempts} ->${s.failed_points || 0} ball</strong></div>
<div class="risk-ev-item">Ko'p IP:<strong>${s.unique_ips} ->${s.ip_points || 0} ball</strong></div>
<div class="risk-ev-item">Tungi:<strong>${s.odd_hours_count || 0} ->${s.odd_hours_points || 0} ball</strong></div>
<div class="risk-ev-item">Ustun amal:<strong>${tA(s.max_action||'-')}</strong></div>
</div>
</div>`;
 }).join('');
 }catch(e){console.warn('Risk:',e.message)}
}

/* 
 AI INSIGHTS
 */
async function loadAIInsights(){
 try{
 const r=await fetch('/api/ai/insights');
 const d=await r.json();
 const grid=document.getElementById('insightsGrid');
 if(!d.insights.length){grid.innerHTML='<div class="empty-state"><span class="es-icon"></span>Topilmadi</div>';return;}

 grid.innerHTML=d.insights.slice(0,8).map(ins=>{
 const sev=(ins.severity||'info').toLowerCase();
 const sevCls = sev === 'high' ? 'severity-high' : sev === 'warning' ? 'severity-warning' : 'severity-info';
 const type=(ins.type||'INSIGHT').replace(/_/g,' ').toUpperCase();
 const ev=ins.data||{};
 const sevBadge = sev === 'high' ? 'badge-red' : sev === 'warning' ? 'badge-yellow' : 'badge-blue';

 const evItems=[];
 const mfTr = ev.most_frequent_action_translated || (ev.most_frequent_action ? tA(ev.most_frequent_action) : undefined);
 if(ev.total_actions!==undefined) evItems.push(`<div class="insight-ev-item"><strong>Jami amallar</strong>${ev.total_actions}</div>`);
 if(ev.unique_ips!==undefined) evItems.push(`<div class="insight-ev-item"><strong>IP manzillar</strong>${ev.unique_ips}</div>`);
 if(ev.most_frequent_hour!==undefined) evItems.push(`<div class="insight-ev-item"><strong>Eng faol soat</strong>${ev.most_frequent_hour}:00</div>`);
 if(mfTr!==undefined) evItems.push(`<div class="insight-ev-item"><strong>Eng ko'p amal</strong>${mfTr}</div>`);
 if(ev.percentage!==undefined) evItems.push(`<div class="insight-ev-item"><strong>Ulush</strong>${ev.percentage}%</div>`);
 if(ev.peak_hour!==undefined) evItems.push(`<div class="insight-ev-item"><strong>Peak soat</strong>${ev.peak_hour}:00</div>`);

 return `<div class="insight-card ${sevCls} fade-up">
<div class="insight-meta-row">
<span class="badge badge-accent" style="font-size:0.65rem">${type}</span>
<span class="badge ${sevBadge}" style="font-size:0.65rem">${sev.toUpperCase()}</span>
</div>
<div class="insight-title-text">${ins.title||'-'}</div>
<div class="insight-desc-text">${ins.description||'-'}</div>
 ${evItems.length ? `<div class="insight-evidence"><div style="font-size:0.72rem;font-weight:700;color:var(--text3);text-transform:uppercase;letter-spacing:0.05em;margin-bottom:6px">Dalillar</div><div class="insight-ev-grid">${evItems.join('')}</div></div>` : ''}
<div class="insight-rec"><strong>Tavsiya:</strong>${ins.recommendation||'-'}</div>
</div>`;
 }).join('');
 }catch(e){console.warn('Insights:',e.message)}
}

/* 
 PREDICTIONS
 */
async function loadPredictions(){
 try{
 const r=await fetch('/api/ai/predictions');
 const d=await r.json();
 const grid=document.getElementById('predGrid');
 if(!d.predictions.length){grid.innerHTML='<div class="empty-state"><span class="es-icon">OK</span>Xavf signali topilmadi</div>';return;}

 grid.innerHTML=d.predictions.map(p=>`
<div class="pred-card fade-up">
<div class="pred-risk">${(p.risk||'').replace(/_/g,' ').toUpperCase()}</div>
<div class="pred-msg">${p.message||'-'}</div>
<div class="pred-action"><strong>Harakat:</strong>${p.suggested_action||'-'}</div>
<div style="margin-top:8px"><span class="badge ${p.confidence === 'high' ? 'badge-red' : 'badge-orange'}">${p.confidence||'medium'}</span></div>
</div>`).join('');
 }catch(e){console.warn('Predictions:',e.message)}
}

/* 
 RECOMMENDATIONS
 */
async function loadRecommendations(){
 try{
 const r=await fetch('/api/ai/recommendations');
 const d=await r.json();
 const grid=document.getElementById('recsGrid');
 if(!d.recommendations.length){grid.innerHTML='<div class="empty-state"><span class="es-icon"></span>Tavsiya topilmadi</div>';return;}

 grid.innerHTML=d.recommendations.map(rec=>{
 const pri=(rec.priority||'medium').toLowerCase();
 const priLbl = pri === 'high' ? 'YUQORI' : pri === 'medium' ? "O'RTA" : 'PAST';
 const steps = (rec.steps && rec.steps.length) ? `<div class="rec-steps"><ol>${rec.steps.map(s=>`<li>${s}</li>`).join('')}</ol></div>` : '';
 const ev = rec.evidence ? `<div class="rec-ev"><strong>Dalil:</strong>${rec.evidence.metric||''} ${rec.evidence.value||''}</div>` : '';
 const vf = rec.verification ? `<div class="rec-verify"><strong>Tekshiruv:</strong>${rec.verification}</div>` : '';
 return `<div class="rec-card ${pri} fade-up">
<div class="rec-chip-row">
<span class="badge badge-accent" style="font-size:0.65rem">${rec.category||'General'}</span>
<span class="badge ${pri === 'high' ? 'badge-red' : pri === 'medium' ? 'badge-orange' : 'badge-green'}" style="font-size:0.65rem">${priLbl}</span>
<span class="badge badge-yellow" style="font-size:0.65rem">${rec.urgency||'-'}</span>
</div>
<div class="rec-title-text">${rec.title||rec.action||'-'}</div>
<div class="rec-reason-text"><strong>Sabab:</strong>${rec.reason||'-'}</div>
 ${ev}${steps}${vf}
</div>`;
 }).join('');
 }catch(e){console.warn('Recs:',e.message)}
}

/* 
 USER ROLES
 */
async function loadUserRoles(){
 try{
 const r=await fetch('/api/behavior/user-roles');
 const d=await r.json();
 const grid=document.getElementById('rolesGrid');
 const entries=Object.entries(d).slice(0,12);
 if(!entries.length){grid.innerHTML='<div class="empty-state"><span class="es-icon"></span>Topilmadi</div>';return;}

 grid.innerHTML=entries.map(([admin,info])=>{
 const acts=Object.entries(info.primary_actions||{}).sort((a,b)=>b[1]-a[1]).slice(0,4).map(([a,c])=>`${tA(a)} (${c})`).join(', ');
 return `<div class="role-card fade-up">
<div class="role-badge-inline">${info.inferred_role||'Umumiy'}</div>
<div class="role-name">${admin}</div>
<div class="role-desc">${info.description||'Taxminiy rol'}</div>
<div class="role-actions-list"><strong>Asosiy ishlar:</strong>${acts||'-'}</div>
</div>`;
 }).join('');
 }catch(e){console.warn('Roles:',e.message)}
}

/* 
 SUSPICIOUS SEQUENCES
 */
async function loadSuspSequences(){
 try{
 const r=await fetch('/api/suspicious-sequences');
 const d=await r.json();
 const sum=d.summary||{};
 const rc=sum.risk_counts||{};

 document.getElementById('seqSummary').innerHTML=`
<div class="seq-stat"><strong>${d.total||0}</strong><span>Jami</span></div>
<div class="seq-stat"><strong>${rc.high||0}</strong><span>Yuqori xavf</span></div>
<div class="seq-stat"><strong>${rc.medium||0}</strong><span>O'rta xavf</span></div>
<div class="seq-stat"><strong>${sum.unique_admins||0}</strong><span>Admin</span></div>`;

 const grid=document.getElementById('seqGrid');
 if(!d.suspicious_sequences.length){
 grid.innerHTML='<div class="empty-state"><span class="es-icon">OK</span>Hozircha topilmadi</div>'; return;
 }
 const trPat=p=>{
 if(!p) return '-';
 return p.includes('->') ? p.split('->').map(x => tA(x.trim())).join(' ->')
 : p.split(' ').map(t => tA(t) || t).join(' ');
 };
 grid.innerHTML=d.suspicious_sequences.map(s=>`
<div class="seq-card fade-up">
<div class="seq-pattern">${trPat(s.pattern)}</div>
<div class="seq-info"><strong>Admin:</strong>${s.admin}</div>
<div class="seq-info"><strong>Xavf:</strong><span style="color:var(--red);font-weight:700">${(s.risk||'').toUpperCase()}</span></div>
<div class="seq-info" style="margin-top:4px">${s.description||''}</div>
</div>`).join('');
 }catch(e){console.warn('Sequences:',e.message)}
}

/* 
 AMAL KATEGORIYALARI TREEMAP
 */
const TREEMAP_COLORS = [
 '#3b82f6','#10b981','#f59e0b','#ef4444','#8b5cf6',
 '#06b6d4','#ec4899','#84cc16','#f97316','#6366f1',
 '#14b8a6','#e11d48','#0ea5e9','#a855f7','#22c55e',
];

const CAT_INFO = {
 student: { icon:'', desc:'HEMIS tizimida talabalar bilan bevosita bog\'liq barcha amallar: ro\'yxatdan o\'tkazish, ma\'lumotlarni tahrirlash, buyruqlar, hujjatlar, diplom, davomat va to\'lov.' },
 teacher: { icon:'', desc:'O\'qituvchilar faoliyati: elektron jurnal yuritish, baho qo\'yish, sillabus va dars materiallarini yuklash, vazifalar berish va imtihon natijalari kiritish.' },
 curriculum: { icon:'', desc:'O\'quv dasturi va jadvallar: semestr rejalari, fan biriktirishlari, haftalik dars jadvali, imtihon jadvali yaratish va tahrirlash.' },
 education: { icon:'', desc:'Ta\'lim jarayoni resurslari: talaba va o\'qituvchi uchun fanlar, vazifalar, davomat, o\'zlashtirish ko\'rsatkichlari va dars jadvali.' },
 archive: { icon:'', desc:'Arxiv amallari: diplom blanki, akademik spravka, bitiruvchilar hujjatlari, akkreditatsiya ma\'lumotlari va chaqiruv varaqlari.' },
 decree: { icon:'', desc:'Buyruqlar va farmoyishlar: talabalar bo\'yicha buyruqlar, ta\'lim buyruqlari, qabul qilish, chiqarish va ko\'chirish farmoyishlari.' },
 document: { icon:'', desc:'Elektron hujjatlar boshqaruvi: imzolash, ko\'rish, yuborish, tasdiqlash va rad etish amallari.' },
 employee: { icon:'', desc:'Xodimlar boshqaruvi: shartnomalar, ta\'tillar, maosh, attestatsiya, murabbiy vazifasi va xodim ma\'lumotlarini tahrirlash.' },
 performance: { icon:'', desc:'Samaradorlik ko\'rsatkichlari: GPA va PTT reytinglari, KPI hisoblash, to\'ldirish va tekshirish amallari.' },
 report: { icon:'', desc:'Hisobotlar moduli: talabalar, davomat, baholar, moliya, xodimlar va statistik hisobotlarni ko\'rish va eksport qilish.' },
 system: { icon:'™', desc:'Tizim boshqaruvi: foydalanuvchi rollari, ruxsatlar, konfiguratsiya, OAuth, audit jurnali va sinxronizatsiya holati.' },
 finance: { icon:'', desc:'Moliyaviy amallar: to\'lov shartnomalar, stipendiya, qarzdorlik, hisob-faktura va stipendiya protokollari.' },
 science: { icon:'', desc:'Ilmiy faoliyat: ilmiy loyihalar, nashrlar, konferensiyalar, patentlar va grantlar boshqaruvi.' },
 message: { icon:'OK‰', desc:'Xabarlar va bildirishnomalar: xabar yuborish, kiruvchi/chiquvchi xabarlar, e\'lonlar yaratish va ko\'rish.' },
 admission: { icon:'', desc:'Qabul jarayoni: abituriyentlar reytingi, kvota boshqaruvi, qabul ro\'yxatlari va hisobotlar.' },
 transfer: { icon:'', desc:'Ko\'chirish amallari: talabani guruhga, kursga ko\'chirish, bitiruvchi qilish, akademik ta\'tilga chiqarish.' },
 dashboard: { icon:'', desc:'Tizimga kirish va chiqish amallari: autentifikatsiya, profil ko\'rish, rolni almashtirish, parol tiklash.' },
 'file-resource':{ icon:'', desc:'O\'quv materiallari: dars fayllari, taqdimotlar va qo\'shimcha resurslarni yuklash, ko\'rish va tahrirlash.' },
 attendance: { icon:'OK', desc:'Davomat moduli: talabalar dars davomati va faolligini qayd etish amallari.' },
 credit: { icon:'', desc:'Kredit tizimi: fanlarga o\'qituvchi biriktirish va kredit soatlarini boshqarish.' },
 indexer: { icon:'', desc:'Tizim indekslash: ma\'lumotlarni qayta indekslash, indeks holati va tozalash amallari.' },
 files: { icon:'', desc:'Fayl ulanish boshqaruvi: tizim fayllari va ulanish amallari.' },
};

// Yagona floating tooltip elementi
let _tmTip = null;
function _initTip(){
 if(_tmTip) return;
 _tmTip = document.createElement('div');
 _tmTip.style.cssText=`position:fixed;z-index:9999;max-width:280px;padding:12px 14px;
 background:#1e293b;color:#f1f5f9;border-radius:10px;font-size:12.5px;line-height:1.5;
 box-shadow:0 8px 24px rgba(0,0,0,.35);pointer-events:none;display:none;
 transition:opacity .15s`;
 document.body.appendChild(_tmTip);
}
function _showTip(e, cat, color){
 _initTip();
 const info = CAT_INFO[cat.key] || {desc:'Tafsilot mavjud emas'};
 _tmTip.innerHTML=`
<div style="font-weight:700;font-size:13px;color:${color};margin-bottom:5px">
 ${info.icon} ${cat.label}
</div>
<div style="color:#cbd5e1;margin-bottom:7px">${info.desc}</div>
<div style="display:flex;gap:10px;border-top:1px solid #334155;padding-top:7px;margin-top:2px">
<span><b>${cat.count.toLocaleString()}</b>ta amal</span>
<span><b>${cat.percent}%</b></span>
</div>`;
 _tmTip.style.display='block';
 _moveTip(e);
}
function _moveTip(e){
 if(!_tmTip) return;
 const x=e.clientX+14, y=e.clientY-10;
 const w=_tmTip.offsetWidth, h=_tmTip.offsetHeight;
 _tmTip.style.left=(x+w>window.innerWidth x-w-28 : x)+'px';
 _tmTip.style.top =(y+h>window.innerHeight y-h-4 : y)+'px';
}
function _hideTip(){ if(_tmTip) _tmTip.style.display='none'; }

async function loadCategoryTreemap(){
 try{
 const r = await fetch('/api/charts/action-categories');
 const d = await r.json();
 if(!d.categories.length) return;
 document.getElementById('treemapTotal').textContent =
 `Jami: ${d.total.toLocaleString()} ta amal`;
 const container = document.getElementById('categoryTreemap');
 const max = d.categories[0].count;
 container.innerHTML = d.categories.map((cat, i) =>{
 const color = TREEMAP_COLORS[i % TREEMAP_COLORS.length];
 const info = CAT_INFO[cat.key] || { icon:'' };
 return `<div data-catidx="${i}" style="
 background:${color}18;border:2px solid ${color}55;border-radius:12px;
 padding:12px 16px;flex:${cat.count} 1 auto;min-width:90px;max-width:260px;
 cursor:default;transition:transform .15s,box-shadow .15s;position:relative;overflow:hidden">
<div style="font-size:1.4rem;margin-bottom:4px">${info.icon}</div>
<div style="font-weight:700;font-size:0.88rem;color:${color}">${cat.label}</div>
<div style="font-size:1.05rem;font-weight:800;color:var(--text);margin:2px 0">
 ${cat.count.toLocaleString()}
</div>
<div style="font-size:0.72rem;color:var(--text-muted)">${cat.percent}%</div>
<div style="position:absolute;bottom:0;left:0;height:3px;
 width:${cat.percent}%;background:${color};border-radius:0 2px 2px 0"></div>
</div>`;
 }).join('');

 // Hover hodisalari
 container.querySelectorAll('[data-catidx]').forEach(el=>{
 const idx = +el.dataset.catidx;
 const cat = d.categories[idx];
 const color = TREEMAP_COLORS[idx % TREEMAP_COLORS.length];
 el.addEventListener('mouseenter', e=>{
 el.style.transform='scale(1.04)';
 el.style.boxShadow=`0 6px 20px ${color}44`;
 _showTip(e, cat, color);
 });
 el.addEventListener('mousemove', _moveTip);
 el.addEventListener('mouseleave', ()=>{
 el.style.transform='';
 el.style.boxShadow='';
 _hideTip();
 });
 });
 }catch(e){console.warn('Treemap:',e.message)}
}

/* 
 HAFTALIK FAOLLIK HEATMAP
 */
async function loadWeeklyHeatmap(){
 try{
 const r = await fetch('/api/charts/weekly-heatmap');
 const d = await r.json();
 if(!d.matrix.length) return;
 const days=['Dush','Sesh','Chor','Pay','Jum','Shan','Yak'];
 const maxV = d.max||1;
 let html=`<div style="display:grid;grid-template-columns:44px repeat(24,1fr);gap:2px;min-width:600px">`;
 /* soat sarlavhalari */
 html+=`<div></div>`;
 for(let h=0;h<24;h++)
 html+=`<div style="text-align:center;font-size:9px;color:var(--text-muted);padding-bottom:2px">${h}</div>`;
 /* qatorlar */
 d.matrix.forEach((row,di)=>{
 html+=`<div style="font-size:10px;font-weight:600;color:var(--text-muted);
 display:flex;align-items:center;padding-right:4px">${days[di]}</div>`;
 row.forEach(val=>{
 const pct=val/maxV;
 const r=Math.round(59 + pct*(239-59));
 const g=Math.round(130 + pct*(68-130));
 const b=Math.round(246 + pct*(68-246));
 const bg=val===0'#f8fafc':`rgb(${r},${g},${b})`;
 const fg=pct>0.5'#fff':'#374151';
 html+=`<div title="${val} ta amal" style="
 height:26px;background:${bg};border-radius:3px;
 display:flex;align-items:center;justify-content:center;
 font-size:8px;font-weight:600;color:${fg};cursor:default">
 ${val>0val:''}
</div>`;
 });
 });
 html+=`</div>`;
 /* Rang jadval izohis */
 html+=`<div style="display:flex;align-items:center;gap:6px;margin-top:10px;font-size:11px;color:var(--text-muted)">
<span>Kam</span>
<div style="display:flex;gap:2px">
 ${[0.1,0.3,0.5,0.7,0.9,1].map(p=>{
 const rv=Math.round(59+p*(239-59)),gv=Math.round(130+p*(68-130)),bv=Math.round(246+p*(68-246));
 return `<div style="width:20px;height:12px;background:rgb(${rv},${gv},${bv});border-radius:2px"></div>`;
 }).join('')}
</div>
<span>Ko'p</span>
</div>`;
 document.getElementById('weeklyHeatmapGrid').innerHTML=html;
 }catch(e){console.warn('WeeklyHeatmap:',e.message)}
}

/* 
 TARJIMA QILINMAGAN AMALLAR
 */
async function loadUntranslated(){
 try{
 const r=await fetch('/api/untranslated-actions');
 const d=await r.json();
 const section=document.getElementById('untranslatedSection');
 const list=document.getElementById('untranslatedList');
 const cnt=document.getElementById('untranslatedCount');
 if(!d.total){
 section.style.display='none';
 return;
 }
 cnt.textContent=`${d.total} ta amal tarjima qilinmagan`;
 list.innerHTML=d.untranslated.map(a=>
 `<span style="background:rgba(245,158,11,0.12);border:1px solid rgba(245,158,11,0.35);
 border-radius:6px;padding:4px 10px;font-size:0.8rem;color:#f59e0b;font-family:monospace">
 ${a.action}<span style="opacity:0.6">(${a.count})</span>
</span>`
 ).join('');
 }catch(e){console.warn('Untranslated:',e.message)}
}

/* 
 DATA MOVEMENT
 */
async function loadDataMovement(){
 try{
 const r=await fetch('/api/behavior/data-movement');
 const d=await r.json();
 const list=document.getElementById('movementList');
 if(!d.patterns.length){list.innerHTML='<div class="empty-state"><span class="es-icon"></span>IMPORT/EXPORT amallari topilmadi</div>';return;}

 list.innerHTML=d.patterns.map(p=>{
 const rl=p.risk_assessment.risk_level||'low';
 const cls=rl==='high''move-high':rl==='medium''move-medium':'move-low';
 return `<div class="movement-item fade-up">
<div class="movement-name">${p.admin}</div>
<div class="movement-stats-grid">
<div class="move-stat-box"><strong>${p.imports}</strong><span>Import</span></div>
<div class="move-stat-box"><strong>${p.exports}</strong><span>Export</span></div>
<div class="move-stat-box"><strong>${p.downloads}</strong><span>Yuklab</span></div>
<div class="move-stat-box"><strong>${p.uploads}</strong><span>Yuklash</span></div>
</div>
<div class="movement-risk ${cls}">
<strong>Risk:</strong>${rl.toUpperCase()} (${p.risk_assessment.risk_score||0}/100)
 ${p.risk_assessment.factors.length' - '+p.risk_assessment.factors.join(', '):''}
</div>
</div>`;
 }).join('');
 }catch(e){console.warn('Movement:',e.message)}
}

/* 
 PDF EXPORT
 */
async function exportPDF(){
 try{
 const r=await fetch('/api/export-pdf');
 const b=await r.blob();
 const a=document.createElement('a');
 a.href=URL.createObjectURL(b);
 a.download=`HEMIS_${new Date().toISOString().slice(0,10)}.pdf`;
 a.click(); URL.revokeObjectURL(a.href);
 }catch(e){alert('PDF xato: '+e.message)}
}

/* 
 NLP PANEL
 */
function openNLP(){
 document.getElementById('nlpPanel').style.display='block';
 document.body.style.overflow='hidden';
 document.getElementById('nlpSpinner').style.display='block';
 document.getElementById('nlpContent').style.display='none';
 loadNLPData();
}
function closeNLP(){
 document.getElementById('nlpPanel').style.display='none';
 document.body.style.overflow='';
}

async function loadNLPData(){
 try{
 const r=await fetch('/api/nlp/report');
 const body=await r.json();
 document.getElementById('nlpSpinner').style.display='none';
 const cont=document.getElementById('nlpContent');
 cont.style.display='block';

 if(!body.success){
 cont.innerHTML=`<div class="empty-state"><span class="es-icon">X</span>Xato: ${body.error||'Noma\'lum xato'}</div>`;
 return;
 }

 const d=body.data||{};
 const s=d.summary||{};

 const SC={critical:'#ff4e6a',error:'#ff7c3b',warning:'#fbbf24',info:'#10e8a0',debug:'#a78bfa'};
 const KWCOLS=['#7c6bff','#38bdf8','#10e8a0','#ff7c3b','#fbbf24','#ff4e6a','#a78bfa','#06d6d6','#f472b6','#34d399'];

 const errDist=d.error_analysis.distribution||{};
 const errTotal=Object.values(errDist).reduce((a,b)=>a+b,0)||1;

 cont.innerHTML=`
<!-- SUMMARY GRID -->
<div class="nlp-summary-grid">
 ${[
 [(s.total_logs||0).toLocaleString(),'Jami Loglar'],
 [s.unique_admins||0,'Adminlar'],
 [s.unique_actions||0,'Amal Turlari'],
 [s.unique_templates||0,'Shablonlar'],
 [(s.error_rate_pct||0)+'%','Xato Ulushi'],
 [s.dominant_category||'-','Dominant Kategoriya'],
 ].map(([v,l])=>`<div class="nlp-stat"><div class="nlp-stat-val">${v}</div><div class="nlp-stat-lbl">${l}</div></div>`).join('')}
</div>

<!-- KEYWORDS + ACTION GROUPS -->
<div class="nlp-two-col">
<div class="nlp-card">
<div class="nlp-card-title">Kalit So'zlar</div>
<div class="kw-cloud">
 ${(d.keywords||[]).slice(0,24).map((k,i)=>{
 const c=KWCOLS[i%KWCOLS.length];
 const sz=12+Math.round(((k.frequency||1)/((d.keywords[0].frequency)||1))*14);
 return `<span class="kw-tag" style="background:${c}18;color:${c};border:1px solid ${c}30;font-size:${sz}px">${k.keyword}</span>`;
 }).join('')}
</div>
</div>
<div class="nlp-card">
<div class="nlp-card-title">Amal Guruhlari</div>
 ${Object.entries(d.action_groups||{}).sort((a,b)=>b[1].count-a[1].count).map(([cat,st])=>`
<div class="ag-row">
<span class="ag-name">${cat}</span>
<div class="ag-bar-bg"><div class="ag-bar-fill" style="width:${st.percentage||0}%"></div></div>
<span class="ag-pct">${st.percentage||0}%</span>
</div>`).join('')}
</div>
</div>

<!-- ERROR DIST + TEMPLATES -->
<div class="nlp-two-col">
<div class="nlp-card">
<div class="nlp-card-title">Xatoliklar Darajasi</div>
 ${Object.entries(errDist).map(([lv,cnt])=>{
 const pct=(cnt/errTotal*100).toFixed(1);
 const c=SC[lv]||'#888';
 return `<div class="err-row">
<span class="err-badge" style="background:${c}18;color:${c};border:1px solid ${c}30">${lv.toUpperCase()}</span>
<div class="err-bar-bg"><div class="err-bar-fill" style="width:${pct}%;background:${c}"></div></div>
<span class="err-count" style="color:${c}">${cnt}</span>
</div>`;
 }).join('')}
</div>
<div class="nlp-card">
<div class="nlp-card-title">Log Shablonlari</div>
 ${(d.templates||[]).slice(0,8).map(t=>`
<div class="tpl-item">
<span class="tpl-count">${t.count}x</span>
<span class="tpl-text">${t.template}</span>
</div>`).join('')}
</div>
</div>

<!-- BIGRAMS -->
<div class="nlp-card">
<div class="nlp-card-title">Eng Ko'p Juft So'zlar (Bigrams)</div>
<div class="bigram-cloud">
 ${(d.bigrams||[]).slice(0,18).map(g=>`
<span class="bigram-tag">${g.ngram}<span>(${g.count})</span></span>`).join('')}
</div>
</div>`;
 }catch(e){
 document.getElementById('nlpSpinner').style.display='none';
 document.getElementById('nlpContent').style.display='block';
 document.getElementById('nlpContent').innerHTML=`<div class="empty-state"><span class="es-icon">X</span>NLP ma'lumot yuklanmadi: ${e.message}</div>`;
 }
}
